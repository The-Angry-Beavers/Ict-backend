from typing import Final, final, override

from django.db import models


class FeatureParamModel(models.Model):
    class Meta:
        abstract = True


@final
class GenderEnum(models.TextChoices):
    MALE = "male", "Мужской"
    FEMALE = "female", "Женский"


@final
class ProductModel(models.Model):
    name = models.CharField(verbose_name="название")
    link = models.URLField(verbose_name="ссылка на продукт")

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "продукты"

    @override
    def __str__(self) -> str:
        return self.name


@final
class JobSphereModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")

    class Meta:
        verbose_name = "сфера деятельности"
        verbose_name_plural = "сферы деятельности"

    @override
    def __str__(self) -> str:
        return self.name


@final
class AgeGroupModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")

    class Meta:
        verbose_name = "возрастная группа"
        verbose_name_plural = "возрастные группы"

    @override
    def __str__(self) -> str:
        return self.name


@final
class SpriteModel(FeatureParamModel):
    image = models.FileField(upload_to="sprites", verbose_name="изображение")
    gender = models.CharField(
        max_length=8, choices=GenderEnum.choices, verbose_name="пол"
    )
    age_group = models.ForeignKey(
        to=AgeGroupModel, on_delete=models.PROTECT, verbose_name="возрастная группа"
    )

    class Meta:
        verbose_name = "спрайт"
        verbose_name_plural = "спрайты"


@final
class CityModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")

    class Meta:
        verbose_name = "город"
        verbose_name_plural = "города"

    @override
    def __str__(self) -> str:
        return self.name


@final
class FirstNameModel(FeatureParamModel):
    content = models.CharField(verbose_name="имя")
    gender = models.CharField(
        max_length=8, choices=GenderEnum.choices, verbose_name="пол"
    )

    class Meta:
        verbose_name = "имя"
        verbose_name_plural = "имена"

    @override
    def __str__(self) -> str:
        return self.content


@final
class LastNameModel(FeatureParamModel):
    content = models.CharField(verbose_name="фамилия")
    gender = models.CharField(
        max_length=8, choices=GenderEnum.choices, verbose_name="пол"
    )

    class Meta:
        verbose_name = "фамилия"
        verbose_name_plural = "фамилии"

    @override
    def __str__(self) -> str:
        return self.content


@final
class ReviewModel(models.Model):
    product = models.ForeignKey(
        to=ProductModel,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="продукт",
    )
    is_product_in_answer = models.BooleanField(
        choices=[
            (True, "Не нужен, но указали"),
            (False, "Нужен, но не указали"),
        ],
        blank=True,
        verbose_name="статус продукта в ответе",
    )
    text = models.TextField(verbose_name="текст отзыва")

    class Meta:
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"


@final
class HintModel(models.Model):
    product = models.ForeignKey(
        to=ProductModel, on_delete=models.PROTECT, verbose_name="продукт"
    )
    text = models.TextField(verbose_name="текст подсказки")

    class Meta:
        verbose_name = "подсказка"
        verbose_name_plural = "подсказки"


BOOL_CONDITION_CHOICES: Final[list[tuple[bool | None, str]]] = [
    (None, "Не важно"),
    (True, "Есть"),
    (False, "Нет"),
]


@final
class SituationModel(models.Model):
    male_text = models.TextField(verbose_name="текст для мужчин")
    female_text = models.TextField(verbose_name="текст для женщин")
    common_products = models.ManyToManyField(
        to=ProductModel, verbose_name="общие продукты"
    )

    real_estate_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
        blank=True,
        verbose_name="условие недвижимости",
    )
    allowed_age_groups = models.ManyToManyField(
        AgeGroupModel, verbose_name="доступные возрастные группы"
    )

    class Meta:
        verbose_name = "ситуация"
        verbose_name_plural = "ситуации"


@final
class ProductRecommendationConditionModel(models.Model):
    product = models.ForeignKey(
        to=ProductModel, on_delete=models.CASCADE, verbose_name="продукт"
    )
    situation = models.ForeignKey(
        to=SituationModel,
        on_delete=models.CASCADE,
        related_name="conditions",
        verbose_name="ситуация",
    )
    children_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
        blank=True,
        verbose_name="условие наличия детей",
    )
    real_estate_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
        blank=True,
        verbose_name="условие недвижимости",
    )
    age_group_condition = models.ForeignKey(
        to=AgeGroupModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="условие возрастной группы",
    )
    job_sphere_condition = models.ForeignKey(
        to=JobSphereModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="условие сферы деятельности",
    )
    city_condition = models.ForeignKey(
        to=CityModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="условие города",
    )

    class Meta:
        verbose_name = "условие рекомендации продукта"
        verbose_name_plural = "условия рекомендаций продуктов"


@final
class GenerationModel(models.Model):
    seed = models.UUIDField(verbose_name="сид")
    iteration = models.PositiveSmallIntegerField(verbose_name="итерация")

    situation = models.ForeignKey(
        to=SituationModel, on_delete=models.PROTECT, verbose_name="ситуация"
    )

    client_gender = models.CharField(
        max_length=8, choices=GenderEnum.choices, verbose_name="пол клиента"
    )
    client_age = models.ForeignKey(
        to=AgeGroupModel, on_delete=models.PROTECT, verbose_name="возраст клиента"
    )
    client_job = models.ForeignKey(
        to=JobSphereModel, on_delete=models.PROTECT, verbose_name="профессия клиента"
    )
    client_is_married = models.BooleanField(verbose_name="семейное положение")
    client_is_have_child = models.BooleanField(verbose_name="наличие детей")
    client_is_have_real_estate = models.BooleanField(
        verbose_name="наличие недвижимости"
    )
    client_city = models.ForeignKey(
        to=CityModel, on_delete=models.PROTECT, verbose_name="город клиента"
    )
    client_sprite = models.ForeignKey(
        to=SpriteModel, on_delete=models.PROTECT, verbose_name="спрайт клиента"
    )
    client_first_name = models.ForeignKey(
        to=FirstNameModel, on_delete=models.PROTECT, verbose_name="имя клиента"
    )
    client_last_name = models.ForeignKey(
        to=LastNameModel, on_delete=models.PROTECT, verbose_name="фамилия клиента"
    )

    hint = models.ForeignKey(
        to=HintModel, on_delete=models.PROTECT, verbose_name="подсказка"
    )

    class Meta:
        verbose_name = "генерация"
        verbose_name_plural = "генерации"
        unique_together = [("seed", "iteration")]


@final
class GenerationAnswerModel(models.Model):
    generation = models.ForeignKey(
        GenerationModel,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="генерация",
    )
    product = models.ForeignKey(
        to=ProductModel, on_delete=models.PROTECT, verbose_name="продукт"
    )
    is_correct = models.BooleanField(verbose_name="корректность")

    class Meta:
        verbose_name = "ответ генерации"
        verbose_name_plural = "ответы генераций"
