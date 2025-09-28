from django.contrib import admin

from server.apps.game.models import (
    AgeGroupModel,
    CityModel,
    HintModel,
    JobSphereModel,
    ProductModel,
    ReviewModel,
    SituationModel,
    SpriteModel,
    ProductRecommendationConditionModel,
)


class HintInline(admin.StackedInline):
    model = HintModel
    extra = 0


class ReviewInline(admin.StackedInline):
    model = ReviewModel
    extra = 0


class ProductRecommendationConditionInline(admin.StackedInline):
    model = ProductRecommendationConditionModel
    extra = 0


@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    inlines = [HintInline, ReviewInline]


@admin.register(JobSphereModel)
class JobSphereModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(SpriteModel)
class SpriteModelAdmin(admin.ModelAdmin):
    list_display = ["gender", "age_group"]


@admin.register(AgeGroupModel)
class AgeGroupModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(CityModel)
class CityModelAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(ReviewModel)
class ReviewModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "is_product_in_answer",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product")


@admin.register(HintModel)
class HintModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SituationModel)
class SituationModelAdmin(admin.ModelAdmin):
    inlines = [ProductRecommendationConditionInline]


# @admin.register(ProductRecommendationModel)
# class ProductRecommendationModelAdmin(admin.ModelAdmin):
#     pass
