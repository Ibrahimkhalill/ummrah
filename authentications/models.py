from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.conf import settings
from cloudinary.models import CloudinaryField  # Import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self._create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('guide', 'Guide'),
        ('tourist', 'Tourist'),
    )
    username = None
    email = models.EmailField(_('email address'), unique=True, max_length=255)
    role = models.CharField(max_length=10, choices=ROLES, default='tourist')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f'OTP for {self.email}: {self.otp}'

    def save(self, *args, **kwargs):
        with transaction.atomic():
            OTP.objects.filter(email=self.email).delete()
            super().save(*args, **kwargs)

    def is_expired(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 120

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='user_profile'
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', folder="tourists", blank=True, null=True)  # Changed to CloudinaryField
    joined_date = models.DateField(auto_created=True, blank=True, null=True)
    def __str__(self):
        return self.user.email if self.user else "No User"

class Language(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

class GuideProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='guide_profile'
    )
    is_verified = models.BooleanField(default=False, blank=True, null=True)
    guide_status = models.BooleanField(default=True, null=True, blank=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    languages = models.ManyToManyField(Language, blank=True)
    about_us = models.TextField(blank=True, null=True)
    guide_card_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', folder="guides", blank=True, null=True)  # Changed to CloudinaryField
    joined_date = models.DateField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user.email if self.user else "No User"
    
    
class Reviews(models.Model):
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews')
    rating = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])  # Overall rating (0-5)
    comment = models.TextField(blank=True, null=True)
    personalized_tours = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])  # Category ratings
    navigation_assistance = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    translation_services = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    local_knowledge = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    safety_and_security = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by  for {self.guide.name}"

    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"