from server.apps.game.models import (
    ProductModel,
    JobSphereModel,
    SpriteModel,
    AgeGroupModel,
    CityModel,
    ReviewModel,
    HintModel,
    SituationModel,
    ProductRecommendationModel,
)
from django.contrib import admin


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    pass


@admin.register(JobSphereModel)
class JobSphereModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SpriteModel)
class SpriteModelAdmin(admin.ModelAdmin):
    pass


@admin.register(AgeGroupModel)
class AgeGroupModelAdmin(admin.ModelAdmin):
    pass


@admin.register(CityModel)
class CityModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    pass


@admin.register(HintModel)
class HintModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SituationModel)
class SituationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductRecommendationModel)
class ProductRecommendationModelAdmin(admin.ModelAdmin):
    pass
