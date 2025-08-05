import json
import wikipedia
from typing import Union

wikipedia.set_lang("uk")  # встановлюємо українську мову за замовчуванням

# Отримати всі фільми або один за індексом
def get_films(file_path: str = "films.json", film_id: Union[int, None] = None) -> Union[list[dict], dict]:
    try:
        with open(file_path, 'r', encoding="utf-8") as fp:
            films = json.load(fp)
    except FileNotFoundError:
        films = []

    if film_id is not None and 0 <= film_id < len(films):
        return films[film_id]
    return films

# Додати новий фільм
def add_film(film: dict, file_path: str = "films.json"):
    films = get_films(file_path)
    films.append(film)
    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(films, fp, indent=4, ensure_ascii=False)

# Шукати фільм у Вікіпедії та зберігати його
def fetch_and_save_film_from_wiki(name: str, file_path: str = "films.json") -> str:
    try:
        page = wikipedia.page(name)
        summary = wikipedia.summary(name, sentences=3)

        new_film = {
            "name": page.title,
            "description": summary,
            "rating": 0,
            "genre": "невідомо",
            "actors": [],  # можна доповнити пізніше
            "poster": page.images[0] if page.images else ""
        }

        add_film(new_film, file_path)
        return f"🎬 Фільм '{new_film['name']}' додано з описом із Вікіпедії."

    except wikipedia.exceptions.DisambiguationError as e:
        return f"🔎 Назва не однозначна. Можливо ти мав на увазі: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return "😕 Нічого не знайдено у Вікіпедії."
