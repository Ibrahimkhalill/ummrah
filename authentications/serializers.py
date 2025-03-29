from rest_framework import serializers
from django.contrib.auth import authenticate
import json
from .models import CustomUser, UserProfile, GuideProfile, OTP, Language


class LangaugeSerializer(serializers.ModelSerializer):  # Fixed typo: LangaugeSerializer -> LanguageSerializer
    class Meta:
        model = Language
        fields = ('id', 'name')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'role')
        read_only_fields = ('id',)

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = UserProfile
        fields = ('user', 'name', 'phone_number', 'address', 'image')
        read_only_fields = ('user',)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

class GuideProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    languages = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Language.objects.all(),
        required=False
    )
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = GuideProfile
        fields = (
            'id','user', 'name', 'phone_number', 'languages', 'about_us',
            'guide_card_number', 'address', 'is_verified', 'image', 'guide_status', 'joined_date'
        )
        read_only_fields = ('user',)

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def update(self, instance, validated_data):
        languages = validated_data.pop('languages', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if languages is not None:
            valid_languages = []
            for lang_name in languages:
                lang_obj, created = Language.objects.get_or_create(name=lang_name)
                valid_languages.append(lang_obj)
            
            instance.languages.set(valid_languages)

        return instance

class AllProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'name')
        read_only_fields = ('user',)

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ('email', 'otp')
        read_only_fields = ('otp',)

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=200, required=True)
    phone_number = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=True)
    role = serializers.ChoiceField(choices=['tourist', 'admin'], default='tourist', required=False)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'name', 'phone_number', 'role')

    def create(self, validated_data):
        name = validated_data.pop('name')
        phone_number = validated_data.pop('phone_number', None)
        role = validated_data.pop('role', 'tourist')
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        UserProfile.objects.create(
            user=user,
            name=name,
            phone_number=phone_number if phone_number else ''
        )
        return user

class GuideRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(max_length=200, required=True)
    phone_number = serializers.CharField(max_length=20, required=False)
    email = serializers.EmailField(required=True)
    languages = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Language.objects.all(),
        required=False
    )
    about_us = serializers.CharField(required=True)
    guide_card_number = serializers.CharField(max_length=20, required=False)
    
    class Meta:
        model = CustomUser
        fields = (
            'email', 'password', 'name', 'phone_number', 'languages',
            'about_us', 'guide_card_number',
        )

    def create(self, validated_data):
        name = validated_data.pop('name')
        phone_number = validated_data.pop('phone_number', None)
        languages = validated_data.pop('languages', [])
        about_us = validated_data.pop('about_us')
        guide_card_number = validated_data.pop('guide_card_number', None)
        
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role='guide'
        )
        guide_profile = GuideProfile.objects.create(
            user=user,
            name=name,
            phone_number=phone_number if phone_number else '',
            about_us=about_us,
            guide_card_number=guide_card_number if guide_card_number else '',
        )
        if languages:
            guide_profile.languages.set(languages)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")

        if user.role != role:
            raise serializers.ValidationError(
                f"Invalid user role. Expected '{user.role}', but got '{role}'."
            )

        return user

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'phone_number', 'address')