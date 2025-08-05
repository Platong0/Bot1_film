from external import async_log_function_call

from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest

from external import async_log_function_call
from wiki_utils import fetch_and_save_film_with_actors as fetch_and_save_film_from_wiki

router = Router()


@router.message(Command("start"))
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        "Я перший бот Python розробника user."
    )


@router.message(CommandStart())
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer(
    "👋 Привіт! Це бот для роботи з базою фільмів.\n\n"
    "Ось що ти можеш зробити:\n"
    "🎬 /films — переглянути список усіх фільмів.\n"
    "🔎 /search_movie — знайти фільм за назвою.\n"
    "⚙️ /filter_movie — відфільтрувати фільми за жанром, рейтингом тощо.\n"
    "🎲 /random — показати випадковий фільм.\n"
    "📚 /wiki_film — додати фільм з Вікіпедії за назвою.\n\n"
    "Просто надішли відповідну команду або натисни на неї в меню.\n"
    "Якщо потрібна допомога — звертайся!"
    )


# Обробка будь-якого тексту (крім команд)
@router.message()
@async_log_function_call
async def handle_film_name(message: Message) -> None:
    title = message.text.strip()

    if title.startswith("/"):  # Якщо це команда — ігноруємо
        return

    film_info = await fetch_and_save_film_from_wiki(title)

    if film_info is None:
        await message.answer("Фільм не знайдено у Вікіпедії.")
        return

    poster_url = film_info.get("poster_url")
    actors = film_info.get("actors", "не знайдено")
    caption = f"🎬 Фільм '{title}' додано!\nАктори: {actors}"

    if poster_url:
        try:
            await message.answer_photo(poster_url, caption=caption)
        except TelegramBadRequest:
            await message.answer(f"{caption}\n(⚠️ Не вдалося завантажити зображення)")
    else:
        await message.answer(caption)

# Обробка відповіді на певне повідомлення
@router.message(F.reply_to_message, lambda m: m.reply_to_message.text == "Введи назву фільму з Вікіпедії:")
@async_log_function_call
async def handle_film_title(message: Message):
    title = message.text.strip()
    film_info = await fetch_and_save_film_from_wiki(title)

    if film_info is None:
        await message.answer("Фільм не знайдено у Вікіпедії.")
        return

    poster_url = film_info.get("poster_url")
    actors = film_info.get("actors", "не знайдено")
    caption = f"🎬 Фільм '{title}' додано!\nАктори: {actors}"

    if poster_url:
        try:
            await message.answer_photo(poster_url, caption=caption)
        except TelegramBadRequest:
            await message.answer(f"{caption}\n(⚠️ Не вдалося завантажити зображення)")
    else:
        await message.answer(caption)
