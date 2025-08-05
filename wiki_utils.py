#wiki_utils.py

import wikipedia
import re
from data import add_film
import aiohttp

DEFAULT_POSTER_URL = "https://example.com/path/to/no-image.png"

wikipedia.set_lang("uk")

def extract_actors_from_content(content: str) -> list[str]:
    pattern = re.compile(r"(Актори|Cast|В ролях)[\s\S]*?(?:\n\n|\Z)", re.IGNORECASE)
    match = pattern.search(content)
    if not match:
        return []
    section = match.group(0)
    actors = re.findall(r"^\*?\s*([А-ЯҐЄЇ][а-яґєії']+(?:\s[А-ЯҐЄЇ][а-яґєії']+)*)", section, re.MULTILINE)
    return actors

async def is_url_valid(url: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=5) as resp:
                return resp.status == 200
    except Exception:
        return False

async def fetch_and_save_film_with_actors(title: str) -> dict | None:
    try:
        page = wikipedia.page(title)
        summary = wikipedia.summary(title, sentences=3)
        actors = extract_actors_from_content(page.content)

        poster_url = page.images[0] if page.images else DEFAULT_POSTER_URL
        if not poster_url or not poster_url.startswith("http"):
            poster_url = DEFAULT_POSTER_URL

        if not await is_url_valid(poster_url):
            poster_url = DEFAULT_POSTER_URL

        film = {
            "name": page.title,
            "description": summary,
            "rating": 0,
            "genre": "Unknown",
            "actors": actors if actors else [],
            "poster_url": poster_url
        }

        add_film(film)
        return {
            "poster_url": poster_url,
            "actors": ", ".join(actors) if actors else "не знайдено",
            "description": summary
        }
    except wikipedia.exceptions.DisambiguationError as e:
        return {"error": f"🔎 Назва не однозначна. Можливо ти мав на увазі: {', '.join(e.options[:3])}"}
    except wikipedia.exceptions.PageError:
        return {"error": "😕 Нічого не знайдено у Вікіпедії."}
