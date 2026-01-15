import re
import sqlite3
from typing import List

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from app.core.config import settings
from app.db import save_data_to_db
from app.schemas import Movie


async def get_movies_by_genre(
        conn: sqlite3.Connection, 
        genre_id: int, 
        genre: str
        ) -> List[Movie]:
    page_num = 1
    page_total = 1
    movies = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--disable-images',
                '--disable-web-security',
                '--disable-gpu',
                '--no-sandbox',
            ]
            )
        page = await browser.new_page()
        await page.route(
            "**/*.{png,jpg,jpeg,gif,svg,woff}", 
            lambda route: route.abort()
            )

        while page_num <= page_total:
            url = f"{settings.KINORIUM_GENRE_URL}{genre_id}&page={page_num}"
            await page.goto(url, wait_until="domcontentloaded")

            movie_selector = "headlines_type-, .item" 
            await page.wait_for_selector(movie_selector, state="visible", timeout=20000)
        
            content_txt = await page.content()

            content = BeautifulSoup(content_txt, "html.parser")
            pages_el = content.find("ul", class_="pages")
            try:
                page_total = int(pages_el.find_all("a")[-1].text)
            except:
                page_total = 1
            
            movie_cards = content.find_all("div", class_="filmList__item-content")
            for card in movie_cards:
                title_el = card.find("span", class_="title")
                title = title_el.get_text(strip=True) if title_el else ""
                if not title:
                    continue
                
                year = 0
                country = ""
                rating_imdb = 0.0
                movie_url = ""

                url_el = card.find("a", href=True)
                if url_el:
                    movie_url = f"{settings.KINORIUM_BASE_URL}{url_el['href']}"

                info = card.find("div", class_="info")
                if info:
                    try:
                        year_el = info.find("small").get_text(strip=True)
                        year_match = re.search(r"(\d{4})", year_el)
                        year = int(year_match.group(1))
                    except:
                        year = 0

                    country_el = info.find(
                        "span", class_="filmList__extra-info-director"
                        )
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
            page_num += 1

        await browser.close()
    
    if movies:
        save_data_to_db(conn, genre_id, genre, url, movies)

    return movies
