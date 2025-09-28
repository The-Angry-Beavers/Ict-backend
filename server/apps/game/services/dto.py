import enum
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field


# class GenderEnum(enum.StrEnum):
#     MALE = enum.auto()
#     FEMALE = enum.auto()
#
#
# class JobSphereEnum(enum.StrEnum):
#     IT = enum.auto()
#     FINANCES = enum.auto()
#     AGROCULTURE = enum.auto()
#     CONSTRUCTION = enum.auto()
#     EDUCATION = enum.auto()
#     HEALTHCARE = enum.auto()
#
#
# class CityEnum(enum.StrEnum):
#     MOSCOW = "Москва"
#     NIZHNY_NOVGOROD = "Нижний Новгород"
#     SAINT_PETERSBURG = "Санкт-Петербург"
#     VOLOGDA = "Вологда"
#     OBNINSK = "Обнинск"
#     KALUGA = "Калуга"
#     SOCHI = "Сочи"
#     KAZAN = "Казань"
#     EKATERINBURG = "Екатеринбург"
#     ORENBURG = "Оренгбург"
#     SAMARA = "Самара"
#     KHABAROVSK = "Хабаровск"
#     YUZHNO_SAKHALINSK = "Южно-Сахалинск"


# class AgeEnum(enum.StrEnum):
#     YOUNG = enum.auto()
#     AVERAGE = enum.auto()
#     RETIRED = enum.auto()
#

class Client(BaseModel):
    gender: str
    age: str
    job_sphere: str
    is_married: bool
    is_have_child: bool
    is_have_real_estate: bool
    city: str
    message: str
    sprite: AnyHttpUrl


class Product(BaseModel):
    id: int
    name: str = Field(description="Наименование продукта")
    link: AnyHttpUrl = Field(description="Ссылка на продукт")


class GenerateSituationParams(BaseModel):
    seed: UUID = Field(description="Сид ранддомной генерации.")
    num_iterations: int = Field(
        description="Какая по счету генерация (порядковый номер клиента)"
    )


class SituationAnswer(BaseModel):
    product: Product
    is_correct: bool


class Situation(BaseModel):
    generation_params: GenerateSituationParams = Field(
        description="Используемые параметры генерации"
    )
    client: Client = Field(description="Уникальная генерация клиента")
    answers: list[SituationAnswer] = Field(
        description="Варианты продуктов к рекоммендации"
    )


class ValidateSituationAnswer(BaseModel):
    generation_params: GenerateSituationParams
    recommended_product_id: int


class ValidateStuationAnswerResponse(BaseModel):
    is_success: bool


class AcknowledgeSituationAnswer(BaseModel):
    iteration: int = Field(description="Номер итерации (Порядковый номер клиента)")
    recommended_product_ids: list[int] = Field(description="Рекомендованные ID товаров")


class AcknowledgeDayFinish(BaseModel):
    seed: UUID = Field(description="Семя генерации для текущего дня")
    answers: list[AcknowledgeSituationAnswer]


class Review(BaseModel):
    client: Client
    review: str
    is_success: bool


class AcknowledgeDayFinishResponse(BaseModel):
    total_rating: int
    reviews: list[Review]


class SituationHint(BaseModel):
    product: Product
    text: str
