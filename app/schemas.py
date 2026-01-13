from typing import List

from pydantic import BaseModel


class Movie(BaseModel):
    title: str
    year: int
    url: str
    country: str
    rating_imdb: float


class GenreResponse(BaseModel):
    genre_id: int
    genre: str
    amount: int
    movies: List[Movie]