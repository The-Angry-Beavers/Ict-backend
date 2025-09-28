from typing import TYPE_CHECKING, Self
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field

if TYPE_CHECKING:
    from server.apps.game.models import GenerationModel


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

    @classmethod
    def from_generation_model(cls, generation: "GenerationModel") -> Self:
        raise NotImplementedError


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
