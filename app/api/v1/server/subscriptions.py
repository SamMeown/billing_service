from fastapi import APIRouter, Depends
from app.db.database import get_db
from sqlalchemy.orm import Session
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from app.db.db_models import ModelSubscriptions

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


@router.get('/subscriptions')
def fetch_subscriptions():
    # Info about products
    return [{**sub_info, 'id': sub_id} for sub_id, sub_info in subscriptions.items()]

# @router.get('/subscriptions')
# def fetch_subscriptions(
#         db: Session = Depends(get_db),
#         params: Params = Depends()
# ) -> dict:
#     return {
#         "success": True,
#         "response": paginate(db.query(ModelSubscriptions), params)
#     }
