#wiki_handlers.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from wiki_utils import fetch_and_save_film_with_actors

router = Router()

class WikiStates(StatesGroup):
    waiting_for_title = State()

@router.message(Command("wiki_film"))
async def start_wiki_search(message: types.Message, state: FSMContext):
    await message.reply("Напиши название фильма, который хочешь найти в Википедии.")
    await state.set_state(WikiStates.waiting_for_title)

@router.message(WikiStates.waiting_for_title)
async def handle_film_title(message: types.Message, state: FSMContext):
    title = message.text.strip()
    result = await fetch_and_save_film_with_actors(title)  # <- await !!!
    
    if "error" in result:
        await message.answer(result["error"])
    else:
        response = (
            f"🎬 {title}\n"
            f"Актори: {result['actors']}\n"
            f"Опис: {result['description']}\n"
            f"Постер: {result['poster_url']}"
        )
        await message.answer(response)
    
    await state.clear()
