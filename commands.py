# commands.py - модуль в якому оголошені всі необхідні команди(та їх фільтри)
from aiogram.filters import Command
from aiogram.types.bot_command import BotCommand


FILMS_COMMAND = Command('films')
START_COMMAND = Command('start')
FILM_FILTER_COMMAND = Command("filter_movie")
FILM_SEARCH_COMMAND = Command("search_movie")
RANDOM_FILM_COMMAND = Command("random")
WIKI_FILM_COMMAND = Command("wiki_film")

BOT_COMMANDS = [
   BotCommand(command="films", description="Перегляд списку фільмів"),
   BotCommand(command="start", description="Почати розмову"),
   BotCommand(command="search_movie", description="Знайти фільм"),
   BotCommand(command="filter_movie", description="Фільтрувати фільми"),
   BotCommand(command="random", description="Показати випадковий фільм"),
   BotCommand(command="wiki_film", description="Додати фільм з Вікіпедії"),

]