from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelUserMovies
from app.models.user_movies import UserMovieBase

router = APIRouter()
object = 'user_movies'


@router.get('/user_movies')
def fetch_subscriptions(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> list:
    _user_movies = jsonable_encoder(paginate(db.query(ModelUserMovies), params))
    return _user_movies
    if _user_movies.get('items') is not None:
        return _user_movies.get('items')
    return []


@router.get("/user_movies/{id}")
def get_id(
        id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelUserMovies).filter(ModelUserMovies.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response