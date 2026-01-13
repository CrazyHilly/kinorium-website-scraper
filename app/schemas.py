from pydantic import BaseModel


class Movie(BaseModel):
    title: str
    year: int
    url: str
    country: str
    rating_imdb: float
