from django.contrib import admin

# Register your models here.


from .models import *

admin.site.register(FirebaseToken)
admin.site.register(Notification)