from fastapi import APIRouter, Response, Body, status
import stripe

router = APIRouter()

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

users = {
    'alice': {
    }
}

def calculate_order_amount(item):
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    product = subscriptions[item['id']] if item['type'] == 'subscription' else movies[item['id']]
    return product['price'] * 100  # in cents


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