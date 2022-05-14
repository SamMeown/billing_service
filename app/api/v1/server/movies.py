from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Query
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_models import ModelMovies
from app.models.movies import MovieBase

router = APIRouter()
object = 'movies'


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


@router.get('/movies')
def fetch_subscriptions(
        db: Session = Depends(get_db),
        params: Params = Depends()
) -> list:
    _movies = jsonable_encoder(paginate(db.query(ModelMovies), params))
    if _movies.get('items') is not None:
        return _movies.get('items')
    return []


@router.get("/movies/{id}")
def get_id(
        id: Optional[str],
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelMovies).filter(ModelMovies.id == id).first()
    if response is None:
        return {"response": f'The {object} not found'}
    else:
        return response


@router.post("/movies")
def create(
        movies: MovieBase,
        db: Session = Depends(get_db)
) -> dict:
    if db.query(ModelMovies).filter(ModelMovies.name == movies.name).first() is not None:
        return {"response": f'The {object} already exists'}
    else:
        to_create = ModelMovies(
            name=movies.name,
            description=movies.description,
            price=movies.price
        )

        db.add(to_create)
        db.commit()
        return {"response": to_create.id}


@router.put("/movies/{id}")
async def update(
        id: Optional[str],
        movies: MovieBase,
        db: Session = Depends(get_db)
) -> dict:
    response = db.query(ModelMovies).filter(ModelMovies.id == id).first()

    if response is None:
        return {"response": f'The {object} not found'}
    else:
        response.name = movies.name
        response.description = movies.description
        response.price = movies.price

        db.add(response)
        db.commit()
        return {"response": id}
