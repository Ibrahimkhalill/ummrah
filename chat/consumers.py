import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from .models import ChatHistory, ChatMessage
from authentications.models import UserProfile, GuideProfile
from notifications.views import send_firebase_notification
from notifications.models import FirebaseToken

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection for a specific chat"""
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        try:
            # ✅ Ensure chat exists before allowing connection
            self.chat = await sync_to_async(ChatHistory.objects.get)(chat_id=self.chat_id)
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"✅ WebSocket connected to chat {self.chat_id}")

        except ChatHistory.DoesNotExist:
            print(f"❌ Chat {self.chat_id} does not exist.")
            await self.close(code=404)

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"⚠️ WebSocket disconnected from chat {self.chat_id}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            sender_id = text_data_json.get('sender_id')
            receiver_id = text_data_json.get('receiver_id')

            if not (message and sender_id and receiver_id):
                print("⚠️ Missing required fields in WebSocket message.")
                return

            # ✅ Validate sender and receiver
            sender = await sync_to_async(User.objects.get)(id=sender_id)
            receiver = await sync_to_async(User.objects.get)(id=receiver_id)

            # ✅ Get sender's name and image
            sender_profile = await self.get_user_profile(sender)

            # ✅ Save message to database
            chat_message = await sync_to_async(ChatMessage.objects.create)(
                chat=self.chat,
                sender=sender,
                receiver=receiver,
                message=message
            )
            try:
                firebase_token = await sync_to_async(FirebaseToken.objects.get)(user=receiver)
                print("Firebase token:", firebase_token.token)
                # ✅ Send Firebase notification
                await sync_to_async(send_firebase_notification)(
                    token=firebase_token.token,
                    title=sender_profile["name"],
                    body=message,
                    data = "InboxScreen"
                )
            except FirebaseToken.DoesNotExist:
                print(f"❌ Firebase token not found for user {receiver.id}")
            # ✅ Broadcast message to WebSocket group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "id": chat_message.id,
                    'message': message,
                    'sender': sender_id,
                    'name': sender_profile["name"],
                    'image': sender_profile["image"],
                    'timestamp': chat_message.timestamp.isoformat(),
                    'is_read': chat_message.is_read,
                }
            )
           
            

            # ✅ Notify frontend about the new message (without sending the full chat list)
            await ChatListConsumer.notify_new_message(sender_id, receiver_id)

        except Exception as e:
            print(f"❌ Error in WebSocket receive: {str(e)}")

    async def get_user_profile(self, user):
        """Fetch user's profile data including name and image asynchronously"""
        user_profile = await sync_to_async(UserProfile.objects.filter(user=user).select_related("user").first)()
        guide_profile = await sync_to_async(GuideProfile.objects.filter(user=user).select_related("user").first)()

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

    async def chat_message(self, event):
        """Send received messages to WebSocket"""
        await self.send(text_data=json.dumps(event))


from urllib.parse import parse_qs

class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection for the chat list"""
        try:
            # ✅ Extract user_id from WebSocket URL
            query_string = parse_qs(self.scope["query_string"].decode())
            user_id = query_string.get("user_id", [None])[0]

            if not user_id:
                print("❌ WebSocket Connection Failed: No User ID Provided")
                await self.close()
                return

            # ✅ Validate user
            try:
                self.user = await sync_to_async(User.objects.get)(id=user_id)
            except User.DoesNotExist:
                print("❌ User Not Found")
                await self.close()
                return

            # ✅ Join WebSocket Group
            self.group_name = f"user_{self.user.id}_chat_list"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"✅ WebSocket Connected for {self.user.username}")

        except Exception as e:
            print(f"❌ Error connecting WebSocket: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"⚠️ WebSocket Disconnected for {self.user.username}")
        except Exception as e:
            print(f"❌ Error disconnecting WebSocket: {str(e)}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages (not needed here)"""
        pass  

    @staticmethod
    async def notify_new_message(sender_id, receiver_id):
        """Send a notification to the frontend that a new message has arrived"""
        channel_layer = get_channel_layer()

        # ✅ Notify sender and receiver that a new message has arrived
        for user_id in [sender_id, receiver_id]:
            await channel_layer.group_send(
                f"user_{user_id}_chat_list",
                {
                    "type": "new_message_received",
                    "user_id": user_id
                }
            )

    async def new_message_received(self, event):
        """Send notification to frontend when a new message arrives"""
        await self.send(text_data=json.dumps({
            "type": "new_message_notification",
            "message": "New message received!",
            "user_id": event["user_id"]
        }))



class GuideTransactionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """WebSocket connection for Guide's Transactions"""
        query_string = parse_qs(self.scope["query_string"].decode())
        self.guide_id = query_string.get("guide_id", [None])[0]
        print(f"r Guide {self.guide_id}")
        if not self.guide_id:
            print("❌ No Guide ID provided in WebSocket connection")
            await self.close()
            return
        
        self.room_group_name = f"guide_{self.guide_id}_transactions"

        # ✅ Add Guide to WebSocket Group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ WebSocket Connected for Guide {self.guide_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket Disconnection"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"⚠️ Guide {self.guide_id} WebSocket Disconnected")

    async def new_transaction(self, event):
        """Send new transaction data to the Guide in real-time"""
        await self.send(text_data=json.dumps({
        "type": "new_transaction",
        "transaction_id": event["transaction_id"],
       
    }))