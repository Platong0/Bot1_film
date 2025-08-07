#models.py

from pydantic import BaseModel


class Film(BaseModel):
    name: str
    description: str
    rating: float
    genre: str
    actors: list[str]
    poster: str | None  # poster может быть None

    @property
    def poster_url(self) -> str:
        if self.poster and self.poster.strip():
            return self.poster
        else:
            return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShncOlaOnQbwOG5dvZAi2HYPzlL4B2y14MPQ&s"

    
    