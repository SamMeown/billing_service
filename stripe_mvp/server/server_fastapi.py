import os
import logging

import stripe
import uvicorn
from fastapi import FastAPI, APIRouter, Response, Body, status
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv, find_dotenv


router = APIRouter()


# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))


app = FastAPI(
    title="Billing MVP",
    description='Billing API MVP using Stripe',
    docs_url='/mvp/openapi',
    openapi_url='/mvp/openapi.json',
)


users = {
    'alice': {
    }
}


subscriptions = {
    'subs_1m': {
        'type': 'subscription',
        'name': '1-Month Subscription',
        'price': 12,
    },
    'subs_1y': {
        'type': 'subscription',
        'name': '1-Year Subscription',
        'price': 120,
    },
}

movies = {
    'movie_swe4': {
        'type': 'movie',
        'name': 'Star Wars: Episode 4',
        'price': 8,
    },
    'movie_swe5': {
        'type': 'movie',
        'name': 'Star Wars: Episode 5',
        'price': 8,
    },
}


@router.get('/subscriptions')
def fetch_subscriptions():
    # Info about products
    return [{**sub_info, 'id': sub_id} for sub_id, sub_info in subscriptions.items()]


def calculate_order_amount(item):
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    product = subscriptions[item['id']] if item['type'] == 'subscription' else movies[item['id']]
    return product['price'] * 100  # in cents


@router.get('/stripe-key')
def fetch_key():
    # Send publishable key to client
    return {'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY')}


@router.post('/users/{user_id}/payments')
def pay(user_id: str, response: Response, data: dict = Body(...)):
    if (user := users.get(user_id)) is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return dict(error='user_not_found')

    # data = json.loads(request.data)
    try:
        if data['action'] == 'create':
            # create corresponding stripe customer if user doesn't have one yet
            if not user.get('stripe_cus_id'):
                stripe_customer = stripe.Customer.create()
                user['stripe_cus_id'] = stripe_customer['id']

            order_amount = calculate_order_amount(data['item'])
            payment_intent_data = dict(
                amount=order_amount,
                currency=data['currency'],
                payment_method=data['paymentMethodId'],
                confirmation_method='manual',
                confirm=True
            )

            payment_intent_data['customer'] = user['stripe_cus_id']

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
            if not user.get('stripe_cus_id'):
                response.status_code = status.HTTP_404_NOT_FOUND
                return dict(error='users_stripe_cus_not_found')

            payment_methods = stripe.PaymentMethod.list(
                customer=user['stripe_cus_id'],
                type='card'
            )

            intent = stripe.PaymentIntent.create(
                amount=calculate_order_amount(data['item']),
                currency=data['currency'],
                payment_method=payment_methods['data'][0]['id'],
                customer=user['stripe_cus_id'],
                confirm=True,
                off_session=True
            )
        return generate_response(intent)
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
        return dict(error=str(e))


def generate_response(intent):
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
        return {'clientSecret': intent['client_secret']}


app.include_router(router)
app.mount('/', StaticFiles(directory=static_dir, html=True), name='static')


if __name__ == '__main__':
    uvicorn.run('server_fastapi:app', host='0.0.0.0', port=4242, log_level=logging.DEBUG, debug=True)
