from django.contrib import admin
from nltk import Model

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
    FirstNameModel,
    LastNameModel,
)


class ModelAdmin(admin.ModelAdmin):

    def log_deletion(self, request, obj, object_repr):
        pass

    def log_addition(self, request, obj, message):
        pass

    def log_change(self, request, obj, message):
        pass

    def log_deletions(self, request, queryset):
        pass


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
class ProductModelAdmin(ModelAdmin):
    list_display = ["id", "name"]
    inlines = [HintInline, ReviewInline]


@admin.register(JobSphereModel)
class JobSphereModelAdmin(ModelAdmin):
    list_display = ["id", "name"]


@admin.register(SpriteModel)
class SpriteModelAdmin(ModelAdmin):
    list_display = ["gender", "age_group"]


@admin.register(AgeGroupModel)
class AgeGroupModelAdmin(ModelAdmin):
    list_display = ["id", "name"]


@admin.register(CityModel)
class CityModelAdmin(ModelAdmin):
    list_display = ["id", "name"]


@admin.register(ReviewModel)
class ReviewModelAdmin(ModelAdmin):
    list_display = [
        "id",
        "product",
        "is_product_in_answer",
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("product")


@admin.register(HintModel)
class HintModelAdmin(ModelAdmin):
    pass


@admin.register(SituationModel)
class SituationModelAdmin(ModelAdmin):
    inlines = [ProductRecommendationConditionInline]


# @admin.register(ProductRecommendationModel)
# class ProductRecommendationModelAdmin(admin.ModelAdmin):
#     pass


@admin.register(FirstNameModel)
class FirstNameModelAdmin(ModelAdmin):
    list_display = ["content"]


@admin.register(LastNameModel)
class LastNameModelAdmin(ModelAdmin):
    list_display = ["content"]
