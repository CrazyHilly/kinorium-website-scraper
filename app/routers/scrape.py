import sqlite3

from fastapi import APIRouter, HTTPException, Depends

from app.core.config import settings
from app.db import get_db, is_db_data_fresh, get_movies_from_db
from app.schemas import GenreResponse
from app.services.scrapers.http import get_movies_by_genre

router = APIRouter()


@router.get("/genre/{genre}")
async def scrape_genre(genre: str, conn: sqlite3.Connection=Depends(get_db)):
    """Get movies by genre: return from db or auto-scrape if does not exist."""
    genre_id = _get_genre_id(genre)

    if is_db_data_fresh(conn, genre_id):
        movies = get_movies_from_db(conn, genre_id)
        return GenreResponse(
            genre_id=genre_id,
            genre=genre,
            amount=len(movies),
            movies=movies,
        )
    
    return await _scrape_genre(conn, genre_id, genre)


@router.post("/genre/{genre}/scrape")
async def force_scrape_genre(genre: str, conn: sqlite3.Connection = Depends(get_db)):
    """Force scrape movies by genre ignoring cache."""
    genre_id = _get_genre_id(genre)
    return await _scrape_genre(conn, genre_id, genre)


async def _scrape_genre(
        conn: sqlite3.Connection, 
        genre_id: int, 
        genre: str
        ) -> GenreResponse:
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
