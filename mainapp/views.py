from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from .models import MainCity, Location, Services, Blog, Transactions , HelpSupport , Ummrah , CalendarAvailability
from .serializers import UmmarhSerializer, CalendarAvailabilitySerializer, HelpSupportSerializer, MainCitySerializer, LocationSerializer, ReviewsSerializer, ServicesSerializer, BlogSerializer , TransactionSerializer , GuideAvailabilitySerializer , GuideProfileAvaibale
import cloudinary.uploader
from  authentications.models import GuideProfile , Reviews, UserProfile , CustomUser
from rest_framework.permissions import IsAuthenticated
from django.db import models  # Added import for aggregation functions
from authentications.models import GuideProfile
from django.shortcuts import get_object_or_404
from notifications.views import send_visible_notifications,send_firebase_notification
from notifications.models import Notification, FirebaseToken
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# MainCity Views (unchanged)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def main_city_list_create(request):
    if request.method == 'GET':
        main_cities = MainCity.objects.all()
        serializer = MainCitySerializer(main_cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = MainCitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def main_city_detail(request, pk):
    try:
        main_city = MainCity.objects.get(pk=pk)
    except MainCity.DoesNotExist:
        return Response({"error": "MainCity not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MainCitySerializer(main_city)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = MainCitySerializer(main_city, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        main_city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Location Views (unchanged)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def location_list_create(request):
    if request.method == 'GET':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def location_detail(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = LocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Services Views (updated)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def services_list_create(request):
    if request.method == 'GET':
        services = Services.objects.filter(user=request.user)
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['user_id'] = request.user.id  # Use 'user_id' instead of 'user'
        print("request.user.id", request.user.id)
        serializer = ServicesSerializer(data=data)
        if serializer.is_valid():
            service = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def services_detail(request, pk):
    try:
        # Optionally filter by user here too for consistency
        service = Services.objects.get(pk=pk, user=request.user)
    except Services.DoesNotExist:
        return Response({"error": "Service not found or you don't have access"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ServicesSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        data = request.data.copy()  # Create a mutable copy of request.data
        data['user'] = request.user.id  # Ensure user remains the authenticated user
        serializer = ServicesSerializer(service, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Blog Views (unchanged)
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
@api_view(['GET', 'POST'])
def blog_list_create(request):
    if request.method == 'GET':
        blogs = Blog.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = BlogSerializer(data=request.data)
        print("request.data",request.data)
        if serializer.is_valid():
            serializer.save()  # CloudinaryField will handle the image upload automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def blog_detail(request, pk):
    try:
        blog = Blog.objects.get(pk=pk)
    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlogSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = BlogSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("id", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def transaction_list_create(request):
    if request.method == 'GET':
        transactions = Transactions.objects.filter(guide=request.user.guide_profile).order_by('-created_at')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        data = request.data.copy()
        print("data", data)
        print("Authenticated user:", request.user, request.user.id)

        # Get the location names from the request
        location_names = data.get('locations', [])
        if isinstance(location_names, str):
            location_names = location_names.split(',')  # If it's a string, split into list
        location_names = [name.strip() for name in location_names]
        print("location_names", location_names)

        # Filter locations
        locations = Location.objects.filter(location_name__in=location_names)
        print("locations count:", locations.count(), "locations:", locations)

        # Validate guide_id early
        try:
            guide = GuideProfile.objects.get(id=data.get('guide_id'))
            print("guide", guide, "guide user:", guide.user)
        except GuideProfile.DoesNotExist:
            return Response(
                {"detail": "Invalid guide_id provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Filter services based on location and guide's user
        try:
            service_all = Services.objects.all()
            print("service_all count:", service_all.count())
            for service in service_all:
                print(f"Service ID: {service.id}, User: {service.user}, Location: {service.location}")
            services = Services.objects.filter(location__in=locations, user=guide.user)
            print("Filtered Services count:", services.count(), "services:", services)
        except Exception as e:
            print("Error filtering services:", str(e))
            return Response(
                {"detail": "Invalid service filter configuration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if not services.exists():
            print("No services found for guide user:", guide.user, "in locations:", location_names)
            return Response(
                {"detail": "Invalid locations or no services available for those locations"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get deduplicated service IDs
        service_ids = list(set(services.values_list('id', flat=True)))
        print("deduplicated service_ids", service_ids)

        # Add service_ids to the data
        data['service_ids'] = service_ids

        # Assign user and other fields
        user = get_object_or_404(UserProfile, user=request.user)
        print("user_id", user.id)
        data['user_id'] = user.id
        data['status'] = Transactions.StatusChoices.PENDING
        data['payment_status'] = False
        data['guide_id'] = guide.id  # Ensure guide_id is set

        # Serialize and save
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            transaction = serializer.save()
            print("transaction", transaction)

            # WebSocket Notification
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"guide_{guide.user.id}_transactions",
                {
                    "type": "new_transaction",
                    "transaction_id": transaction.id,
                }
            )

            # Create notification
            guide_user = CustomUser.objects.get(id=guide.user.id)
            print("guide_user", guide_user)
            notification = Notification.objects.create(
                user=guide_user,
                title="Request For Booking",
                message="New booking request is placed"
            )
            notification.save()

            # Send Firebase notification
            try:
                user_token = FirebaseToken.objects.get(user=guide_user)
                print("user_token", user_token)
                send_firebase_notification(
                    user_token.token,
                    title="Request For Booking",
                    body="New booking request is placed"
                )
            except FirebaseToken.DoesNotExist:
                print("No Firebase token found for guide_user")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def transaction_detail(request, pk):
   
    transaction = get_object_or_404(Transactions, pk=pk, guide=request.user.guide_profile)

    if request.method == 'GET':
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        allowed_updates = {'status', 'payment_status'}
        update_data = {key: request.data[key] for key in allowed_updates if key in request.data}

        serializer = TransactionSerializer(transaction, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            notification = Notification.objects.create(user = transaction.user.user, title = "Guide Booking", message = "Your guide is accepted your bokking request. Please now pay your payment")
            notification.save()
            user = FirebaseToken.objects.get(user = transaction.user.user)
            send_firebase_notification(user.token, title = "Guide Booking", body = "Your guide is accepted your bokking request. Please now pay your payment")
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("serializer",serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)  # 🔴 Ensure empty res
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail_user(request):
    if request.method == 'GET':
        transactions = Transactions.objects.filter(user=request.user.user_profile).order_by('-updated_at')  # Newest first
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_detail_all(request):
    if request.method == 'GET':
        transactions = Transactions.objects.all().order_by('-created_at')  # Newest first
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    
from datetime import datetime
from django.utils import timezone  # Import timezone utility

from django.db.models import Sum

@api_view(['GET'])
def search_available_guides(request):
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    location_names = request.query_params.getlist('location_ids[]')  
    adults = request.query_params.get('adults', 1)  # Default to 1 if not provided
    children = request.query_params.get('children', 0)  

    print("location_names", location_names)

    if not start_date or not end_date or not location_names:
        return Response({"error": "start_date, end_date, and location_ids are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        start_date = timezone.make_aware(datetime.fromisoformat(start_date.replace('Z', '+00:00')))
        end_date = timezone.make_aware(datetime.fromisoformat(end_date.replace('Z', '+00:00')))
    except ValueError:
        return Response({"error": "Invalid date format. Use ISO 8601 (e.g., 2025-03-07T10:00:00Z)"}, status=status.HTTP_400_BAD_REQUEST)

    locations = Location.objects.filter(location_name__in=location_names)
    if not locations.exists():
        return Response({"error": "One or more locations are invalid"}, status=status.HTTP_400_BAD_REQUEST)

    print("locations", locations)

    available_guides = []

    # Get guides that are verified and active
    guides = GuideProfile.objects.filter(guide_status=True, is_verified=True)

    for guide in guides:
        # Check for overlapping transactions
        overlapping_transactions = Transactions.objects.filter(
            guide=guide,
            trip_started_date__lt=end_date,
            trip_end_date__gt=start_date
        ).exists()

        if overlapping_transactions:
            continue  # Skip this guide if they have existing bookings

        # Get services this guide offers in the selected locations
        services = Services.objects.filter(user=guide.user, location__in=locations)

        # Ensure guide covers all requested locations
        unique_service_locations = services.values_list('location', flat=True).distinct()
        if len(unique_service_locations) < len(location_names):
            continue  

        # Calculate individual guide's total price
        price_sum = services.aggregate(total_price=Sum('price'))['total_price'] or 0
        number_of_days = (end_date - start_date).days + 1  
        guide_total_price = price_sum * number_of_days * int(adults)  

        # Prepare guide data
        image_url = "https://via.placeholder.com/90"  
        if guide.image and hasattr(guide.image, 'public_id'):
            image_url = cloudinary.CloudinaryImage(guide.image.public_id).build_url(secure=True)

        languages = [lang.name for lang in guide.languages.all()]
        location_str = ", ".join([loc.location_name for loc in locations])
        reviews = guide.reviews.all()
        total_reviews = reviews.count()
        average_rating = reviews.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0.0

        guide_data = {
            'id': guide.id,
            'user': guide.name,
            'user_id': guide.user.id,
            'location': location_str,
            'reviews': average_rating,
            'total_reviews': total_reviews,
            'joined': guide.user.date_joined.strftime("%b %Y") if guide.user.date_joined else "N/A",
            'price': price_sum,  # Individual guide's total price
            'image': image_url,
            'language': languages,
            'services': list(services.values('id', 'location__location_name', 'price')),  # Show service details
            'is_available': True
        }

        available_guides.append(guide_data)

        print("Guide Data:", guide_data)

    return Response({"guides": available_guides}, status=status.HTTP_200_OK)




@api_view(['GET'])
def get_guide_profile(request, guide_id):
    guide = get_object_or_404(GuideProfile, id=guide_id)

    services = Services.objects.filter(user=guide.user)
    location_str = "N/A"
    if services.exists():
        service = services.first()
        if service and service.location:
            location_name = service.location.location_name or "Unknown Location"
            main_city_name = service.location.main_city.name if service.location.main_city else "Unknown City"
            location_str = f"{location_name}, {main_city_name}"

    image_url = "https://via.placeholder.com/90"
    if guide.image and hasattr(guide.image, 'public_id'):
        image_url = cloudinary.CloudinaryImage(guide.image.public_id).build_url(secure=True)

    languages = [lang.name for lang in guide.languages.all()]

    # Calculate review statistics
    reviews = guide.reviews.all()
    rating_filter = Reviews.objects.filter(guide=guide)
    review_serializer = ReviewsSerializer(rating_filter, many=True)
    total_reviews = reviews.count()

    averages = reviews.aggregate(
        avg_rating=models.Avg('rating'),
        avg_personalized_tours=models.Avg('personalized_tours'),
        avg_navigation_assistance=models.Avg('navigation_assistance'),
        avg_translation_services=models.Avg('translation_services'),
        avg_local_knowledge=models.Avg('local_knowledge'),
        avg_safety_and_security=models.Avg('safety_and_security')
    )
    average_rating = averages['avg_rating'] or 0.0
    rating_details = {
        'personalized_tours': averages['avg_personalized_tours'] or 0.0,
        'navigation_assistance': averages['avg_navigation_assistance'] or 0.0,
        'translation_services': averages['avg_translation_services'] or 0.0,
        'local_knowledge': averages['avg_local_knowledge'] or 0.0,
        'safety_and_security': averages['avg_safety_and_security'] or 0.0
    }

    serializer = GuideProfileAvaibale({
        'id': guide.id,
        "user_id" : guide.user.id,
        'name': guide.name,
        'about_us': guide.about_us,
        'location': location_str,
        'reviews': total_reviews,
        'average_rating': average_rating,
        'rating_details': rating_details,
        'joined': guide.user.date_joined.strftime("%b %Y") if guide.user.date_joined else "N/A",
        'price': float(services.first().price) if services.exists() else 100.0,
        'image': image_url,
        'language': languages,
        'services': services,
        'rating': review_serializer.data,
        'is_available': True
    })
    
    print(serializer.data)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_messages_for_help_support(request):
    
    try:
        
        email = request.data.get("email")
        problem = request.data.get("message")
        data = HelpSupport(email=email, problem=problem)
        data.save()
        
        return Response({"message": "Message Send Sucessfully"}, status= 200)
    
    except:
        return Response({"errot": "Message Send Sucessfully"}, status= 500)
    
        
    
@csrf_exempt 
@api_view(['GET', 'POST'])
def get_help_support(request):
    if request.method == 'GET':
        help_support = HelpSupport.objects.all().order_by('-date')  # Order by latest first
        serializer = HelpSupportSerializer(help_support, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
@csrf_exempt
@api_view(['DELETE'])
def delete_help_support(request, id):
    try:
        help_support = HelpSupport.objects.get(id=id)
    except HelpSupport.DoesNotExist:
        return Response({"error": "Help support entry not found"}, status=status.HTTP_404_NOT_FOUND)

    help_support.delete()
    return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from django.core.mail import send_mail

@api_view(['POST'])
def send_reply_email(request, id):
    try:
      
        help_support = HelpSupport.objects.get(id=id)
      

        email = request.data.get('email')  # Get email from request
        reply_message = request.data.get('text')  # Get message from request

        if not email or not reply_message:
            return Response({"error": "Email and message are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Send Email
        send_mail(
            subject="Reply to Your Message",
            message=reply_message,
            from_email="your-email@gmail.com",  # Use the same email as in settings
            recipient_list=[email],
            fail_silently=False,
        )
        
        help_support.replied = reply_message
        help_support.save()
        

        return Response({"message": "Reply sent successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    

@csrf_exempt 
@api_view(['GET', 'POST'])
def ummrah_list_create(request):
    if request.method == 'GET':
        blogs = Ummrah.objects.all()
        serializer = UmmarhSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = UmmarhSerializer(data=request.data)
        print("request.data",request.data)
        if serializer.is_valid():
            serializer.save()  # CloudinaryField will handle the image upload automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', 'PUT', 'DELETE'])
def ummrah_detail(request, pk):
    try:
        blog = Ummrah.objects.get(pk=pk)
    except Ummrah.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UmmarhSerializer(blog)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = UmmarhSerializer(blog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("id", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_guide_calendar(request):
    """
    Fetch the calendar of the authenticated guide.
    - Only the guide's own availability is fetched.
    """
    guide = request.user.guide_profile  # Ensure only logged-in guide accesses their calendar

    date = request.query_params.get("date")  # Example: "2025-04-01"
    if not date:
        return Response({"error": "Date is required"}, status=400)

    calendar_entries = CalendarAvailability.objects.filter(guide=guide, date=date)
    serializer = CalendarAvailabilitySerializer(calendar_entries, many=True)

    return Response(serializer.data, status=200)


@api_view(['GET'])
def get_guide_aviable_calendar(request):
    """
    Fetch the calendar of a specific guide based on guide_id.
    - Requires date and guide_id in query params.
    """
    guide_id = request.query_params.get("guide_id")
    date = request.query_params.get("date")  # Example: "2025-04-01"

    if not date:
        return Response({"error": "Date is required"}, status=400)
    if not guide_id:
        return Response({"error": "Guide ID is required"}, status=400)

    try:
        guide = GuideProfile.objects.get(id=guide_id)  # Fetch the guide by ID
    except GuideProfile.DoesNotExist:
        return Response({"error": "Guide not found"}, status=404)

    calendar_entries = CalendarAvailability.objects.filter(guide=guide, date=date)
    serializer = CalendarAvailabilitySerializer(calendar_entries, many=True)

    return Response(serializer.data, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_time_slot(request):
    """
    Guide books or updates a time range.
    - The guide can only manage their own availability.
    """
    guide = request.user.guide_profile  # Fetch the authenticated guide
    print("guide.id",guide.id)
    data = request.data.copy()
    print("data",data)
    data["guide"] = guide.id  # Ensure guide ID is set

    serializer = CalendarAvailabilitySerializer(data=data, context={"request": request})
    
    if serializer.is_valid():
        serializer.save()
        
        return Response({"message": "Time slot booked successfully", "data": serializer.data}, status=201)
    print("error", serializer.errors)
    return Response(serializer.errors, status=400)






from django.db.models.functions import TruncMonth, ExtractYear

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from .models import Transactions
from authentications.models import GuideProfile
from authentications.models import Reviews
import logging
import calendar
logger = logging.getLogger('transactions.views')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_transaction_metrics(request):
    """
    Calculate transaction metrics for the authenticated user.
    Endpoint: GET /transactions/metrics/
    """
    try:
        user = request.user

      
        guide = GuideProfile.objects.get(user=user)
            # For GuideProfile: Reviews where the guide was reviewed
        print("guide", guide)
     
        # Filter transactions based on user type
        transactions = Transactions.objects.filter(guide=guide)
        # 1. Total Income (sum of total_amount for completed transactions)
        total_income = transactions.filter(
            status=Transactions.StatusChoices.COMPLETE
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        # 2. Ongoing Trips (count of transactions with status="Ongoing")
        ongoing_trips = transactions.filter(
            status=Transactions.StatusChoices.ONGOING
        ).count()

        # 3. Total Completed Trips (count of transactions with status="Complete")
        total_completed_trips = transactions.filter(
            status=Transactions.StatusChoices.COMPLETE
        ).count()
        review_average = Reviews.objects.filter(
                guide=guide
            ).aggregate(
                avg_rating=Avg('rating')
            )['avg_rating'] or 0
        # 4. Review Average (average rating from reviews for completed transactions)
       

        return Response({
            'total_income': float(total_income),  # Convert Decimal to float for JSON serialization
            'ongoing_trips': ongoing_trips,
            'review_average': float(review_average),  # Convert to float
            'total_completed_trips': total_completed_trips,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error("Error calculating transaction metrics for user %s: %s", user.id, str(e))
        return Response({
            'error': str(e),
            'total_income': 0,
            'ongoing_trips': 0,
            'review_average': 0,
            'total_completed_trips': 0,
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth, ExtractYear
import calendar

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    try:
        # Total Income (sum of amounts for completed transactions)
        total_income = Transactions.objects.filter(status="Complete").aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        # Total Guides (count of users with role "guide")
        total_guides = CustomUser.objects.filter(role="guide").count()

        # Total Users (count of all users or users with role "tourist")
        total_users = CustomUser.objects.filter(role="tourist").count()

        # Monthly Revenue for all years
        monthly_revenue = (
            Transactions.objects.filter(status="Complete")
            .annotate(
                year=ExtractYear("created_at"),  # Extract the year
                month=TruncMonth("created_at")   # Truncate to the start of the month
            )
            .values("year", "month")  # Group by year and month
            .annotate(revenue=Sum("total_amount"))
            .order_by("year", "month")
        )

        # Get the list of years for which data exists
        years_with_data = sorted(set(entry["year"] for entry in monthly_revenue))

        # Format monthly revenue data for all years, including all 12 months
        monthly_data = []
        for year in years_with_data:
            # For each year, loop through all 12 months
            for month_num in range(1, 13):
                month_name = calendar.month_name[month_num]  # Get the month name (e.g., "January")
                # Find the revenue for this year and month, default to 0 if no data
                revenue = next(
                    (
                        float(item["revenue"])
                        for item in monthly_revenue
                        if item["year"] == year and item["month"].month == month_num
                    ),
                    0
                )
                monthly_data.append({
                    "year": year,
                    "month": month_name,
                    "data": revenue
                })

        # Prepare the response
        response_data = {
            "total_income": float(total_income) if total_income else 0,
            "total_guides": total_guides,
            "total_users": total_users,
            "monthly_revenue": monthly_data,
            "years": years_with_data  # Include the list of years for the frontend
        }

        return Response(response_data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
   
   
#rating 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_rating(request):
    try:
        transaction_id = request.data.get("transaction_id")
        user = request.user
        guide_id = request.data.get("guide_id")
        overall_rating = request.data.get("overall_rating", 0)  # Add overall rating
        personalized_tours = request.data.get("personalized_tours", 0)
        navigation_assistance = request.data.get("navigation_assistance", 0)
        local_knowledge = request.data.get("local_knowledge", 0)
        translation_services = request.data.get("translation_services", 0)
        safety_and_security = request.data.get("safety_and_security", 0)
        comment = request.data.get("comment", "")

        # Validate guide_id
        if not guide_id:
            return Response({"error": "Guide ID is required."}, status=400)

        # Validate ratings (should be between 0 and 5)
        ratings = {
            "overall_rating": overall_rating,  # Add overall rating to validation
            "personalized_tours": personalized_tours,
            "navigation_assistance": navigation_assistance,
            "local_knowledge": local_knowledge,
            "translation_services": translation_services,
            "safety_and_security": safety_and_security,
        }
        for key, value in ratings.items():
            try:
                value = int(value)
                if value < 0 or value > 5:
                    return Response({"error": f"Invalid rating for {key}. Must be between 0 and 5."}, status=400)
            except (ValueError, TypeError):
                return Response({"error": f"Invalid rating for {key}. Must be an integer."}, status=400)

        # Get the guide (assuming guide is a User with role="guide")
        try:
            guide = GuideProfile.objects.get(user_id=guide_id)
        except GuideProfile.DoesNotExist:
            return Response({"error": "Guide not found."}, status=404)
        try:
            user = UserProfile.objects.get(user=user)
        except GuideProfile.DoesNotExist:
            return Response({"error": "Guide not found."}, status=404)
        
        try:
            trsansaction = Transactions.objects.get(id=transaction_id)
            trsansaction.rated = True
            trsansaction.save()
        except Transactions.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=404)
        
       
        

        # Create the rating
        rating = Reviews.objects.create(
            user=user,
            guide=guide,
            rating=overall_rating,  # Save overall rating
            personalized_tours=personalized_tours,
            navigation_assistance=navigation_assistance,
            local_knowledge=local_knowledge,
            translation_services=translation_services,
            safety_and_security=safety_and_security,
            comment=comment.strip() if comment else None,
        )
        rating.save()
        return Response({"message": "Rating submitted successfully."}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)



