from model import *
import yaml

""" Получаем данные из файла настроек """
with open('settings.yml', 'r', encoding='utf-8') as file:
    CONSTANTS = yaml.safe_load(file)

db_name = CONSTANTS['DB_NAME']

def create_tables() -> None:
    """ Создание таблиц при создании новой БД """
    db.connect()
    db.create_tables([ParkingSpot, ParkingSpotType, BookingType, Department, Employee, Transport, ParkingSpot, Booking])

create_tables()