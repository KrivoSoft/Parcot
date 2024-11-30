import yaml
from peewee import *

""" Получаем данные из файла настроек """
with open('settings.yml', 'r', encoding='utf-8') as file:
    CONSTANTS = yaml.safe_load(file)

db_name = CONSTANTS['DB_NAME']

db = SqliteDatabase(db_name)

class BaseModel(Model):
    class Meta:
        database = db


class ParkingSpotType(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'parking_spot_types'


class BookingType(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'booking_types'


class Department(BaseModel):
    name = CharField()

    class Meta:
        table_name = 'departments'


class Employee(BaseModel):
    name = CharField()
    phone = CharField()
    department =  ForeignKeyField(Department, backref="department_id")
    role = CharField()

    class Meta:
        table_name = 'employees'


class Transport(BaseModel):
    model_name = CharField()
    registration_number = CharField()
    employee = ForeignKeyField(Employee, backref="employee_id")

    class Meta:
        table_name = 'transports'


class ParkingSpot(BaseModel):
    name = CharField()
    type_of_spot = ForeignKeyField(ParkingSpotType, backref="type_id")
    department = ForeignKeyField(Department, backref="department_id")
    type_of_booking = ForeignKeyField(BookingType, backref="booking_type_id")

    class Meta:
        table_name = 'parking_spots'


class Booking(BaseModel):
    parking_spot = ForeignKeyField(ParkingSpot, backref="spot_id")
    date_reservation = DateField()

    class Meta:
        table_name = 'bookings'