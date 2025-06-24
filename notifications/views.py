from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework import status
from mainapp.serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes
from django.utils.timezone import now
import requests
from rest_framework.response import Response
from django.http import JsonResponse , HttpResponse
from .models import Notification, FirebaseToken
from django.conf import settings

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_notification_count(request):
    now_time = now()
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    print("unread_count",unread_count)
    return Response({"unread_count": unread_count}, status=status.HTTP_200_OK)

# API View for Fetching Notifications
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_view(request):
    # Only return notifications that are currently visible
    now_time = now()
    notifications = Notification.objects.filter(
        user=request.user,
    ).order_by('-created_at')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    data = [{
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "data": notification.data,
        "created_at": notification.created_at,
        "is_read": notification.is_read,
        "is_sound_play": notification.is_sound_played,
       
    } for notification in notifications]
    return Response(data, status=status.HTTP_200_OK)

# Mark Notification as Read
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_sound_played(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_sound_played = True
        notification.save()
        return Response({"message": "Sound marked as played"}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
    
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    if request.method == "POST":
        try:
            token = request.data.get("expo_token")
            user_id = request.user

            if not token:
                return JsonResponse({"error": "Token is required"}, status=400)

            # Check if the user already has an associated token
            firebase_token = FirebaseToken.objects.filter(user=user_id).first()

            if firebase_token:
                # If the token exists, update it
                firebase_token.token = token
                firebase_token.save()
                message = "Token updated successfully!"
            else:
                # If no token exists for the user, create a new one
                FirebaseToken.objects.create(user=user_id, token=token)
                message = "Token saved successfully!"

            return JsonResponse({"message": message})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)



def send_firebase_notification(token, title, body, data=None):
    print("send_firebase_notification")
    # Ensure all values in the data dictionary are strings
    expo_url = "https://exp.host/--/api/v2/push/send"
    payload = {
        "to": token,
        "title": title,
        "body": body,
        "data": data or {},  # Optional additional data
        "sound": "default"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(expo_url, json=payload, headers=headers)
    if response.status_code == 200:
        print("Notification sent successfully:", response.json())
    else:
        print("Failed to send notification:", response.text)




def send_visible_notifications():
    print("sss")
    # Fetch all notifications that are visible and not sent
    notifications = Notification.objects.filter(is_read=False, is_sound_played=False )
    if notifications: 
        for notification in notifications:
            # Get the user's FCM tokens
            tokens = FirebaseToken.objects.filter(user=notification.user).values_list("token", flat=True)
  
            # Send notification to each token
            for token in tokens:
                send_firebase_notification(
                    token=token,
                    title=notification.title,
                    body=notification.message,
                    data= notification.data
                )

            # Mark the notification as sent
            notification.is_sound_played = True
            notification.save()
            
            print("notification is send", tokens)
    print("check notification")
