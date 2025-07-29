from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from external import async_log_function_call

from aiogram import Router

r = Router()

@r.message(Command("start"))
@async_log_function_call
async def start(message: Message) -> None:
    await message.answer(
        f"Вітаю, {message.from_user.full_name}!\n"
        "Я перший бот Python розробника user."
    )