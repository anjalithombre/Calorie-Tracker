


from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from myapp import views  # Import the views from your app

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication
    path('', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),

    # Core app
    path('index/', views.index, name='index'),
    path('add_item/', views.add_item, name='add_item'),
    path('set_goal/', views.set_goal, name='set_goal'),

    # Food management
    path('food_list/', views.food_list, name='food_list'),
    path('food_delete/<int:id>/', views.delete_food, name='food_delete'),
    path('food_update/<int:id>/', views.update_food, name='food_update'),

    # Consumption management
    path('delete/<int:id>/', views.delete_consume, name="delete"),

    # Reports
    path('report/', views.report, name='report'),
    path('report/pdf/', views.report_pdf, name='report_pdf'),
    path("chatbot/", include("chatbot.urls")),
]



