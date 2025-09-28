from typing import TYPE_CHECKING, Self
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, computed_field

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
    sprite: str

    @classmethod
    def from_generation(cls, generation_instance: "GenerationModel") -> Self:
        data = {
            "gender": generation_instance.client_gender,
            "age": generation_instance.client_age.name,
            "job_sphere": generation_instance.client_job.name,
            "is_married": generation_instance.client_is_married,
            "is_have_child": generation_instance.client_is_have_child,
            "is_have_real_estate": generation_instance.client_is_have_real_estate,
            "city": generation_instance.client_city.name,
            "sprite": generation_instance.client_sprite.image.url,
            "message": generation_instance.situation.male_text
        }

        if generation_instance.client_gender == "female":
            data["message"] = generation_instance.situation.female_text

        return cls.model_validate(data)


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
        data = {
            "generation_params": GenerateSituationParams(
                seed=generation.seed,
                num_iterations=generation.iteration,
            ),
            "client": Client.from_generation(generation),
            "answers": [
                SituationAnswer.model_validate(ans, from_attributes=True)
                for ans in generation.answers.all()
            ],
        }

        return cls.model_validate(data)


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
    rating: int


class AcknowledgeDayFinishResponse(BaseModel):
    reviews: list[Review]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def total_rating(self) -> int:
        return sum([rev.rating for rev in self.reviews])


class SituationHint(BaseModel):
    product: Product
    text: str
