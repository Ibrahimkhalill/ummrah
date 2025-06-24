from django.db import models

# Create your models here.


class Pixel(models.Model):
    ip = models.CharField(max_length=200, blank=True, null=True)
    website_url = models.CharField(max_length=400, blank=True, null=True)
    image_link = models.CharField(max_length=400, blank=True, null=True)
    time_spend = models.CharField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
    