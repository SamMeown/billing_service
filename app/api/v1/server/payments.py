import stripe
from fastapi import APIRouter, Body, Depends, Response, status
from sqlalchemy.orm import Session

from msg.events_reporter import EventsReporter, get_events_reporter
from db.database import get_db
from db.db_models import (ModelMovies, ModelSubscriptions, ModelUserMovies,
                          ModelUsers, ModelUserSubscription)

router = APIRouter()


def calculate_order_amount(item, db: Session = Depends(get_db)):
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client

    if item['type'] == 'subscription':
        # subscription cost
        response = db.query(ModelSubscriptions).filter(ModelSubscriptions.id == item['id']).first()
        if response is not None:
            return response.price * 100  # in cents
    else:
        # movie cost
        response = db.query(ModelMovies).filter(ModelMovies.id == item['id']).first()
        if response is not None:
            return response.price * 100  # in cents
    return 0


@router.post('/users/{user_id}/payments')
def pay(user_id: str,
        response: Response,
        data: dict = Body(...),
        db: Session = Depends(get_db),
        events_reporter: EventsReporter = Depends(get_events_reporter)):
    user_id = '6a8b52b0-c402-4aee-9693-128b1581e092'

    # data['item']['type'] = 'subscription'
    # data['action'] = 'repeat'

    # data['item']['type'] = 'movie'
    # data['item']['id'] = "0ccb507f-4211-4d17-8182-2f09b61a23e9"

    user = db.query(ModelUsers).filter(ModelUsers.id == user_id).first()

    if user is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return dict(error='user_not_found')

    try:

        if data['action'] == 'create':
            # create corresponding stripe customer if user doesn't have one yet

            if user.stripe_cus_id is None:
                stripe_customer = stripe.Customer.create()

                user.id = user_id
                user.stripe_cus_id = stripe_customer['id']

                db.add(user)
                db.commit()

            order_amount = calculate_order_amount(data['item'], db)
            payment_intent_data = dict(
                amount=order_amount,
                currency=data['currency'],
                payment_method=data['paymentMethodId'],
                confirmation_method='manual',
                customer=user.stripe_cus_id,
                confirm=True
            )

            if data['item']['type'] == 'subscription':
                # Need to save card for off-session usage
                # setup_future_usage saves the card and tells Stripe how you plan to use it later
                # 'off_session' means we are going to charge the saved card when the customer is not present
                payment_intent_data['setup_future_usage'] = 'off_session'

            # Create a new PaymentIntent for the order
            # If it fails, exception will be raised

            intent = stripe.PaymentIntent.create(**payment_intent_data)

        elif data['action'] == 'confirm':
            # Confirm the PaymentIntent to collect the money
            intent = stripe.PaymentIntent.confirm(data['paymentId'])

        else:  # 'repeat'

            if user.stripe_cus_id is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                return dict(error='users_stripe_cus_not_found')

            payment_methods = stripe.PaymentMethod.list(
                customer=user.stripe_cus_id,
                type='card'
            )

            order_amount = calculate_order_amount(data['item'], db)
            intent = stripe.PaymentIntent.create(
                amount=order_amount,
                currency=data['currency'],
                payment_method=payment_methods['data'][0]['id'],
                customer=user.stripe_cus_id,
                confirm=True,
                off_session=True
            )

        return generate_response(intent, data, user, db, events_reporter)
    except stripe.error.CardError as e:
        # off-session errors
        err = e.error
        if err.code == 'authentication_required':
            # Bring the customer back on-session to authenticate the purchase
            # by sending an email or app notification to let them know
            # the off-session purchase failed
            # Probably we can save the PM ID and client_secret to authenticate the purchase later
            # without asking your customers to re-enter their details
            # err.payment_method.id, err.payment_intent.client_secret, err.payment_method.card
            return {
                'error': 'authentication_required',
            }
        elif err.code:
            # The card was declined for other reasons (e.g. insufficient funds)
            # Bring the customer back on-session by sending him a message asking him for a new payment method
            return {
                'error': err.code,
            }
    except Exception as e:
        response.status_code = status.HTTP_403_FORBIDDEN
        print(e)
        return dict(error=str(e))


def generate_response(intent: stripe.PaymentIntent, data: dict, user: ModelUsers,
                      db: Session,
                      events_reporter: EventsReporter):
    _status = intent['status']
    if _status == 'requires_action' or _status == 'requires_source_action':
        # Card requires authentication
        return {'requiresAction': True, 'paymentIntentId': intent['id'], 'clientSecret': intent['client_secret']}
    elif _status == 'requires_payment_method' or _status == 'requires_source':
        # Card was not properly authenticated, suggest a new payment method
        return {'error': 'Your card was denied, please provide a new payment method'}
    elif _status == 'succeeded':
        # Payment is complete, authentication not required
        # To cancel the payment after capture you will need to issue a Refund (https://stripe.com/docs/api/refunds)
        print("💰 Payment received!")
        if data['item']['type'] == 'subscription':
            if user.user_subscription_id is None:
                # 'user_subscriptions'
                to_create = ModelUserSubscription(
                    sub_id=data['item']['id']
                )
                db.add(to_create)
                db.commit()

                user_subscriptions_id = db.query(ModelUserSubscription).filter(
                    ModelUserSubscription.sub_id == data['item']['id']).first()

                # 'users'
                user.user_subscription_id = user_subscriptions_id.id
                db.add(user)
                db.commit()
            else:

                user_subscription = user.subscription

                if str(user_subscription.sub_id) != data['item']['id']:
                    return {'error': 'You are trying to pay for the wrong subscription'}

                user_subscription.status = "ACTIVE"
                db.add(user_subscription)
                db.commit()
        else:
            to_create = ModelUserMovies(
                user_id=user.id,
                movie_id=data['item']['id']
            )
            db.add(to_create)
            db.commit()

        # report new purchase
        events_reporter.report_status_change(str(user.id), data['item'], intent.amount, 'new')

        return {'clientSecret': intent['client_secret'], 'status': 'success'}


@router.get('/users/{user_id}/payments')
def get(
        user_id: str,
        type: str,
        db: Session = Depends(get_db)
) -> list:
    response = []
    if type == 'subscription':
        response = db.query(
            ModelUsers.id, ModelSubscriptions.name, ModelUserSubscription.status, ModelUserSubscription.updated_on
        ).filter(
            ModelUsers.id == user_id
        ).filter(
            ModelUserSubscription.id == ModelUsers.user_subscription_id
        ).filter(
            ModelSubscriptions.id == ModelUserSubscription.sub_id
        ).all()
    elif type == 'movies':
        response = db.query(
            ModelUsers.id, ModelMovies.name
        ).filter(
            ModelUserMovies.user_id == user_id
        ).filter(
            ModelMovies.id == ModelUserMovies.movie_id
        ).all()

    return response


@router.delete('/users/{user_id}/subscription')
def delete_users_subscription(
        user_id: str,
        chargeback: bool,
        db: Session = Depends(get_db),
        events_reporter: EventsReporter = Depends(get_events_reporter)
) -> dict:
    response = db.query(
        ModelUserSubscription
    ).filter(
        ModelUsers.id == user_id
    ).filter(
        ModelUserSubscription.id == ModelUsers.user_subscription_id
    ).first()

    if response is None:
        return {"response": f'The {object} not found'}
    else:
        if chargeback is True:
            response.status = "EXPIRED"
            db.add(response)
            db.commit()
            # report subscription end
            events_reporter.report_status_change(user_id,
                                                 {'type': 'subscription', 'id': str(response.sub_id)},
                                                 response.subscription.price,
                                                 'expired')
            return {"id": response.id, "status": response.status,
                    "mssage": "Subscription is discontinued. Money back on the card."}
        else:
            response.recurring = False
            db.add(response)
            db.commit()
            return {"id": response.id, "status": response.status,
                    "mssage": "Subscription will not be renewed."}


@router.delete('/users/{user_id}/movies')
def delete_movies(
        user_id: str,
        movie_id: str,
        db: Session = Depends(get_db),
        events_reporter: EventsReporter = Depends(get_events_reporter)
) -> dict:
    response = db.query(
        ModelUserMovies, ModelMovies
    ).filter(
        ModelUserMovies.user_id == user_id
    ).filter(
        ModelUserMovies.movie_id == movie_id
    ).filter(
        ModelUserMovies.movie_id == ModelMovies.id
    ).first()

    if response is None:
        return {"response": f'The object not found'}
    else:
        db.query(ModelUserMovies).filter(ModelUserMovies.id == response[0].id).delete()
        db.commit()
        # report movie "expiration"
        events_reporter.report_status_change(user_id,
                                             {'type': 'movie', 'id': str(response[1].id)},
                                             response[1].price,
                                             'expired')
        return {"response": response[0].id, "mssage": "Access to the film has been terminated."}
