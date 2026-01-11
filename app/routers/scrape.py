from fastapi import APIRouter, HTTPException

from app.services.scrapers.http import get_movies_by_genre

router = APIRouter()


@router.get("/genre/{genre}")
async def scrape_genre(genre: str):
    try:
        return await get_movies_by_genre(genre)
    except TimeoutError as e:
        raise HTTPException(408, f"Timeout error: {e}")
    except Exception as e:
        raise HTTPException(500, f"Scraping error: {e}")
