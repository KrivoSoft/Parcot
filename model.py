from datetime import date
from typing import Optional
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
    lives = IntegerField()
    telegram_id = IntegerField(null=False)

    class Meta:
        table_name = 'employees'

    @staticmethod
    def get_user_by_id(the_user_id_i_want: int):
        """ Функция, возвращающая нужного пользователя по его telegram id из БД """
        query: ModelSelect = Employee.select().where(Employee.telegram_id == the_user_id_i_want)

        if len(query) == 0:
            return None
        else:
            return query[0]

    @staticmethod
    def get_user_role(user_telegram_id) -> Optional[str]:
        user = Employee.get_user_by_id(user_telegram_id)
        if user is None:
            return None
        return user.role


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

    @staticmethod
    def get_booking_options(date_for_book: date, employee_id: Employee):
        """ Функция, получающая доступные для бронирования варианты """

        available_spots_for_book = []

        employee = Employee.select().where(
            Employee.id == employee_id
        )

        if employee.count() < 1:
            print("Не нашёл такого пользователя с id", employee_id)
            return 0

        emp_department = Department.select().where(
            Department.id == employee.department
        )

        if emp_department.count() < 1:
            print("Не нашёл такой департамент", employee.department)
            return 0

        all_spots = ParkingSpot.select().where(
            ParkingSpot.department == emp_department
        )

        # for one_spot in all_spots:
        #     if one_spot.is_spot_free(date_for_book):
        #         available_spots_for_book.append(one_spot)

        return available_spots_for_book


class Booking(BaseModel):
    parking_spot = ForeignKeyField(ParkingSpot, backref="spot_id")
    date_reservation = DateField()
    is_morning = BooleanField()
    employee = ForeignKeyField(Employee, backref="employee_id")

    class Meta:
        table_name = 'bookings'


class Guest(BaseModel):
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    telegram_id = IntegerField(null=False)

    class Meta:
        table_name = 'guests'

    def __repr__(self):
        return " ".join([str(self.username), str(self.first_name), str(self.last_name)])

    def __str__(self):
        return " ".join([str(self.username), str(self.first_name), str(self.last_name)])

    def delete_guest(self) -> bool:
        is_success = True

        try:
            guest = Guest.get(Guest.id == self.id)
            guest.delete_instance()
        except Exception:
            is_success = False

        return is_success