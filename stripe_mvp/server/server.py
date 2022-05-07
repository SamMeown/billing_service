import stripe
import json
import os

from flask import Flask, render_template, jsonify, request, send_from_directory
from dotenv import load_dotenv, find_dotenv

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)

# no cache now
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


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


@app.route('/', methods=['GET'])
def get_example():
    # Display checkout page
    return render_template('index.html')


@app.route('/subscriptions', methods=['GET'])
def fetch_subscriptions():
    # Info about products
    return jsonify([{**sub_info, 'id': sub_id} for sub_id, sub_info in subscriptions.items()])


def calculate_order_amount(item):
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return subscriptions[item['id']] if item['type'] == 'subscription' else movies[item['id']]


@app.route('/stripe-key', methods=['GET'])
def fetch_key():
    # Send publishable key to client
    return jsonify({'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY')})


@app.route('/pay', methods=['POST'])
def pay():
    data = json.loads(request.data)
    try:
        if "paymentIntentId" not in data:
            order_amount = calculate_order_amount(data['items'])
            payment_intent_data = dict(
                amount=order_amount,
                currency=data['currency'],
                payment_method=data['paymentMethodId'],
                confirmation_method='manual',
                confirm=True
            )

            if data['isSavingCard']:
                # Create a Customer to store the PaymentMethod for reuse
                # customer = stripe.Customer.create()
                # payment_intent_data['customer'] = customer['id']
                payment_intent_data['customer'] = 'cus_Le0fM1iaXnHpwK'
                
                # setup_future_usage saves the card and tells Stripe how you plan to use it later
                # set to 'off_session' if you plan on charging the saved card when the customer is not present
                payment_intent_data['setup_future_usage'] = 'off_session'

            # Create a new PaymentIntent for the order
            intent = stripe.PaymentIntent.create(**payment_intent_data)
        else:
            # Confirm the PaymentIntent to collect the money
            intent = stripe.PaymentIntent.confirm(data['paymentIntentId'])
        return generate_response(intent)
    except Exception as e:
        return jsonify(error=str(e)), 403


def generate_response(intent):
    status = intent['status']
    if status == 'requires_action' or status == 'requires_source_action':
        # Card requires authentication
        return jsonify({'requiresAction': True, 'paymentIntentId': intent['id'], 'clientSecret': intent['client_secret']})
    elif status == 'requires_payment_method' or status == 'requires_source':
        # Card was not properly authenticated, suggest a new payment method
        return jsonify({'error': 'Your card was denied, please provide a new payment method'})
    elif status == 'succeeded':
        # Payment is complete, authentication not required
        # To cancel the payment after capture you will need to issue a Refund (https://stripe.com/docs/api/refunds)
        print("💰 Payment received!")
        return jsonify({'clientSecret': intent['client_secret']})


if __name__ == '__main__':
    app.run()
