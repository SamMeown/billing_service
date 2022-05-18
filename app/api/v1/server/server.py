import os

import stripe
from fastapi import APIRouter, Body, Response, status

router = APIRouter()

# Setup Stripe python client library
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')


@router.get('/stripe-key')
def fetch_key():
    # Send publishable key to client
    return {'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY')}
