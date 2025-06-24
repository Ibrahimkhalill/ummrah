from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from .models import CustomUser, UserProfile, GuideProfile, OTP , Language
from .serializers import (
    UserRegisterSerializer, GuideRegisterSerializer, LoginSerializer, UserSerializer,
    UserProfileSerializer, GuideProfileSerializer, OTPSerializer, UpdateProfileSerializer,
    AllProfileSerializer 
)
from .otpGenarate import generate_otp  # Assuming this exists
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import LangaugeSerializer
# Utility function for sending OTP
def send_otp_email(email, otp):
    html_content = render_to_string('otp_email_template.html', {'otp': otp, 'email': email})
    msg = EmailMultiAlternatives(
        subject='Your OTP Code',
        body=f'Your OTP is {otp}',
        from_email='hijabpoint374@gmail.com',
        to=[email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)



@api_view(["POST"])
def register_user(request):
    # For tourists and admins
    email = request.data.get("email")
    print("email", email)
    
    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        if user.role in ['tourist', 'admin']:
            try:
                profile = user.user_profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = UserProfileSerializer(profile)
        elif user.role == 'guide':
            try:
                profile = user.guide_profile
            except GuideProfile.DoesNotExist:
                profile = GuideProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = GuideProfileSerializer(profile)
            
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": profile_serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def register_guide(request):
    # For guides
    email = request.data.get("email")
    print("email", email)
    
    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = GuideRegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        if user.role in ['tourist', 'admin']:
            try:
                profile = user.user_profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = UserProfileSerializer(profile)
        elif user.role == 'guide':
            try:
                profile = user.guide_profile
            except GuideProfile.DoesNotExist:
                profile = GuideProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = GuideProfileSerializer(profile)
            
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": profile_serializer.data
        }, status=status.HTTP_201_CREATED)
    print(serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    if CustomUser.objects.filter(email=email).exists():
        return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
    
    otp = generate_otp()
    OTP.objects.create(email=email, otp=otp)
    try:
        send_otp_email(email, otp)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
def verify_otp(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    
    if not all([email, otp]):
        return Response({'error': 'Email and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        otp_record = OTP.objects.get(email=email, otp=otp)
        if otp_record.is_expired():
            otp_record.delete()
            return Response({'error': 'OTP expired'}, status=status.HTTP_400_BAD_REQUEST)
        otp_record.delete()
        return Response({'message': 'Email verified'}, status=status.HTTP_200_OK)
    except OTP.DoesNotExist:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        
        # Choose profile based on role
        if user.role in ['tourist', 'admin']:
            try:
                profile = user.user_profile
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = UserProfileSerializer(profile)
        elif user.role == 'guide':
            try:
                profile = user.guide_profile
            except GuideProfile.DoesNotExist:
                profile = GuideProfile.objects.create(user=user, name=user.email.split('@')[0])
            profile_serializer = GuideProfileSerializer(profile)
        
        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": profile_serializer.data
        }, status=status.HTTP_200_OK)
    print("serializer.errors",serializer.errors)
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["POST"])
def password_reset_send_otp(request):
    email = request.data.get('email')
    print("email", email)
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
        otp = generate_otp()
        OTP.objects.create(email=email, otp=otp)
        send_otp_email(email, otp)
        return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['POST'])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    
    if not all([email, new_password]):
        return Response({'error': 'Email, new password, and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
    except OTP.DoesNotExist:
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    if user.role in ['tourist', 'admin']:
        profile_model = UserProfile
        serializer_class = UserProfileSerializer
        related_name = 'user_profile'
    elif user.role == 'guide':
        profile_model = GuideProfile
        serializer_class = GuideProfileSerializer
        related_name = 'guide_profile'
    else:
        return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        try:
            profile = getattr(user, related_name)
            serializer = serializer_class(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except profile_model.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'PUT':
        try:
            profile = getattr(user, related_name)
            # Now handle file upload correctly
            image = request.FILES.get('image')  # Access the file via request.FILES

            # Update the profile using the data from request.data and request.FILES
            serializer = serializer_class(profile, data=request.data, partial=True)
            
            if serializer.is_valid():  # Ensure the serializer is valid before accessing validated_data
                # If image is present, add it to the validated data
                if image:
                    print("Image received:", image)
                    serializer.validated_data['image'] = image

                serializer.save()  # Save the profile with updated data
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print("Serializer errors:", serializer.errors)  # Log errors to console
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except profile_model.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST', 'GET'])  # Allow both POST and GET (though GET is not ideal)
def refresh_access_token(request):
    # For GET request, check the query params
    if request.method == 'GET':
        # Get the 'refresh_token' from the query parameters
        refresh_token = request.GET.get('refresh_token')
    else:
        # For POST request, get the data from the body (request.data)
        refresh_token = request.data.get('refresh_token')

    # If refresh_token is not provided, return an error
    if not refresh_token:
        return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
        return Response({'access_token': new_access_token}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def all_users(request):
    if request.method == 'GET':
        # Fetch user profiles
        user_profiles = UserProfile.objects.all()

        # Fetch guide profiles and order them by joined_date
        guide_profiles = GuideProfile.objects.all().order_by('joined_date')

        # Serialize the data
        user_serializer = UserProfileSerializer(user_profiles, many=True)
        guide_serializer = GuideProfileSerializer(guide_profiles, many=True)

        # Combine the data
        combined_data = {
            "tourists": user_serializer.data,
            "guides": guide_serializer.data
        }

        # Return response with the combined data
        return Response(combined_data, status=status.HTTP_200_OK)

@api_view(['GET'])       
def get_language(request):
    languages = Language.objects.all()
    data = {lang.name: lang.id for lang in languages}
    return Response(data, status=status.HTTP_200_OK)




@api_view(["PUT"])
def approved_user(request, id):
    
    try:
        user = GuideProfile.objects.get(id=id)
        
        user.is_verified = True
        user.save()
        
        return Response({"messages":"User Approved"}, status=200)
    
    except Exception:
        return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['DELETE'])
def delete_user(request, id):
    if request.method == 'DELETE':
        user = CustomUser.objects.get(pk=id)  # Newest first
        user.delete()
        return Response({"messages":"User delete Sucessfully"}, status=status.HTTP_204_NO_CONTENT)
    return  Response({"messages":"method not allowed"}, status=status.HTTP_204_NO_CONTENT)