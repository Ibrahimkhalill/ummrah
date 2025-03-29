
from django.urls import path 
from .views import create_checkout_session, checkout_success, checkout_cencel, stripe_webhook

urlpatterns = [
 
   path("checkout/session/",create_checkout_session),
   path("checkout/success/",checkout_success),
   path("checkout/cancel/",checkout_cencel),
   path("webhook/",stripe_webhook),
    
]
