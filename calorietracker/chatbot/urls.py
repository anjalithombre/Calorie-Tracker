from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_page, name="chat_page"),          # GET → shows chat UI
    path("chat/", views.chatbot_response, name="chatbot_response"),  # POST → API
]