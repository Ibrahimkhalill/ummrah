

from django.urls import path
from .views import track_pixel

urlpatterns = [
    path('track_pixel/', track_pixel, name='approved_user'),
]