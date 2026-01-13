import sqlite3
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query

from app.core.config import settings
from app.db import get_db, is_db_data_fresh, get_movies_from_db
from app.schemas import Movie
from app.services.scrapers.http import get_movies_by_genre

router = APIRouter()


@router.get("/genre/{genre}")
async def scrape_genre(
        genre: str, 
        conn: sqlite3.Connection=Depends(get_db),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=200, description="Movies per page")
        ) -> dict:
    """Get movies by genre: return from db or auto-scrape if does not exist."""
    genre_id = _get_genre_id(genre)

    if is_db_data_fresh(conn, genre_id):
        movies = get_movies_from_db(conn, genre_id)
    else:
        movies = await _scrape_genre(conn, genre_id, genre)

    return _get_movies_per_page(genre_id, genre, movies, page, size)


@router.post("/genre/{genre}/scrape")
async def force_scrape_genre(
        genre: str, 
        conn: sqlite3.Connection = Depends(get_db),
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(50, ge=1, le=200, description="Movies per page")
        ) -> dict:
    """Force scrape movies by genre ignoring cache."""
    genre_id = _get_genre_id(genre)

    movies = await _scrape_genre(conn, genre_id, genre)

    return _get_movies_per_page(genre_id, genre, movies, page, size)


async def _scrape_genre(
        conn: sqlite3.Connection, 
        genre_id: int, 
        genre: str
        ) -> List[Movie]:
    try:
        return await get_movies_by_genre(conn, genre_id, genre)
    except TimeoutError as e:
        raise HTTPException(408, f"Timeout error: {e}")
    except Exception as e:
        raise HTTPException(500, f"Scraping error: {e}")
    

def _get_genre_id(genre: str) -> int:
    if genre.lower() not in settings.GENRE_IDS:
        raise HTTPException(400, f"Genre '{genre}' not found")
    
    return settings.GENRE_IDS[genre.lower()]


def _get_movies_per_page(
        genre_id: int, 
        genre: str, 
        movies: List[Movie], 
        page: int, 
        size: int
        ) -> dict:
    total = len(movies)
    start = (page - 1) * size
    end = start + size
    movies_per_page = movies[start:end]

    return {
        "genre_id": genre_id,
        "genre": genre,
        "amount": total,
        "page": page,
        "per_page": size,
        "pages": (total + size - 1) // size,
        "movies": movies_per_page
    }
