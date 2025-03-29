from django.urls import path
from . import views



urlpatterns = [
     path("save-expo-token/", views.save_fcm_token)
]