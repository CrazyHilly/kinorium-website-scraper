import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List

from app.schemas import Movie

DB_PATH = "database.db"
UPDATE_TIME = timedelta(hours=1)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    conn = get_conn()
    cursor = conn.cursor()
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            year INTEGER,
            country TEXT,
            rating_imdb REAL,
            last_seen_at TEXT
        );

        CREATE TABLE IF NOT EXISTS movie_genres (
            movie_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            UNIQUE(movie_id, genre_id)
        );

        CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genre_id INTEGER NOT NULL,
            genre TEXT NOT NULL,
            source_url TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            amount INTEGER NOT NULL,
            success INTEGER NOT NULL,
            error TEXT
        );
        """)
    conn.commit()
    conn.close()


def get_last_scrape_time(conn: sqlite3.Connection, genre_id: int) -> datetime | None:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT fetched_at
        FROM scrape_runs
        WHERE genre_id = ? AND success = 1
        ORDER BY fetched_at DESC
        LIMIT 1
        """,
        (genre_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    
    return datetime.fromisoformat(row["fetched_at"])


def is_db_data_fresh(conn: sqlite3.Connection, genre_id: int) -> bool:
    last = get_last_scrape_time(conn, genre_id)
    if not last:
        return False
    return datetime.now(timezone.utc) - last < UPDATE_TIME


def get_movies_for_genre(conn: sqlite3.Connection, genre_id: int) -> List[Movie]:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT m.title, m.year, m.url, m.country, m.rating_imdb
        FROM movies m
        JOIN movie_genres mg ON mg.movie_id = m.id
        WHERE mg.genre_id = ?
        """,
        (genre_id,),
    )
    rows = cursor.fetchall()
    return [
        Movie(
            title=row["title"],
            year=row["year"] or 0,
            url=row["url"],
            country=row["country"] or "",
            rating_imdb=row["rating_imdb"] or 0.0,
        )
        for row in rows
    ]


def save_genre_movies(
    conn: sqlite3.Connection,
    genre_id: int,
    genre: str,
    url: str,
    movies: List[Movie],
) -> None:
    cursor = conn.cursor()

    cursor.execute("DELETE FROM movie_genres WHERE genre_id = ?", (genre_id,))

    current_time = datetime.now(timezone.utc).isoformat()
    for m in movies:
        cursor.execute(
            """
            INSERT INTO movies (url, title, year, country, rating_imdb, last_seen_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
              title = excluded.title,
              year = excluded.year,
              country = excluded.country,
              rating_imdb = excluded.rating_imdb,
              last_seen_at = excluded.last_seen_at
            """,
            (m.url, m.title, m.year, m.country, m.rating_imdb, current_time),
        )
        cursor.execute(
            """
            INSERT INTO movie_genres (movie_id, genre_id)
            SELECT id, ? FROM movies WHERE url = ?
            """,
            (genre_id, m.url),
        )

    cursor.execute(
        """
        INSERT INTO scrape_runs (genre_id, genre, source_url, fetched_at, amount, success, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (genre_id, genre, url, current_time, len(movies), 1, None),
    )

    conn.commit()
