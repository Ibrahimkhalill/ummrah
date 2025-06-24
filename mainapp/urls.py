from django.urls import path
from . import views

app_name = 'mainapp'  # Namespace for the app

urlpatterns = [
    # MainCity URLs
    path('main-cities/', views.main_city_list_create, name='main_city_list_create'),
    path('main-cities/<int:pk>/', views.main_city_detail, name='main_city_detail'),

    # Location URLs
    path('locations/', views.location_list_create, name='location_list_create'),
    path('locations/<int:pk>/', views.location_detail, name='location_detail'),

    # Services URLs
    path('services/', views.services_list_create, name='services_list_create'),
    path('services/<int:pk>/', views.services_detail, name='services_detail'),

    # Blog URLs
    path('blogs/', views.blog_list_create, name='blog_list_create'),
    path('blogs/<int:pk>/', views.blog_detail, name='blog_detail'),

    # Transactions URLs
    path('transactions/', views.transaction_list_create, name='transaction_list_create'),
    path('transactions/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transactions/user/', views.transaction_detail_user, name='transaction_detail_user'),
    path('transactions/all/', views.transaction_detail_all, name='transaction_detail_all'),
    
    path('search-available-guides/', views.search_available_guides, name='search_available_guides'),
    
    path('guides/<int:guide_id>/', views.get_guide_profile, name='get_guide_profile'),  # New endpoint
    
    path('send_messages_for_help_support/', views.send_messages_for_help_support, name='send_messages_for_help_support'), 
    path('get_help_support/', views.get_help_support),# New endpoint
    path('delete_help_support/<int:id>/', views.delete_help_support),# New endpoint
    path('send-reply/<int:id>/', views.send_reply_email),# New endpoint
    
    #ummrah
    path('ummrah/', views.ummrah_list_create, name='ummrah_list_create'),
    path('ummrah/<int:pk>/', views.ummrah_detail, name='ummrah_detail'),
    
    # calender
    path('guide/calendar/', views.get_guide_calendar, name='get_guide_calendar'),
    path('guide/book-time-slot/', views.book_time_slot, name='book_time_slot'),
    path('guide/available/calender/', views.get_guide_aviable_calendar, name='get_guide_aviable_calendar'),
    
    
    # guide metrics
    
    path("guide/metrics/", views.get_user_transaction_metrics),
    path("calculate_yearly_revenue/", views.dashboard_stats),
    
    # ratings
    
    path("submit-rating/", views.submit_rating, name="submit-rating"),
     
]