# Kinorium.ua Movie Scraper API

FastAPI REST API that scrapes [Kinorium.ua](https://ua.kinorium.com/) website for:

- **movies per genre** and stores data in SQLite database
- **movie by search** and opens movie page in Chromium browser

## Installation

1. **Clone the repository**

   `git clone <your-repo-url> `
   `cd kinorium-website-scraper  `
2. **Install Python dependencies**

   `pip install -r requirements.txt`
3. **Install Playwright Chromium browser**

   `playwright install chromium  `
4. **Run the server**
   `uvicorn app.main:app --port 8002`

Server will be available at [http://localhost:8002](http://localhost:8002/)

## Usage

Open in browser:

* **Interactive API docs** : [http://localhost:8002/docs](http://localhost:8002/docs)
* **Alternative docs** : [http://localhost:8002/redoc](http://localhost:8002/redoc)

## Example API calls

`http://localhost:8002/genre/concert`

`http://localhost:8002/genre/news/scrape`

`http://localhost:8002/genre/action?page=1&size=50`

`http://127.0.0.1:8002/movie/avatar/open`

 **Sample response** :

`{ "genre_id": 5, "genre": "war", "amount": 8592, "page": 1, "per_page": 50, "pages": 172, "movies": [ { "title": "Безславні виродки", "year": 2009, "url": "https://ua.kinorium.com/283333/", "country": "США, Німеччина", "rating_imdb": 8.4 }, { "title": "Список Шиндлера", "year": 1993, "url": "https://ua.kinorium.com/98467/", "country": "США", "rating_imdb": 9 }, ... ] } `

`{ "status": "opened", "search_text": "аватар", "movie_title": "Аватар", "year": "2009", "movie_url": "https://ua.kinorium.com/372833/" }`

## API Endpoints

| Method   | Endpoint                  | Description                         | Response Time     |
| -------- | ------------------------- | ----------------------------------- | ----------------- |
| `GET`  | `/`                     | Health check                        | < 1ms             |
| `GET`  | `/genre/{genre}`        | Get movies for genre (cache/scrape) | 0.1-0.5s / 2-5min |
| `POST` | `/genre/{genre}/scrape` | Force scrape genre                  | 2-5min            |
| `GET`  | `/movie/{title}/open`   | Search movie and open in browser    | 10s               |

 **Supported genres** : `action`, `adventure`, `animation`, `comedy`, `crime`, `documentary`, `drama`, `family`, `fantasy`, `horror`, `musical`, `mystery`, `romance`, `sci-fi`, `thriller`, `war`, `western` (case-insensitive). Full list in `app/core/config.py`.

 **Pagination params** :

* `page` (default=1, min=1)
* `size` (default=50, 1-200)

Example: `/genre/drama?page=2&size=100` → movies 51-150

**Error responses** :

* `400 Bad Request`: Invalid genre name
* `408 Request Timeout`: Scraping timeout
* `500 Internal Server Error`: Parsing/network error

## Database Schema

SQLite database `database.db` with 3 tables:

`movies(id, url UNIQUE, title, year, country, rating_imdb, last_seen_at)  `

`movie_genres(movie_id, genre_id UNIQUE)  `

`scrape_runs(id, genre_id, genre, source_url, fetched_at, amount, success, error)`

**Caching logic** : Data is fresh if scraped within last 1 hour (`UPDATE_TIME = timedelta(hours=1)`).
