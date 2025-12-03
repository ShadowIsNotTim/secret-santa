import asyncio
import logging
import random
from aiofiles import open as a_open

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from aiogram.types import InputFile, FSInputFile

from tokens import *
import users

# Загружаем help-текст из файла при старте
HELP_TEXT = ""
try:
    with open("help.md", "r", encoding="utf-8") as f:
        HELP_TEXT = f.read()
except FileNotFoundError:
    HELP_TEXT = "❌ Файл справки не найден"
    logging.error("Файл help.md не найден")
except Exception as e:
    HELP_TEXT = "❌ Ошибка загрузки справки"
    logging.error(f"Ошибка загрузки help: {e}")

# Загружаем start-текст из файла при старте
START_TEXT = ""
try:
    with open("start.md", "r", encoding="utf-8") as f:
        START_TEXT = f.read()
except FileNotFoundError:
    START_TEXT = "❌ Файл справки не найден"
    logging.error("Файл start.md не найден")
except Exception as e:
    START_TEXT = "❌ Ошибка загрузки справки"
    logging.error(f"Ошибка загрузки start: {e}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    waiting_for_wishlist = State()
    waiting_for_info = State()


async def read_logs():
    try:
        async with a_open("bot.log", "r", encoding="utf-8") as f:
            return await f.read()
    except Exception as e:
        return f"Ошибка чтения логов 🥵: {e}"
    

@dp.message(Command("help"))
async def send_help(message: types.Message):
    """Отправляет новогодний help-текст"""
    await message.answer(HELP_TEXT, parse_mode="Markdown")


@dp.message(Command("logs"))
async def send_logs(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет доступа 😘")
        return
    await bot.send_document(message.chat.id, FSInputFile("bot.log"))


@dp.message(Command("info"))
async def set_info(message: types.Message, state: FSMContext):
    if message.from_user.id != OWNER_ID:
        await message.answer("У вас нет доступа 😘")
        return

    await message.answer("Жду сообщение для отправки")
    await state.set_state(RegistrationStates.waiting_for_info)


@dp.message(Command("register"))
async def register(message: types.Message):
    user = users.get_user(message.from_user.id)
    if user:
        await message.answer("Вы уже зарегистрированы 🫠")
        return
    if users.save_user(message.from_user.id, message.from_user.username):
        await message.answer("Успешная регистрация 🥳")
    else:
        await message.answer("Ошибка регистрации 🫣")


@dp.message(Command("unregister"))
async def unregister(message: types.Message):
    user = users.get_user(message.from_user.id)
    if not user:
        await message.answer("Вы еще не зарегистрировались 😰 /register")
        return
    if users.delete_user(message.from_user.id):
        await message.answer("Вы отчислены. 😬")
    else:
        await message.answer("Ошибка удаления 🫣")


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(START_TEXT, parse_mode="Markdown")


@dp.message(Command("new_year"))
async def new_year(message: types.Message):
    if message.from_user.id == OWNER_ID:
        dd = users.load_users()
        ids = list(dd.keys())
        random.shuffle(ids)
        for i in range(len(ids)):
            target = ids[(i + 1) % len(ids)]
            users.set_target(int(ids[i]), int(target))
            if int(ids[i]) == int(target):
                await message.answer("FATAL ERROR ON SHUFFLING!!!! FATAL ERROR!!!! 🫣🫣🫣")
                return
        for i in range(len(ids)):
            target = ids[(i + 1) % len(ids)]
            await bot.send_message(int(ids[i]),
                                   f"О боже?!? ты даришь @{dd[target]['tag']} 🤭\nПосмотреть его(её) вишлист можно через /check_wishlist")
    else:
        await message.answer("У вас нет доступа 😘")


@dp.message(Command("check"))
async def check(message: types.Message):
    user = users.get_user(message.from_user.id)
    print(user)
    if not user:
        await message.answer("Вы еще не зарегистрировались 😰 /register")
        return
    dd = users.load_users()
    target = dd[str(user["user_id"])]["target"]
    target_tag = dd.get(str(target), None)
    target_tag = target_tag["tag"] if target_tag is not None else target_tag
    if target_tag is not None:
        await message.answer(f"Ты даришь @{target_tag} 😈")
    else:
        await message.answer("Вы еще никому не дарите 🥲")


@dp.message(Command("my_wishlist"))
async def my_wishlist(message: types.Message, state: FSMContext):
    user = users.get_user(message.from_user.id)
    if not user:
        await message.answer("Вы еще не зарегистрировались 😰 /register")
        return
    await message.answer("Хорошо! Отправьте следующим сообщением свой вишлист или отправьте /cancel")
    await state.set_state(RegistrationStates.waiting_for_wishlist)


@dp.message(Command("get_my_wishlist"))
async def get_my_wishlist(message: types.Message, state: FSMContext):
    user = users.get_user(message.from_user.id)
    if not user:
        await message.answer("Вы еще не зарегистрировались 😰 /register")
        return
    await message.answer(f"Вот ваш виш лист: {user["wishlist"]}")


@dp.message(Command("check_wishlist"))
async def check_wishlist(message: types.Message):
    user = users.get_user(message.from_user.id)
    if not user:
        await message.answer("Вы еще не зарегистрировались 😰 /register")
        return
    await message.answer(f"Вишлист:\n{users.check_wishlist(user["user_id"])}")


@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных процессов для отмены")
        return
    await state.clear()
    await message.answer("Изменение отменено")


@dp.message(RegistrationStates.waiting_for_wishlist)
async def my_wishlist_state(message: types.Message, state: FSMContext):
    if users.set_wishlist(message.from_user.id, message.text):
        await message.answer("Ваш вишлист успешно изменен 🤡")
    else:
        await message.answer("Ошибка сохранения вишлиста, попробуйте заново /my_wishlist")
    await state.clear()


@dp.message(RegistrationStates.waiting_for_info)
async def send_info(message: types.Message, state: FSMContext):
    try:
        for user in users.load_users().keys():
            await bot.send_message(int(user), message.text)
        await message.answer("Успешная рассылка 😺")
    except Exception as e:
        logging.error(e)
        await message.answer("Что-то пошло не так /logs")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
