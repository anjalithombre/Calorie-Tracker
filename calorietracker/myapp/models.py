from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Food(models.Model):
    name = models.CharField(max_length=100, unique=True)

    # Nutrition fields
    calories = models.FloatField(null=True, blank=True, default=0)
    protein = models.FloatField(null=True, blank=True, default=0)
    fat = models.FloatField(null=True, blank=True, default=0)
    carbohydrates = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name



class Consume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_consumed = models.ForeignKey(Food, on_delete=models.CASCADE)
    consumed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} consumed {self.food_consumed.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    calories_goal = models.FloatField(default=2000)

    def __str__(self):
        return f"{self.user.username} Profile"


# ✅ Signal to auto-create or update UserProfile safely
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # use get_or_create to avoid errors if profile doesn't exist
        UserProfile.objects.get_or_create(user=instance)
        instance.userprofile.save()