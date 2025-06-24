from rest_framework import serializers
from .models import MainCity, Location, Services, Blog, Transactions ,HelpSupport , Ummrah , CalendarAvailability
from authentications.models import UserProfile, GuideProfile , Reviews 
from authentications.serializers import UserSerializer
from django.contrib.auth import get_user_model
import cloudinary.uploader
from cloudinary import CloudinaryImage
User = get_user_model()

class MainCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCity
        fields = ['id', 'name']
        
class HelpSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = HelpSupport
        fields = ['id', 'email','problem','date', 'replied']
        

class UmmarhSerializer(serializers.ModelSerializer):
    
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Ummrah
        fields = ['id', 'title', 'image', 'description']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None     


class LocationSerializer(serializers.ModelSerializer):
    main_city = MainCitySerializer(read_only=True)
    main_city_id = serializers.PrimaryKeyRelatedField(
        queryset=MainCity.objects.all(), source='main_city', write_only=True
    )

    class Meta:
        model = Location
        fields = ['id', 'main_city', 'main_city_id', 'location_name']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user','name','phone_number'] 
    

class UserReviewProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user' ,'name', 'phone_number', 'image']

    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'public_id'):
            return CloudinaryImage(obj.image.public_id).build_url(secure=True)
        return None
    
class GuideProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)
    class Meta:
        model = GuideProfile
        fields = ['id', 'user', 'name','phone_number','image', 'guide_card_number' ]  # Adjust fields as needed
    
    def get_image(self, obj):
        if obj.image and hasattr(obj.image, 'public_id'):
            return CloudinaryImage(obj.image.public_id).build_url(secure=True)
        return None
   
        


class ServicesSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), source='location', write_only=True
    )
    user = UserProfileSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True, required=False
    )

    class Meta:
        model = Services
        fields = ['id', 'user', 'user_id', 'location', 'location_id', 'price']

    def validate(self, data):
        return data
    def create(self, validated_data):
        return super().create(validated_data)
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

class TransactionSerializer(serializers.ModelSerializer):
    user = UserReviewProfileSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), source='user', write_only=True
    )
    guide = GuideProfileSerializer(read_only=True)
    guide_id = serializers.PrimaryKeyRelatedField(
        queryset=GuideProfile.objects.all(), source='guide', write_only=True
    )
    services = ServicesSerializer(many=True, read_only=True)  # Service will be included here
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Services.objects.all(), source='services', write_only=True, many=True
    )

    status = serializers.ChoiceField(choices=Transactions.StatusChoices.choices, required=False)
    payment_status = serializers.BooleanField(default=False)

    class Meta:
        model = Transactions
        fields = [
            'id', 'user', 'user_id', 'guide', 'guide_id', 'services', 'service_ids',
            'adult', 'children', 'total_amount', 'trip_started_date', 'trip_end_date',
            'tax', 'status', 'payment_status' ,'created_at', 'updated_at', 'rated'
        ]

    def create(self, validated_data):
        service_ids = validated_data.pop('services', [])  # Get services from validated data

        transaction = super().create(validated_data)

        # Set the services for the transaction after it's created
        transaction.services.set(service_ids)
        
        return transaction



class BlogSerializer(serializers.ModelSerializer):
    location = MainCitySerializer(read_only=True)  # Changed to MainCitySerializer since Blog uses MainCity
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=MainCity.objects.all(), source='location', write_only=True
    )
    image = serializers.ImageField(required=False, allow_null=True)


    class Meta:
        model = Blog
        fields = ['id', 'location', 'location_id', 'title', 'image', 'description']

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None


# Update ReviewsSerializer
class ReviewsSerializer(serializers.ModelSerializer):
    guide = serializers.StringRelatedField()
    user = UserReviewProfileSerializer(read_only=True)

    class Meta:
        model = Reviews
        fields = ['id', 'user', 'guide', 'rating', 'comment', 'personalized_tours', 'navigation_assistance', 'translation_services', 'local_knowledge', 'safety_and_security', 'created_at']
    

class GuideProfileAvaibale(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    name = serializers.CharField()
    about_us = serializers.CharField()
    location = serializers.CharField()
    reviews = serializers.IntegerField(default=0)
    average_rating = serializers.FloatField(default=0.0)
    rating_details = serializers.DictField(
        child=serializers.FloatField(),
        default={
            'personalized_tours': 0.0,
            'navigation_assistance': 0.0,
            'translation_services': 0.0,
            'local_knowledge': 0.0,
            'safety_and_security': 0.0
        }
    )
    joined = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.URLField()
    language = serializers.ListField(child=serializers.CharField())
    services = serializers.ListField(child=ServicesSerializer())
    rating = serializers.ListField()
    is_available = serializers.BooleanField()

class GuideAvailabilitySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user = serializers.CharField()  # Changed to CharField since we pass the username directly
    location = serializers.CharField()
    reviews = serializers.IntegerField(default=0)
    joined = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image = serializers.URLField()
    language = serializers.ListField(child=serializers.CharField())  # Changed to ListField for multiple languages
    services = serializers.ListField(child=ServicesSerializer())
    is_available = serializers.BooleanField()
    
    
    
    
class CalendarAvailabilitySerializer(serializers.ModelSerializer):
    guide_name = serializers.CharField(source='guide.name', read_only=True)  # Ensure guide info is included

    class Meta:
        model = CalendarAvailability
        fields = ['id', 'guide', 'guide_name', 'date', 'start_time', 'end_time', 'status']

    # def validate(self, data):
    #     """
    #     Ensure that only the guide can book or modify their own availability.
    #     """
    #     request = self.context.get('request')

    #     if request and request.user:
    #         if request.user.id != data.get("guide").id:
    #             raise serializers.ValidationError("You can only manage your own availability.")
    #     return data