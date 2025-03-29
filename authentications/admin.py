from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, OTP, GuideProfile, Language, Reviews


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'role', 'is_staff', 'is_active')  # Added 'role'
    list_filter = ('role', 'is_staff', 'is_active', 'is_superuser')  # Added 'role' to filters
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),  # Added 'role'
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'is_staff', 'is_active', 'is_superuser')}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Inline for managing languages in GuideProfile
class LanguageInline(admin.TabularInline):
    model = GuideProfile.languages.through  # The through model for ManyToMany
    extra = 1  # Number of empty rows to display
    verbose_name = "Language"
    verbose_name_plural = "Languages"

# Customize GuideProfile admin
@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number', 'guide_card_number', 'is_verified', 'guide_status')
    list_filter = ('user__role', 'is_verified', 'guide_status')  # Added is_verified and guide_status filters
    search_fields = ('user__email', 'name', 'phone_number', 'guide_card_number')
    inlines = [LanguageInline]  # Add inline for languages
    fieldsets = (
        (None, {'fields': ('user', 'name', 'phone_number', 'is_verified', 'guide_status')}),
        ('Guide Details', {'fields': ('languages', 'about_us', 'guide_card_number', 'address', 'image')}),
    )

# Register CustomUser
admin.site.register(CustomUser, CustomUserAdmin)

# Register other models
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone_number')
    search_fields = ('user__email', 'name', 'phone_number')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('email', 'otp', 'created_at', 'attempts')
    list_filter = ('created_at',)
    search_fields = ('email', 'otp')

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ('guide', 'user', 'rating', 'created_at')
    search_fields = ('guide__name', 'user__name')
    list_filter = ('created_at', 'rating')
