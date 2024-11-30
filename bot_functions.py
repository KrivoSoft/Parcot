from datetime import datetime, timedelta, date
import yaml
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State, default_state
from aiogram.types import Message
from aiogram.types import (
    ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery)
from model import *

""" Получаем данные из файла настроек """
with open('settings.yml', 'r', encoding='utf-8') as file:
    CONSTANTS = yaml.safe_load(file)
API_TOKEN = CONSTANTS['API_TOKEN']

ROLE_BIG_ADMINISTRATOR = "BIG_ADMINISTRATOR"
ROLE_LITTLE_ADMINISTRATOR = "LITTLE_ADMINISTRATOR"
ROLE_USER = "USER"
UNKNOWN_USER_MESSAGE_1 = "Для Вас пока не назначено парковочное место. Обратитесь к руководителю."

bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

def run_bot():
    print("Запускаю бота...")
    dp.run_polling(bot)


async def is_user_unauthorized(message: Message):
    authorized_ids = [user.telegram_id for user in Employee.select()]

    if message.from_user.id not in authorized_ids:
        return True
    return False


@dp.message(Command(commands=["start"]))
async def process_start_command(message: Message, state: FSMContext):
    """ Этот хэндлер обрабатывает команду "/start" """

    """ Проверяем зарегистрирован ли пользователь """
    if await is_user_unauthorized(message):

        """ Проверяем, если этот пользователь уже обращался к боту, то заносить его повторно не нужно """
        guest = Guest.select().where(
            (Guest.username == message.from_user.username) &
            (Guest.first_name == message.from_user.first_name) &
            (Guest.last_name == message.from_user.last_name)
        ).first()
        if guest is None:
            """ Добавляем нового гостя в БД """
            new_guest = Guest.create(
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                telegram_id=message.from_user.id
            )
            new_guest.save()

    """ Переменные, указывающие на то, какие кнопки меню будут доступны в дальнейшем """
    show_change_spot_type_button = False
    show_minus_live_button = False
    show_utilisation_button = False
    show_add_big_administrator_button = False
    show_add_little_administrator_button = False
    show_add_user = False

    show_change_lives_button = False
    show_add_user_button = False
    show_delete_user_button = False

    show_book_spot_button = False
    show_history_button = False

    """ Топорно пропишем полномочия на кнопки меню """
    user_telegram_id = message.from_user.id
    user_role = Employee.get_user_role(user_telegram_id)

    if user_role == ROLE_BIG_ADMINISTRATOR:
        show_change_spot_type_button = True
        show_minus_live_button = True
        show_utilisation_button = True
        show_add_big_administrator_button = True
        show_add_little_administrator_button = True
        show_add_user = True

        show_change_lives_button = True
        show_add_user_button = True
        show_delete_user_button = True

        show_book_spot_button = True
        show_history_button = True
    elif user_role == ROLE_LITTLE_ADMINISTRATOR:
        show_change_lives_button = True
        show_add_user_button = True
        show_delete_user_button = True

        show_book_spot_button = True
        show_history_button = True
    elif user_role == ROLE_USER:
        show_book_spot_button = True
        show_history_button = True

    user_id = message.from_user.id
    requester = Employee.get_user_by_id(user_id)

    if requester is None:
        print("Ошибка")
        return 0

    current_date = date.today()
    current_time = datetime.now().time()

    await send_refusal_unauthorized(message)
    return 0

async def send_refusal_unauthorized(message: Message):
    await message.answer(UNKNOWN_USER_MESSAGE_1)


run_bot()