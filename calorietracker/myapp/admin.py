from django.contrib import admin
from .models import Food, Consume, UserProfile


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ("name", "calories", "protein", "fat", "carbohydrates")
    search_fields = ("name",)


@admin.register(Consume)
class ConsumeAdmin(admin.ModelAdmin):
    list_display = ("user", "food_consumed", "consumed_at")
    list_filter = ("user", "consumed_at")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "calories_goal")