from typing import Final, final

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


@final
class JobSphereModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")


@final
class AgeGroupModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")


@final
class SpriteModel(FeatureParamModel):
    image = models.FileField(upload_to="sprites")

    gender = models.CharField(max_length=8, choices=GenderEnum.choices)
    age_group = models.ForeignKey(
        to=AgeGroupModel,
        on_delete=models.PROTECT,
    )


@final
class CityModel(FeatureParamModel):
    name = models.CharField(verbose_name="название")


@final
class ReviewModel(models.Model):
    product = models.ForeignKey(
        to=ProductModel,
        on_delete=models.PROTECT,
    )
    is_positive = models.BooleanField(default=False)
    text = models.TextField()


@final
class HintModel(models.Model):
    product = models.ForeignKey(
        to=ProductModel,
        on_delete=models.PROTECT,
    )
    text = models.TextField()


BOOL_CONDITION_CHOICES: Final[list[tuple[bool | None, str]]] = [
    (None, "Не важно"),
    (True, "Есть"),
    (False, "Нет"),
]


@final
class SituationModel(models.Model):
    male_text = models.TextField()
    female_text = models.TextField()
    common_products = models.ManyToManyField(to=ProductModel)

    real_estate_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
    )


@final
class ProductRecommendationConditionModel(models.Model):

    product = models.ForeignKey(
        to=ProductModel,
        on_delete=models.CASCADE,
    )
    situation = models.ForeignKey(
        to=SituationModel,
        on_delete=models.CASCADE,
        related_name="conditions",
    )
    children_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
    )
    real_estate_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
    )
    age_group_condition = models.ForeignKey(
        to=AgeGroupModel, on_delete=models.CASCADE, null=True
    )
    job_sphere_condition = models.ForeignKey(
        to=JobSphereModel, on_delete=models.CASCADE, null=True
    )
    city_condition = models.ForeignKey(
        to=CityModel, on_delete=models.CASCADE, null=True
    )


class GenerationModel(models.Model):
    seed = models.UUIDField()
    iteration = models.PositiveSmallIntegerField()

    situation = models.ForeignKey(to=SituationModel, on_delete=models.PROTECT)

    client_gender = models.CharField(max_length=8, choices=GenderEnum.choices)
    client_age = models.ForeignKey(to=AgeGroupModel, on_delete=models.PROTECT)
    client_job = models.ForeignKey(to=JobSphereModel, on_delete=models.PROTECT)
    client_is_married = models.BooleanField()
    client_is_have_child = models.BooleanField()
    client_is_have_real_estate = models.BooleanField()
    client_city = models.ForeignKey(to=CityModel, on_delete=models.PROTECT)
    client_sprite = models.ForeignKey(to=SpriteModel, on_delete=models.PROTECT)

    hint = models.ForeignKey(to=HintModel, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("seed", "iteration")


# Нужна для того чтобы при изменении условий, генерация не изменялась.
# Более элегантного решения я не придумал...
class GenerationAnswerModel(models.Model):
    generation = models.ForeignKey(
        GenerationModel,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    product = models.ForeignKey(to=ProductModel, on_delete=models.PROTECT)
    is_correct = models.BooleanField()
