from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    KINORIUM_BASE_URL: str = "https://ua.kinorium.com"
    KINORIUM_GENRE_URL: str = \
        "https://ua.kinorium.com/R2D2/?order=rating&perpage=200&genres%5B%5D="
    GENRE_IDS: dict = {
        "action": 3,
        "adventure": 22,
        "animation": 19,
        "anime": 1,
        "award": 32,
        "biography": 2,
        "comedy": 13,
        "concert": 14,
        "crime": 16,
        "documentary": 9,
        "drama": 10,
        "family": 24,
        "fantasy": 31,
        "film-noir": 30,
        "game-show": 11,
        "history": 12,
        "horror": 28,
        "musical": 18,
        "musical": 20,
        "mystery": 6,
        "mystic": 58,
        "news": 21,
        "reality": 23,
        "romance": 17,
        "sci-fi": 29,
        "short": 15,
        "sport": 25,
        "talk-show": 26,
        "thriller": 27,
        "war": 5,
        "western": 4,
    }

settings = Settings()
