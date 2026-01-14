from fastapi import HTTPException
from playwright.async_api import async_playwright

from app.core.config import settings


async def open_movie_page(search_title: str) -> dict:
    url = f"{settings.KINORIUM_BASE_URL}/search/?q={search_title.replace(' ', '%20')}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(url)
        await page.wait_for_timeout(3000)

        try:
            await page.wait_for_selector(".searchResult", timeout=10000, state="visible")
            results = page.locator(".searchResult")
            movie_link = results.locator("a.search-page__item-title-text").first
            movie_title = await movie_link.inner_text()
            movie_url = await movie_link.get_attribute("href")
            movie_url = settings.KINORIUM_BASE_URL + movie_url
            try:
                movie_data = await results.locator(".cut_text").first.inner_text()
                year = movie_data.split(",")[0].strip()
            except:
                year = "-"
        except:
            await browser.close()
            raise HTTPException(404, f"Movie '{search_title}' not found")

        await page.goto(movie_url)
        await page.wait_for_timeout(3000)
        await browser.close()

    return {
        "status": "opened",
        "search_text": search_title,
        "movie_title": movie_title,
        "year": year,
        "movie_url": movie_url
    }
