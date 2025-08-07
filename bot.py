import random 
import asyncio
import logging
import sys
import re
import wikipedia

# Імпортуємо необхідні модулі з aiogram (фреймворк для створення Telegram-ботів)
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, URLInputFile, FSInputFile
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Імпортуємо власні модулі
from wiki_handlers import router as wiki_router
from config import TOKEN
from commands import BOT_COMMANDS, FILMS_COMMAND, FILM_SEARCH_COMMAND, FILM_FILTER_COMMAND
from data import get_films
from keyboards import films_keyboard_markup, FilmCallback
from models import Film
from external import async_log_function_call
from handlers import info

# Додаємо батьківську директорію до шляху для імпорту модулів
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Встановлюємо мову для Wikipedia (українська)
wikipedia.set_lang("uk")

# --- Класи станів (FSM) ---
class FilmForm(StatesGroup):
    name = State()
    description = State()
    rating = State()
    genre = State()
    actors = State()
    poster = State()

class MovieStates(StatesGroup):
    search_query = State()
    filter_criteria = State()
    delete_query = State()
    edit_query = State()
    edit_description = State()

# --- Допоміжні функції ---
# Перевірка чи є рядок валідною URL-адресою
def is_valid_url(url: str) -> bool:
    return re.match(r'^https?://', url or '') is not None

# Безпечне отримання фільмів (з обробкою помилок)
def safe_get_films(film_id=None):
    try:
        result = get_films(film_id=film_id)
        if not result:
            logging.warning("get_films повернув порожній результат.")
            return None if film_id else []
        return result
    except Exception as e:
        logging.error(f"Помилка при отриманні фільмів: {e}")
        return None if film_id else []

# Створення об'єкта Film з отриманих даних
def film_from_data(data: dict) -> Film:
    return Film(
        name=data.get('name'),
        description=data.get('description'),
        rating=data.get('rating'),
        genre=data.get('genre'),
        actors=data.get('actors'),
        poster=data.get('poster_url') or data.get('poster') or "no-image.png"
    )

# Надсилання постеру фільму (через URL або локальний файл-заглушку)
async def send_film_photo(message_or_cb, film: Film, text: str):
    poster_url = film.poster or "no-image.png"

    try:
        if poster_url == "no-image.png":
            # Якщо немає постера — надсилаємо локальну заглушку
            await message_or_cb.answer_photo(
                photo=FSInputFile("no-image.png"),
                caption=text
            )
        elif is_valid_url(poster_url):
            # Якщо URL дійсний — надсилаємо постер з інтернету
            await message_or_cb.answer_photo(
                photo=URLInputFile(poster_url),
                caption=text
            )
        else:
            # Якщо URL недійсний — знову використовуємо заглушку
            await message_or_cb.answer_photo(
                photo=FSInputFile("no-image.png"),
                caption=text
            )
    except TelegramNetworkError:
        # Якщо сталася мережева помилка — надсилаємо заглушку
        await message_or_cb.answer_photo(
            photo=FSInputFile("no-image.png"),
            caption=text
        )

# --- Ініціалізація Dispatcher ---
dp = Dispatcher()
dp.include_router(wiki_router)  # Маршрути з wiki
dp.include_router(info.router)  # Інформаційні хендлери

# --- Хендлери команд ---
@dp.message(FILMS_COMMAND)
@async_log_function_call
async def films_list(message: Message) -> None:
    data = safe_get_films()
    markup = films_keyboard_markup(films_list=data)
    await message.answer(
        "Перелік фільмів. Натисніть на назву фільму для отримання деталей.",
        reply_markup=markup
    )

# Обробник натискання на кнопку з назвою фільму
@dp.callback_query(FilmCallback.filter())
@async_log_function_call
async def callb_film(callback: CallbackQuery, callback_data: FilmCallback) -> None:
    film_data = safe_get_films(film_id=callback_data.id)
    if not film_data:
        await callback.message.answer("Фільм не знайдено.")
        return

    try:
        film = film_from_data(film_data)
    except Exception as e:
        logging.error(f"❌ Помилка при створенні Film: {e}\nДані: {film_data}")
        await callback.message.answer("Не вдалося завантажити інформацію про цей фільм.")
        return

    text = (
        f"Фільм: {film.name}\n"
        f"Опис: {film.description}\n"
        f"Рейтинг: {film.rating}\n"
        f"Жанр: {film.genre or 'Невідомо'}\n"
        f"Актори: {', '.join(film.actors) if film.actors else 'Немає даних'}\n"
    )
    await send_film_photo(callback.message, film, text)

# Команда пошуку фільму
@dp.message(FILM_SEARCH_COMMAND)
@async_log_function_call
async def search_movie(message: Message, state: FSMContext):
    await message.reply("Введіть назву фільму для пошуку:")
    await state.set_state(MovieStates.search_query)

# Отримання запиту для пошуку
@dp.message(MovieStates.search_query)
@async_log_function_call
async def get_search_query(message: Message, state: FSMContext):
    query = message.text.lower()
    films = safe_get_films()
    results = [film for film in films if query in film['name'].lower()]

    if results:
        for film in results:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено.")

    await state.clear()

# Команда фільтрації за жанром
@dp.message(FILM_FILTER_COMMAND)
@async_log_function_call
async def filter_movies(message: Message, state: FSMContext):
    await message.reply("Введіть жанр для фільтрації:")
    await state.set_state(MovieStates.filter_criteria)

# Отримання критерію фільтрації
@dp.message(MovieStates.filter_criteria)
@async_log_function_call
async def get_filter_criteria(message: Message, state: FSMContext):
    films = safe_get_films()
    criteria = message.text.lower()
    filtered = [film for film in films if criteria in (film['genre'] or '').lower()]

    if filtered:
        for film in filtered:
            await message.reply(f"Знайдено: {film['name']} - {film['description']}")
    else:
        await message.reply("Фільм не знайдено за цими критеріями.")

    await state.clear()

# Команда /best_film — показує фільм з найвищим рейтингом
@dp.message(Command("best_film"))
@async_log_function_call
async def best_film(message: Message):
    films = safe_get_films()
    if not films:
        await message.reply("У базі немає фільмів.")
        return
    film = max(films, key=lambda film: film.get('rating') or 0)
    await message.reply(f"Найкращий фільм: {film['name']} (Рейтинг: {film['rating']})")

# Команда /random — показує випадковий фільм
@dp.message(Command("random"))
@async_log_function_call
async def random_film(message: Message, state: FSMContext) -> None:
    films = safe_get_films()
    if not films:
        await message.answer("У базі немає фільмів.")
        return

    film_data = random.choice(films)

    try:
        film = film_from_data(film_data)
    except Exception as e:
        logging.error(f"❌ Неможливо завантажити випадковий фільм: {e}")
        await message.answer("Помилка при завантаженні випадкового фільму.")
        return

    text = (
        f"🎲 Випадковий фільм:\n\n"
        f"<b>Фільм:</b> {film.name}\n"
        f"<b>Опис:</b> {film.description}\n"
        f"<b>Рейтинг:</b> {film.rating}\n"
        f"<b>Жанр:</b> {film.genre or 'Невідомо'}\n"
        f"<b>Актори:</b> {', '.join(film.actors) if film.actors else 'Немає даних'}"
    )
    await send_film_photo(message, film, text)
    await state.clear()

# --- Запуск бота ---
async def main() -> None:
    print("✅ Бот запускається...")
    bot = Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    await bot.set_my_commands(BOT_COMMANDS)  # Встановлюємо список доступних команд
    await dp.start_polling(bot)  # Запускаємо бот у режимі опитування

# Точка входу
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
