from django.shortcuts import render, redirect, get_object_or_404
from .models import Food, Consume, UserProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
from django.utils.timezone import now, timedelta, localdate
from django.http import HttpResponse
from django.template.loader import get_template
import io
from xhtml2pdf import pisa
import requests
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db import IntegrityError


# ---------------------------
# Helper function for API call
# ---------------------------
def get_food_nutrition(food_name):
    """
    Fetch nutrition data from Open Food Facts API by food name.
    Returns dict with carbs, protein, fat, calories.
    """
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": food_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("products"):
        product = data["products"][0]
        nutrients = product.get("nutriments", {})
        return {
            "carbs": nutrients.get("carbohydrates_100g", 0),
            "protein": nutrients.get("proteins_100g", 0),
            "fat": nutrients.get("fat_100g", 0),
            "calories": nutrients.get("energy-kcal_100g", 0),
        }
    return None


# ---------------------------
# Views
# ---------------------------

@login_required
def index(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    calories_goal = user_profile.calories_goal

    if request.method == "POST":
        food_consumed_name = request.POST.get('food_consumed')
        if food_consumed_name:
            food_obj, created = Food.objects.get_or_create(name=food_consumed_name)
            if created or not food_obj.calories:
                nutrition = get_food_nutrition(food_consumed_name)
                if nutrition:
                    food_obj.calories = nutrition["calories"]
                    food_obj.protein = nutrition["protein"]
                    food_obj.fat = nutrition["fat"]
                    food_obj.carbohydrates = nutrition["carbs"]
                    food_obj.save()
            Consume.objects.create(user=request.user, food_consumed=food_obj)

    foods = Food.objects.all()
    today = localdate()
    consumed_food = Consume.objects.filter(user=request.user, consumed_at__date=today)

    return render(request, 'myapp/index_fixed2.html', {
        'calories_goal': calories_goal,
        'foods': foods,
        'consumed_food': consumed_food
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'myapp/register.html', {'form': form})


def report(request):
    user = request.user
    today = now().date()
    month_ago = today - timedelta(days=30)

    day_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        day=TruncDay('consumed_at')).values('day').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('day')

    week_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        week=TruncWeek('consumed_at')).values('week').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('week')

    month_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        month=TruncMonth('consumed_at')).values('month').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('month')

    context = {
        'day_data': day_data,
        'week_data': week_data,
        'month_data': month_data,
    }
    return render(request, 'myapp/report.html', context)


def report_pdf(request):
    user = request.user
    today = now().date()
    month_ago = today - timedelta(days=30)

    day_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        day=TruncDay('consumed_at')).values('day').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('day')

    week_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        week=TruncWeek('consumed_at')).values('week').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('week')

    month_data = Consume.objects.filter(user=user, consumed_at__date__gte=month_ago).annotate(
        month=TruncMonth('consumed_at')).values('month').annotate(
        total_calories=Sum('food_consumed__calories'),
        total_protein=Sum('food_consumed__protein'),
        total_fat=Sum('food_consumed__fat'),
        total_carbs=Sum('food_consumed__carbohydrates')
    ).order_by('month')

    context = {
        'day_data': day_data,
        'week_data': week_data,
        'month_data': month_data,
    }

    template_path = 'myapp/report_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode('UTF-8')), dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def add_item(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            food_obj, created = Food.objects.get_or_create(name=name)
            if created or not food_obj.calories:
                nutrition = get_food_nutrition(name)
                if nutrition:
                    food_obj.calories = float(nutrition["calories"])
                    food_obj.protein = float(nutrition["protein"])
                    food_obj.fat = float(nutrition["fat"])
                    food_obj.carbohydrates = float(nutrition["carbs"])
                    food_obj.save()
            else:
                return render(request, 'myapp/add_item.html', {
                    "error": f"Food '{name}' already exists."
                })
            return redirect('index')
    return render(request, 'myapp/add_item.html')


def set_goal(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    if request.method == "POST":
        calories_goal = request.POST.get('calories_goal')
        if calories_goal:
            user_profile.calories_goal = float(calories_goal)
            user_profile.save()
            return redirect('index')
    return render(request, 'myapp/set_goal.html', {'calories_goal': user_profile.calories_goal})


def delete_consume(request, id):
    consumed_food = Consume.objects.get(id=id)
    if request.method == 'POST':
        consumed_food.delete()
        return redirect('/')
    return render(request, 'myapp/delete.html')


def food_list(request):
    foods = Food.objects.all()
    return render(request, 'myapp/food_list.html', {'foods': foods})


def delete_food(request, id):
    food = get_object_or_404(Food, id=id)
    if request.method == 'POST':
        food.delete()
        return redirect('food_list')
    return render(request, 'myapp/delete.html')


def update_food(request, id):
    food = get_object_or_404(Food, id=id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            # Prevent duplicate names
            if Food.objects.filter(name=name).exclude(id=id).exists():
                return render(request, 'myapp/update_food.html', {
                    'food': food,
                    'error': f"Food '{name}' already exists."
                })
            # Fetch nutrition info for the new name
            nutrition = get_food_nutrition(name)
            if nutrition:
                food.name = name
                food.calories = float(nutrition["calories"])
                food.protein = float(nutrition["protein"])
                food.fat = float(nutrition["fat"])
                food.carbohydrates = float(nutrition["carbs"])
                food.save()
            return redirect('food_list')
    return render(request, 'myapp/update_food.html', {'food': food})