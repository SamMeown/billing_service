from fastapi import APIRouter

router = APIRouter()

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