# commands.py - модуль в якому оголошені всі необхідні команди(та їх фільтри)
from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand


FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_CREATE_COMMAND = Command("create_film")
FILM_DELETE_COMMAND = Command("delete_movie")
FILM_FILTER_COMMAND = Command("filter_movie")
FILM_SEARCH_COMMAND = Command("search_movie")
FILM_EDIT_COMMAND = Command("edit_movie")

BOT_COMMANDS = [
   BotCommand(command="films", description="Перегляд списку фільмів"),
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="create_film", description="Додати новий фільм"),
   BotCommand(command="delete_movie", description="Редагувати фільм"),
   BotCommand(command="search_movie", description="Знайти фільм"),
   BotCommand(command="filter_movie", description="Фільтрувати фільми"),
   BotCommand(command="edit_movie", description="Редагувати фільм"),
]