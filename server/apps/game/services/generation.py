import dataclasses
import itertools
import random
from typing import Final, Self, TypeVar

from django.db.models import Prefetch, QuerySet, Q, Model

from server.apps.game.models import (
    AgeGroupModel,
    CityModel,
    GenerationModel,
    HintModel,
    JobSphereModel,
    ProductModel,
    ProductRecommendationConditionModel,
    SituationModel,
    SpriteModel,
    GenerationAnswerModel,
    ReviewModel,
    FirstNameModel,
    LastNameModel,
)
from server.apps.game.services.dto import (
    GenerateSituationParams,
    AcknowledgeDayFinish,
    AcknowledgeDayFinishResponse,
    Review,
    Client,
)

TOTAL_POINTS: Final[int] = 10
INCORRECT_ANSWER_FINE: Final[int] = 3
GENDERS: Final[tuple[str, ...]] = ("male", "female")
TOTAL_ANSWERS_COUNT: Final[int] = 4


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
    hint: float
    review: float
    first_name: float
    last_name: float

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


ModelT = TypeVar("ModelT", bound=Model)


def get_random_value_from_qs(feature_qs: QuerySet[ModelT], val: float) -> ModelT:
    feature_count = feature_qs.count()
    index = _get_index_from_random_val(val, feature_count)
    return feature_qs[index]


@dataclasses.dataclass
class ClientGeneration:
    client_gender: str
    client_age: AgeGroupModel
    client_job: JobSphereModel
    client_is_married: bool
    client_is_have_child: bool
    client_is_have_real_estate: bool
    client_city: CityModel
    client_sprite: SpriteModel
    client_first_name: FirstNameModel
    client_last_name: LastNameModel


def _get_client(situation: SituationModel, generation: Generation) -> ClientGeneration:
    selected_gender = GENDERS[_get_index_from_random_val(generation.gender, 2)]
    selected_age_group = get_random_value_from_qs(
        AgeGroupModel.objects.all(), generation.age
    )
    selected_city = get_random_value_from_qs(CityModel.objects.all(), generation.city)
    selected_job = get_random_value_from_qs(
        JobSphereModel.objects.all(), generation.job
    )
    selected_sprite = get_random_value_from_qs(
        SpriteModel.objects.filter(
            gender=selected_gender,
            age_group=selected_age_group,
        ),
        generation.sprite,
    )
    is_married = bool(_get_index_from_random_val(generation.is_married, 2))
    is_have_child = bool(_get_index_from_random_val(generation.is_married, 2))
    is_have_real_estate = situation.real_estate_condition
    if is_have_real_estate is None:
        is_have_real_estate = bool(_get_index_from_random_val(generation.is_married, 2))

    selected_first_name = get_random_value_from_qs(
        FirstNameModel.objects.filter(gender=selected_gender),
        generation.first_name,
    )
    selected_last_name = get_random_value_from_qs(
        LastNameModel.objects.filter(gender=selected_gender),
        generation.last_name,
    )

    return ClientGeneration(
        client_gender=selected_gender,
        client_age=selected_age_group,
        client_job=selected_job,
        client_is_married=is_married,
        client_is_have_child=is_have_child,
        client_is_have_real_estate=is_have_real_estate,
        client_city=selected_city,
        client_sprite=selected_sprite,
        client_first_name=selected_first_name,
        client_last_name=selected_last_name,
    )


def _is_client_satisfy_condition(
    client: ClientGeneration,
    cond: ProductRecommendationConditionModel,
) -> bool:

    conditions = []

    # TODO: Подумать упаковать эти условия как-то более атомарно
    if cond.children_condition is not None:
        conditions.append(client.client_is_have_child == cond.children_condition)

    if cond.real_estate_condition is not None:
        conditions.append(
            client.client_is_have_real_estate == cond.real_estate_condition
        )

    if cond.age_group_condition is not None:
        conditions.append(client.client_age == cond.age_group_condition)

    if cond.job_sphere_condition is not None:
        conditions.append(client.client_job == cond.job_sphere_condition)

    if cond.city_condition is not None:
        conditions.append(client.client_city == cond.city_condition)

    return all(conditions)


@dataclasses.dataclass
class AnswerGeneration:
    correct_answers: list[ProductModel]
    incorrect_answers: list[ProductModel]


def _resolve_duplicate_indices(indices: list[int], _len: int) -> list[int]:
    if len(set(indices)) > _len:
        raise ValueError("Can not resolve indices")

    result = []
    used_indices = set()

    for index in indices:
        current_index = index
        while current_index in used_indices:
            current_index = (current_index + 1) % _len
        used_indices.add(current_index)
        result.append(current_index)

    return result


def _get_answers(
    situation: SituationModel,
    generation: Generation,
    generated_client: ClientGeneration,
) -> AnswerGeneration:
    correct_products_set = set(situation.common_products.all())

    for cond in situation.conditions.all():
        if _is_client_satisfy_condition(generated_client, cond):
            correct_products_set.add(cond.product)

    correct_product_list = list(correct_products_set)
    other_products_qs = ProductModel.objects.exclude(
        id__in=[_.id for _ in correct_product_list]
    )

    # Сколько можем в сумме выдать правильных ответов.
    count_correct_answers = (
        len(correct_product_list)
        if len(correct_product_list) < generation.correct_answers_num
        else generation.correct_answers_num
    )

    true_answers_indices = [
        _get_index_from_random_val(
            val,
            len(correct_product_list),
        )
        for val in generation.answers[:count_correct_answers]
    ]
    true_answers_indices = _resolve_duplicate_indices(
        true_answers_indices, len(correct_product_list)
    )

    false_answers_indices = [
        _get_index_from_random_val(val, other_products_qs.count())
        for val in generation.answers[count_correct_answers:]
    ]
    false_answers_indices = _resolve_duplicate_indices(
        false_answers_indices, other_products_qs.count()
    )

    true_answers = [correct_product_list[idx] for idx in true_answers_indices]
    false_answers = [other_products_qs[idx] for idx in false_answers_indices]

    return AnswerGeneration(
        correct_answers=true_answers,
        incorrect_answers=false_answers,
    )


@dataclasses.dataclass
class HintGeneration:
    hint: HintModel


def _get_hint(
    generation: Generation, generated_answers: AnswerGeneration
) -> HintGeneration:
    answer_index = _get_index_from_random_val(
        generation.hint, generation.correct_answers_num
    )
    product_to_hint = generated_answers.correct_answers[answer_index]
    hint_qs = HintModel.objects.filter(product=product_to_hint)
    return HintGeneration(hint=get_random_value_from_qs(hint_qs, generation.hint))


def _generate_situation(
    generation_params: GenerateSituationParams,
) -> GenerationModel:
    generation = get_generation(generation_params)

    situation_count = SituationModel.objects.count()
    # TODO: Подумать над этой семантикой как-то по-другому
    # Чисто в теории семантика индексов удобная, но ебучая пиздц...
    situation_index = _get_index_from_random_val(generation.situation, situation_count)
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
    )[situation_index]

    generated_client = _get_client(
        situation,
        generation,
    )
    generated_answers = _get_answers(
        situation,
        generation,
        generated_client,
    )
    generated_hint = _get_hint(
        generation,
        generated_answers,
    )

    generation_instance = GenerationModel.objects.create(
        seed=generation_params.seed,
        iteration=generation_params.num_iterations,
        situation=situation,
        **dataclasses.asdict(generated_client),
        **dataclasses.asdict(generated_hint),
    )
    GenerationAnswerModel.objects.bulk_create(
        itertools.chain(
            [
                GenerationAnswerModel(
                    generation=generation_instance,
                    product=product,
                    is_correct=True,
                )
                for product in generated_answers.correct_answers
            ],
            [
                GenerationAnswerModel(
                    generation=generation_instance,
                    product=product,
                    is_correct=False,
                )
                for product in generated_answers.incorrect_answers
            ],
        )
    )

    return generation_instance


def _fetch_generation(generation_params: GenerateSituationParams) -> GenerationModel:
    return (
        GenerationModel.objects.select_related(
            "situation",
            "client_age",
            "client_job",
            "client_city",
            "client_sprite",
            "hint",
        )
        .prefetch_related(
            Prefetch(
                "answers",
                GenerationAnswerModel.objects.select_related("product"),
            )
        )
        .get(
            seed=generation_params.seed,
            iteration=generation_params.num_iterations,
        )
    )


def generate_situation(generation_params: GenerateSituationParams) -> GenerationModel:
    try:
        return _fetch_generation(generation_params)
    except GenerationModel.DoesNotExist:
        _generate_situation(generation_params)
        return _fetch_generation(generation_params)


def get_hint(generation_params: GenerateSituationParams) -> HintModel:
    generation_instance = generate_situation(generation_params)
    return generation_instance.hint


def check_answers(
    generation_instance: GenerationModel,
    chosen_product_ids: list[int],
) -> Review:
    # Реализовывается не методами, так как создание нового кверисета ведет
    # к еще одному запросу к бд, что нам не особо хочется делать
    correct_generated_answers = list(
        filter(
            lambda ans: ans.is_correct,
            generation_instance.answers.all(),
        )
    )

    points_per_answer = TOTAL_POINTS // len(correct_generated_answers)
    correct_product_ids = set([ans.product_id for ans in correct_generated_answers])
    answered_product_ids = set(chosen_product_ids)

    correct_answers = correct_product_ids & answered_product_ids
    incorrect_answers = answered_product_ids - correct_product_ids
    lost_correct_answers = correct_product_ids - answered_product_ids

    points_for_correct_answers = len(correct_answers) * points_per_answer
    points_for_incorrect_answers = len(incorrect_answers) * INCORRECT_ANSWER_FINE
    total_points = abs(points_for_correct_answers - points_for_incorrect_answers)

    q_object = Q(product_id__in=correct_product_ids)

    # нет потерянных ответов и неправильных -> идеальный ответ
    if len(incorrect_answers) == 0 and len(lost_correct_answers) == 0:
        q_object = Q(product__isnull=True)

    #  Есть какой-то продукт, который не нужен
    if len(incorrect_answers):
        q_object |= Q(is_product_in_answer=True)

    # Есть какой-то потерянный правильный ответ
    if len(lost_correct_answers):
        q_object |= Q(is_product_in_answer=False)

    review_qs = ReviewModel.objects.filter(q_object)
    random_instance = _get_random_instance(
        GenerateSituationParams(
            seed=generation_instance.seed,
            num_iterations=generation_instance.iteration,
        )
    )
    generation = Generation.generate(random_instance)
    review_instance = get_random_value_from_qs(review_qs, generation.review)

    return Review(
        client=Client.from_generation(generation_instance),
        review=review_instance.text,
        rating=total_points,
    )


def acknowledge_day_finish(data: AcknowledgeDayFinish) -> AcknowledgeDayFinishResponse:

    generation_qs = GenerationModel.objects.prefetch_related(
        Prefetch(
            "answers",
            GenerationAnswerModel.objects.select_related("product"),
        )
    ).filter(seed=data.seed)
    generation_by_iteration = {gen.iteration: gen for gen in generation_qs}
    reviews = []
    for ans in data.answers:
        generation_instance = generation_by_iteration.get(ans.iteration)
        if generation_instance is None:
            generation_instance = generate_situation(
                GenerateSituationParams(
                    seed=data.seed,
                    num_iterations=ans.iteration,
                )
            )

        reviews.append(
            check_answers(
                generation_instance,
                ans.recommended_product_ids,
            )
        )

    return AcknowledgeDayFinishResponse(reviews=reviews)
