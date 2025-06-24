from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField
from django.conf import settings
from authentications.models import GuideProfile, UserProfile

# Create your models here.

class MainCity(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name or "Unnamed City"

    class Meta:
        verbose_name = "Main City"
        verbose_name_plural = "Main Cities"

class Location(models.Model):
    main_city = models.ForeignKey(
        MainCity, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name="locations"
    )
    location_name = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return self.location_name or "Unnamed Location"

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"

class Services(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='services'
    )
    location = models.ForeignKey(
        Location, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name="services"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Price in local currency (e.g., 100.50)"
    )

    def __str__(self):
        return f"Service at {self.location} - {self.price or 'No Price'}"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"



class Transactions(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "Pending", "Pending"
        COMPLETE = "Complete", "Complete"
        ONGOING = "Ongoing", "Ongoing"
        PAYMENT = "Payment", "Payment"

    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE)
    services = models.ManyToManyField(Services, blank=True)  # Many-to-many relationship
    adult = models.IntegerField(default=0)
    children = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    trip_started_date = models.DateTimeField()
    trip_end_date = models.DateTimeField()
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    rated = models.BooleanField(default=False)
    
    # Correctly defining the status field with choices
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    payment_status = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # First time creation
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)  # Updates on every save
    
    def __str__(self):
        return f"Transaction by {self.user} with {self.guide} from {self.trip_started_date} to {self.trip_end_date}"

class HelpSupport(models.Model):
    email = models.CharField(max_length=255)  # Added max_length
    problem = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    replied = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Support from {self.email}"

    class Meta:
        verbose_name = "Help Support"
        verbose_name_plural = "Help Supports"

class Blog(models.Model):
    location = models.ForeignKey(
        MainCity, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name="blogs"
    )
    title = models.TextField(blank=True, null=True)
    image = CloudinaryField('blog', blank=True, null=True)
    description = CKEditor5Field(blank=True, null=True, config_name="extends")

    def __str__(self):
        return self.title or "Untitled Blog"

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"
        
        
class Ummrah(models.Model):
    title = models.TextField(blank=True, null=True)
    image = CloudinaryField('ummrah', blank=True, null=True)
    description = CKEditor5Field(blank=True, null=True, config_name="extends")

    def __str__(self):
        return self.title or "Untitled ummrah"

    class Meta:
        verbose_name = "ummrah"
        verbose_name_plural = "ummrah"
        
        
class CalendarAvailability(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
    ]

    guide = models.ForeignKey(GuideProfile, on_delete=models.CASCADE, related_name="calendar")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="available")

    def __str__(self):
        return f"{self.guide.name} - {self.date} {self.start_time}-{self.end_time} ({self.status})"