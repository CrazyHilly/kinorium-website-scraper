import re
from typing import List

from bs4 import BeautifulSoup
from fastapi import HTTPException
from playwright.async_api import async_playwright
from pydantic import BaseModel

from app.core.config import settings


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


async def get_movies_by_genre(genre: str) -> GenreResponse:
    if genre.lower() not in settings.GENRE_IDS:
        raise HTTPException(400, f"Genre '{genre}' not found")
    genre_id = settings.GENRE_IDS.get(genre.lower())
    
    url = f"{settings.KINORIUM_GENRE_URL}/{genre_id}/"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(3000)
        content_txt = await page.content()

        content = BeautifulSoup(content_txt, "html.parser")
        movie_cards = content.find_all("div", class_="item headlines_type-")

        movies = []
        for card in movie_cards:
            title_el = card.find("span", class_="title")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title:
                continue

            url_el = card.find("a", href=True)
            movie_url = f"{settings.KINORIUM_BASE_URL}{url_el['href']}" if url_el else ""

            year = 0
            country = ""
            rating_imdb = 0.0

            info = card.find("div", class_="info")
            if info:
                try:
                    year_el = info.find("small").get_text(strip=True)
                    year_match = re.search(r"(\d{4})$", year_el)
                    year = int(year_match.group(1))
                except:
                    year = 0

                country_el = info.find("span", class_="filmList__extra-info-director")
                country_text = country_el.get_text(strip=True) if country_el else ""
                country = country_text.split("•")[0].strip() if country_text else ""

                rating_el = info.find("li", class_="rating_imdb")
                try:
                    rating_text = rating_el.find("span", class_="value green")
                    rating_imdb = float(rating_text.get_text(strip=True))
                except:
                    rating_imdb = 0.0

            movies.append(
                Movie(
                    title=title,
                    year=year,
                    url=movie_url,
                    country=country,
                    rating_imdb=rating_imdb,
                )
            )

        await browser.close()

    return GenreResponse(
        genre_id=genre_id,
        genre=genre,
        amount=len(movies),
        movies=movies,
    )
