from django.contrib import admin
from .models import MainCity, Location, Services, Blog, Transactions, HelpSupport , Ummrah ,CalendarAvailability

# Register your models here.

@admin.register(MainCity)
class MainCityAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns to display in the admin list view
    search_fields = ('name',)  # Enable search by name

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'main_city')  # Show location name and related main city
    list_filter = ('main_city',)  # Filter by main city
    search_fields = ('location_name',)  # Enable search by location name

@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('location', 'price')  # Show location and price
    list_filter = ('location',)  # Filter by location
    search_fields = ('price',)  # Enable search by price

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')  # Show title and location
    list_filter = ('location',)  # Filter by location
    search_fields = ('title',)  # Enable search by title
    # No need to specify 'description' field explicitly; CKEditor 5 will render automatically

# If you prefer the simpler registration method, you could use:
admin.site.register(Transactions)
admin.site.register(HelpSupport)
admin.site.register(Ummrah)
admin.site.register(CalendarAvailability)

# admin.site.register(Blog)