from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import ChatHistory, ChatMessage
from .serializers import ChatSerializer , ChatMessageSerializer
import uuid
from django.db import models  # Added import for aggregation functions
from authentications.models import GuideProfile, UserProfile
User = get_user_model()

from rest_framework.permissions import IsAuthenticated

# ✅ Helper function to get user profile info
def get_user_profile(user):
    """Fetch user's profile data including name and image"""
    user_profile = UserProfile.objects.filter(user=user).first()
    guide_profile = GuideProfile.objects.filter(user=user).first()

    if user_profile:
        return {
            "name": user_profile.name,
            "image": user_profile.image.url if user_profile.image else None
        }
    elif guide_profile:
        return {
            "name": guide_profile.name,
            "image": guide_profile.image.url if guide_profile.image else None
        }
    return {"name": user.email, "image": None}  # Default fallback

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_chat(request):
    """
    Check if a chat exists in ChatMessage. If exists, return the chat_id.
    Otherwise, create a new chat.
    """
    try:
        sender = request.user  # ✅ Authenticated user as sender
        receiver_id = request.data.get('receiver_id')  # ✅ Receiver ID from request

        if not receiver_id:
            return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "Receiver not found"}, status=status.HTTP_404_NOT_FOUND)

        # ✅ Check if a chat exists in ChatMessage
        existing_message = ChatMessage.objects.filter(
            (models.Q(sender=sender, receiver=receiver) | models.Q(sender=receiver, receiver=sender))
        ).select_related('chat').first()  # ✅ Check both sender-receiver & receiver-sender
        
        if existing_message:
            existing_chat = existing_message.chat
            print(f"🔄 Returning existing chat_id: {existing_chat.chat_id}")
            serializer = ChatSerializer(existing_chat)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # ✅ If no existing chat, create a new one
        print("🆕 Creating new chat...")
        new_chat = ChatHistory.objects.create(chat_id=uuid.uuid4())
        new_chat.save()

        # ✅ Send response
        serializer = ChatSerializer(new_chat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request, chat_id):
    """
    Retrieve the chat history for a given chat_id in WebSocket format.
    """
    try:
        print(f"Fetching chat history for chat_id: {chat_id}")

        # ✅ Ensure chat_id is a UUID
        chat_uuid = uuid.UUID(chat_id)
       
        chat = ChatHistory.objects.get(chat_id=chat_uuid)
        messages = ChatMessage.objects.filter(chat=chat).order_by("timestamp")  # ✅ Order by timestamp

        # ✅ Format messages in WebSocket format
        formatted_messages = []
        for msg in messages:
            sender_profile = get_user_profile(msg.sender)
            formatted_messages.append({
                "id": str(msg.id),
                "message": msg.message,
                "sender": msg.sender.id,
                "name": sender_profile["name"],
                "image": sender_profile["image"],
                "timestamp": msg.timestamp.isoformat(),
                "is_read": msg.is_read,
            })

        return Response(formatted_messages, status=status.HTTP_200_OK)

    except ChatHistory.DoesNotExist:
        return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValueError:
        return Response({'error': 'Invalid chat_id format'}, status=status.HTTP_400_BAD_REQUEST)




def get_chat_list(user):
    """
    Retrieve all unique chat sessions for the given user.
    Returns a list of chat sessions with last message details.
    Only includes unread message count when the user is the receiver.
    """
    try:
        messages = ChatMessage.objects.filter(
            models.Q(sender=user) | models.Q(receiver=user)
        )

        unique_chat_ids = set(messages.values_list('chat', flat=True))  # ✅ Use set() for uniqueness

        chat_list = []

        for chat_id in unique_chat_ids:
            try:
                chat = ChatHistory.objects.get(id=chat_id)

                # ✅ Get the last message in this chat
                last_message = ChatMessage.objects.filter(chat=chat).order_by("-timestamp").first()
                
                if not last_message:
                    continue  # Skip if there are no messages

                # ✅ Calculate unread count only for messages where user is the receiver
                receiver_unread_count = ChatMessage.objects.filter(
                    chat=chat,
                    receiver=user,  # Only count messages where user is the receiver
                    is_read=False
                ).count()

                # ✅ Identify the other user
                other_user = last_message.sender if last_message.sender != user else last_message.receiver

                # ✅ Fetch user profile details
                profile = get_user_profile(other_user)

                # ✅ Append chat details to the list
                chat_list.append({
                    "chat_id": str(chat.chat_id),
                    "user_id": other_user.id,
                    "name": profile["name"],
                    "image": profile["image"],
                    "last_message": last_message.message,
                    "timestamp": last_message.timestamp.isoformat(),
                    "count": receiver_unread_count,  # Only includes unread count for receiver
                    "is_read": last_message.is_read,
                })
            except ChatHistory.DoesNotExist:
                continue  # Skip if chat history is missing

        # ✅ Sort chat list by latest message timestamp (descending order)
        return sorted(chat_list, key=lambda x: x["timestamp"], reverse=True)

    except Exception as e:
        print(f"❌ Error fetching chat list: {str(e)}")
        return []




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_chat_list(request):
    """
    Retrieve all unique chat sessions for the authenticated user.
    """
    try:
        chat_list = get_chat_list(request.user)
        return Response(chat_list, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def count_unread_messages(request):
    """
    Get the count of unread messages for the authenticated user.
    Endpoint: GET /chat/count/unread/
    """
    try:
        # Count messages where the authenticated user is the receiver and is_read=False
        receiver_unread_count = ChatMessage.objects.filter(
            receiver=request.user,
            is_read=False
        ).count()

        # Total unread messages
       
        return Response({'total_unread': receiver_unread_count}, status=status.HTTP_200_OK)
    except Exception as e:
       
        return Response({'error': 'Failed to count unread messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_chat_messages_as_read(request, chat_id):
    """
    Mark all messages in a specific chat as read for the authenticated user.
    Endpoint: POST /chat/mark-read/<chat_id>/
    """
    try:
        # Verify the chat exists
        chat = ChatHistory.objects.get(chat_id=chat_id)
        # Update messages where the authenticated user is the receiver and is_read=False
        messages = ChatMessage.objects.filter(
            chat=chat,
            receiver=request.user,
            is_read=False
        )
        updated_count = messages.update(is_read=True)
      
        return Response({'message': f'Marked {updated_count} messages as read'}, status=status.HTTP_200_OK)
    except ChatHistory.DoesNotExist:
    
        return Response({'error': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      
        return Response({'error': 'Failed to mark messages as read'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)