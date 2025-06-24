from django.urls import path
from .views import (
    register_user, register_guide, send_otp, verify_otp, login, 
    password_reset_send_otp, reset_password, profile, 
    refresh_access_token, all_users , get_language , approved_user ,delete_user
)

urlpatterns = [
    path('register-user/', register_user, name='register_user'),
    path('register-guide/', register_guide, name='register_guide'),
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('login/', login, name='login'),
    path('password-reset/send-otp/', password_reset_send_otp, name='password_reset_send_otp'),
    path('password-reset/', reset_password, name='reset_password'),
    path('profile/', profile, name='profile'),
    path('refresh-token/', refresh_access_token, name='refresh_token'),
    path('all-users/', all_users, name='all_users'),
    path('delete-users/<int:id>/', delete_user, name='delete_user'),
    path('all-langauge/', get_language, name='get_language'),
    path('aprove_guide/<int:id>/', approved_user, name='approved_user'),
   
]