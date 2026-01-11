from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KINORIUM_BASE_URL: str = "https://ua.kinorium.com"
    KINORIUM_GENRE_URL: str = "https://ua.kinorium.com/collections/kinorium"
    GENRE_IDS: dict = {
        "action": 304,
        "adventures": 317,
        "animated_series": 325,
        "animated_short_film": 326,
        "animation": 315,
        "anime": 302,
        "anime_series": 324,
        "biography": 303,
        "comedy": 311,
        "crime": 313,
        "detective": 307,
        "documentary": 308,
        "drama": 309,
        "family": 318,
        "fantasy": 323,
        "history": 310,
        "horror": 321,
        "musical": 316,
        "romance": 314,
        "sci-fi": 322,
        "short_film": 312,
        "sport": 319,
        "stand_up": 932,
        "thriller": 320,
        "war": 306,
        "western": 305,
    }

settings = Settings()
