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
TEXT_CHANGE_SPOT_BUTTON = "Изм. тип парк. места"
TEXT_MINUS_LIVE_BUTTON = "Минусануть жизнь"
TEXT_UTILISATION_BUTTON = "Данные по утилизации"
TEXT_ADD_BIG_ADM_BUTTON = "Добавить бол. админа"
TEXT_LITTLE_ADM_BUTTON = "Добавить мал. админа"
TEXT_USER_BUTTON = "Добавить пользователя"

TEXT_CHANGE_LIVES_BUTTON = "Изменить количество жизней"
TEXT_DELETE_USER_BUTTON = "Удалить пользователя"

TEXT_BOOK_SPOT_BUTTON = "Забронировать место"
TEXT_HISTORY_BUTTON = "Показать историю"

START_MESSAGE = "Добрый день! Какой у Вас вопрос?"

bot: Bot = Bot(token=API_TOKEN)
dp: Dispatcher = Dispatcher()

def run_bot():
    print("Запускаю бота...")
    dp.run_polling(bot)


async def is_user_unauthorized(message: Message):
    authorized_ids = [employee.telegram_id for employee in Employee.select()]

    if message.from_user.id not in authorized_ids:
        return True
    return False


def create_start_menu_keyboard(
        is_show_change_spot_type_button: bool,
        is_show_minus_live_button: bool,
        is_show_utilisation_button: bool,
        is_show_add_big_administrator_button: bool = False,
        is_show_add_little_administrator_button: bool = False,
        is_show_add_user_button: bool = False,
        is_show_change_lives_button: bool = False,
        is_show_delete_user_button: bool = False,
        is_show_book_spot_button: bool = False,
        is_show_history_button: bool = False,
) -> ReplyKeyboardMarkup:
    """ Создаёт клавиатуру, которая будет выводиться на команду /start """

    change_spot_type_button: KeyboardButton = KeyboardButton(text=TEXT_CHANGE_SPOT_BUTTON)
    minus_live_button: KeyboardButton = KeyboardButton(text=TEXT_MINUS_LIVE_BUTTON)
    utilisation_button: KeyboardButton = KeyboardButton(text=TEXT_UTILISATION_BUTTON)
    add_big_administrator_button: KeyboardButton = KeyboardButton(text=TEXT_ADD_BIG_ADM_BUTTON)
    add_little_administrator_button: KeyboardButton = KeyboardButton(text=TEXT_LITTLE_ADM_BUTTON)
    add_user_button: KeyboardButton = KeyboardButton(text=TEXT_USER_BUTTON)

    change_lives_button: KeyboardButton = KeyboardButton(text=TEXT_CHANGE_LIVES_BUTTON)
    delete_user_button: KeyboardButton = KeyboardButton(text=TEXT_USER_BUTTON)

    book_spot_button: KeyboardButton = KeyboardButton(text=TEXT_BOOK_SPOT_BUTTON)
    history_button: KeyboardButton = KeyboardButton(text=TEXT_HISTORY_BUTTON)

    buttons_list = []

    """ 
    Каждый массив - один ряд кнопок.
    Чтобы кнопка была в отдельном ряду, необходимо, 
    чтобы каждая кнопка была в отдельном массиве 
    """

    if is_show_change_spot_type_button:
        buttons_list.append([change_spot_type_button])
    if is_show_minus_live_button:
        buttons_list.append([minus_live_button])
    if is_show_utilisation_button:
        buttons_list.append([utilisation_button])
    if is_show_add_big_administrator_button:
        buttons_list.append([add_big_administrator_button])
    if is_show_add_little_administrator_button:
        buttons_list.append([add_little_administrator_button])
    if is_show_add_user_button:
        buttons_list.append([add_user_button])
    if is_show_change_lives_button:
        buttons_list.append([change_lives_button])
    if is_show_delete_user_button:
        buttons_list.append([delete_user_button])
    if is_show_book_spot_button:
        buttons_list.append([book_spot_button])
    if is_show_history_button:
        buttons_list.append([history_button])

    """ Создаем объект клавиатуры, добавляя в него кнопки """
    keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=buttons_list,
        resize_keyboard=True
    )

    return keyboard


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
        await send_refusal_unauthorized(message)
        return 0

    """ Переменные, указывающие на то, какие кнопки меню будут доступны в дальнейшем """
    show_change_spot_type_button = False
    show_minus_live_button = False
    show_utilisation_button = False
    show_add_big_administrator_button = False
    show_add_little_administrator_button = False
    show_add_user_button = False

    show_change_lives_button = False
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
        show_add_user_button = True

        show_change_lives_button = True
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

    await state.clear()

    await message.answer(
        START_MESSAGE,
        reply_markup=create_start_menu_keyboard(
            show_change_spot_type_button,
            show_minus_live_button,
            show_utilisation_button,
            show_add_big_administrator_button,
            show_add_little_administrator_button,
            show_add_user_button,
            show_delete_user_button,
            show_history_button,
            show_change_lives_button,
            show_book_spot_button
        )
    )

    return 0

async def send_refusal_unauthorized(message: Message):
    await message.answer(UNKNOWN_USER_MESSAGE_1)


@dp.message(F.text == TEXT_BOOK_SPOT_BUTTON)
async def process_booking(message: Message):
    """ Обработчик запроса на бронирование парковочного места """

    if await is_user_unauthorized(message):
        await send_refusal_unauthorized(message)
        return 0

    user_id = message.from_user.id
    requester_id = message.from_user.id
    requester = Employee.get_user_by_id(requester_id)

    if requester is None:
        print("Ошибка")
        return 0

    """ Вычисление даты + 1 день (завтра) """
    current_date = date.today()
    checking_date = current_date + timedelta(days=1)

    reservations_by_user_count = Booking.select(Booking, Employee).join(Employee).where(
        Booking.employee == requester.id,
        Booking.employee.name == requester.first_name,
        Booking.date_reservation == checking_date
    ).count()

    if reservations_by_user_count > 0:
        await message.reply(
            text=f"У Вас уже есть забронированное место:",
            reply_markup=ReplyKeyboardRemove()
        )
        reserved_place = Booking.get(
            Booking.date_reservation == checking_date,
            Booking.employee == requester.id
        )
        await message.answer(
            text=f"Место: {reserved_place.parking_spot_id.name}, дата: {reserved_place.booking_date}"
        )
        return 0

    date_for_book = current_date + timedelta(days=1)
    available_spots = ParkingSpot.get_booking_options(date_for_book, requester.id)


run_bot()