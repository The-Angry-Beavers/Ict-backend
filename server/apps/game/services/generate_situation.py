from typing import Self, Final, Sequence, TypeVar

from django.db.models import Prefetch, QuerySet

from server.apps.game.admin import SpriteModelAdmin
from server.apps.game.models import (
    SituationModel,
    ProductRecommendationConditionModel,
    AgeGroupModel,
    FeatureParamModel,
    CityModel,
    JobSphereModel,
    SpriteModel,
)
from server.apps.game.services.dto import Situation, GenerateSituationParams, Client
import random
import dataclasses


@dataclasses.dataclass
class Generation:
    """
    Набор случайных чисел для определения генерации
    """

    situation: float
    gender: float
    job: float
    age: float
    is_married: float
    is_have_child: float
    is_have_real_estate: float
    city: float
    sprite: float

    correct_answers_num: int
    answers: list[float]

    @classmethod
    def generate(cls, random_instance: random.Random) -> Self:
        return cls(
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.random(),
            random_instance.randint(1, 3),
            [random_instance.random() for _ in range(4)],
        )


def _get_random_instance(generation_params: GenerateSituationParams) -> random.Random:
    return random.Random(str(generation_params.seed))


def get_generation(generation_params: GenerateSituationParams) -> Generation:
    random_instance = _get_random_instance(generation_params)

    for _ in range(generation_params.num_iterations - 1):
        Generation.generate(random_instance)

    return Generation.generate(random_instance)


def _get_index_from_random_val(val: float, num_features: int) -> int:
    return int(val * num_features)


FeatureT = TypeVar("FeatureT", bound=FeatureParamModel)


def get_value_from_feature_params(
    feature_qs: QuerySet[FeatureT], val: float
) -> FeatureT:
    feature_count = feature_qs.count()
    index = _get_index_from_random_val(val, feature_count)
    return feature_qs[index]


GENDERS: Final[tuple[str, ...]] = ("male", "female")


def _get_client(situation: SituationModel, generation: Generation) -> Client:
    selected_gender = GENDERS[_get_index_from_random_val(generation.gender, 2)]
    selected_age_group = get_value_from_feature_params(
        AgeGroupModel.objects.all(), generation.age
    )
    selected_city = get_value_from_feature_params(
        CityModel.objects.all(), generation.city
    )
    selected_job = get_value_from_feature_params(
        JobSphereModel.objects.all(), generation.job
    )
    selected_sprite = get_value_from_feature_params(
        SpriteModel.objects.filter(
            gender=selected_gender,
            age_group=selected_age_group,
        ),
        generation.sprite,
    )
    is_maried = bool(_get_index_from_random_val(generation.is_married, 2))
    is_have_child = bool(_get_index_from_random_val(generation.is_married, 2))
    is_have_real_estate = situation.real_estate_condition
    if situation.real_estate_condition is None:
        is_have_real_estate = bool(_get_index_from_random_val(generation.is_married, 2))

    message = situation.male_text

    if selected_gender == "female":
        message = situation.female_text

    return Client(
        gender=selected_gender,
        age=selected_age_group.name,
        job_sphere=selected_job.name,
        is_maried=is_maried,
        is_have_child=is_have_child,
        is_have_real_estate=is_have_real_estate,
        city=selected_city.name,
        message=message,
        sprite=selected_sprite.image.url,
    )


def generate_situation(
    generation_params: GenerateSituationParams,
) -> Situation:
    generation = get_generation(generation_params)

    situation_count = SituationModel.objects.count()
    situation_id = _get_index_from_random_val(generation.situation, situation_count)
    situation = SituationModel.objects.prefetch_related(
        Prefetch(
            "conditions",
            queryset=ProductRecommendationConditionModel.objects.select_related(
                "product",
                "situation",
                "age_group_condition",
                "job_sphere_condition",
                "city_condition",
            ),
        )
    ).get(pk=situation_id)

    generated_client = _get_client(situation, generation)

