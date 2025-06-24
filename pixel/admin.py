from django.contrib import admin
from .models import Pixel

@admin.register(Pixel)
class PixelAdmin(admin.ModelAdmin):
    list_display = ('ip', 'website_url', 'image_link', 'time_spend', 'timestamp')  # Columns shown in the list view
    list_filter = ('timestamp',)  # Add filtering options
    search_fields = ('ip', 'website_url')  # Enable search functionality
    ordering = ('-timestamp',)  # Order by latest timestamp

