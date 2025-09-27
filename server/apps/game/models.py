from typing import Final, final

from django.db import models


@final
class GenderEnum(models.TextChoices):
    MALE = "male", "Мужской"
    FEMALE = "female", "Женский"


@final
class ProductModel(models.Model):
    name = models.CharField(verbose_name="название")
    link = models.URLField(verbose_name="ссылка на продукт")


@final
class JobSphereModel(models.Model):
    name = models.CharField(verbose_name="название")


@final
class SpriteModel(models.Model):
    image = models.FileField(upload_to="sprites")


@final
class AgeGroupModel(models.Model):
    name = models.CharField(verbose_name="название")


@final
class CityModel(models.Model):
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


@final
class SituationModel(models.Model):
    male_text = models.TextField()
    female_text = models.TextField()


BOOL_CONDITION_CHOICES: Final[list[tuple[bool | None, str]]] = [
    (None, "Не важно"),
    (True, "Есть"),
    (False, "Нет"),
]


@final
class ProductRecommendationModel(models.Model):

    situations = models.ForeignKey(
        to=SituationModel,
        on_delete=models.PROTECT,
    )
    children_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
    )
    real_estate_condition = models.BooleanField(
        null=True,
        choices=BOOL_CONDITION_CHOICES,
    )
    age_groups_condition = models.ManyToManyField(to=AgeGroupModel)
    job_spheres_condition = models.ManyToManyField(to=JobSphereModel)
    cities_condition = models.ManyToManyField(to=CityModel)

    products = models.ManyToManyField(to=ProductModel)
