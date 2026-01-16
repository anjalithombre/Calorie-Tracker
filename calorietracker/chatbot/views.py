from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import os

from myapp.models import Food
from myapp.views import get_food_nutrition   # helper for Open Food Facts

# ✅ Import Google Generative AI SDK
import google.generativeai as genai

# ✅ Configure Gemini with your API key from environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Stop words to avoid treating greetings/fillers as food names
STOP_WORDS = {
    "hi", "hello", "hey", "thanks", "ok",
    "how", "are", "you", "i", "am"
}

def chat_page(request):
    """Render the chatbot frontend page."""
    return render(request, "chatbot/chat.html")

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "").lower().strip()

        reply = None

        # 1. Greeting
        if user_message in STOP_WORDS:
            reply = "Hi there! How can I help you today?"

        # 2. Nutrition lookup in DB
        if not reply:
            food = Food.objects.filter(name__iexact=user_message).first()
            if food:
                reply = (
                    f"{food.name.title()} contains "
                    f"{food.calories} calories, "
                    f"{food.protein}g protein, "
                    f"{food.fat}g fat, and "
                    f"{food.carbohydrates}g carbohydrates per 100g."
                )

        # 3. Fallback: Fetch from Open Food Facts if not in DB
        if not reply:
            nutrition = get_food_nutrition(user_message)
            if nutrition:
                reply = (
                    f"{user_message.title()} contains "
                    f"{nutrition['calories']} calories, "
                    f"{nutrition['protein']}g protein, "
                    f"{nutrition['fat']}g fat, and "
                    f"{nutrition['carbs']}g carbohydrates per 100g."
                )
                # Save to DB for next time
                Food.objects.get_or_create(
                    name=user_message,
                    defaults={
                        "calories": nutrition["calories"],
                        "protein": nutrition["protein"],
                        "fat": nutrition["fat"],
                        "carbohydrates": nutrition["carbs"],
                    }
                )

        # 4. GenAI fallback for general conversation (Gemini)
        if not reply:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(
                "You are a helpful nutrition assistant. " + user_message
            )
            reply = response.text

        return JsonResponse({"response": reply})

    # Handle GET requests gracefully
    return JsonResponse({"response": "Chatbot endpoint is ready. Please send a POST request with JSON."})