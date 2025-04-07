import json
import re
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            sender_email = self.scope["user"].username  # Current logged-in user's email
            receiver_email = self.scope["url_route"]["kwargs"]["username"]  # Chat partner's email

            # Sanitize usernames to avoid special character issues in channel layers
            sender_clean = re.sub(r'[^a-zA-Z0-9]', '_', sender_email)
            receiver_clean = re.sub(r'[^a-zA-Z0-9]', '_', receiver_email)

            # Ensure room name is the same for both users
            self.room_group_name = f"chat_{'_'.join(sorted([sender_clean, receiver_clean]))}"

            # Add user to the WebSocket group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()

            # Load chat history when user connects
            chat_history = await self.get_chat_history(sender_email, receiver_email)
            await self.send(text_data=json.dumps({
                "type": "chat_history",
                "messages": chat_history
            }))

        except Exception as e:
            print(f"⚠️ Error during WebSocket connection: {e}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # Remove user from the WebSocket group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            print(f"🔌 WebSocket disconnected with code: {close_code}")
        except Exception as e:
            print(f"⚠️ Error during WebSocket disconnection: {e}")

    async def receive(self, text_data):
        """Handle receiving messages from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "typing":
                await self.handle_typing(data)
            elif message_type == "stop_typing":
                await self.handle_stop_typing(data)
            elif message_type == "mark_as_read":
                await self.handle_mark_as_read(data)
            else:
                await self.handle_message(data)

        except Exception as e:
            print(f"⚠️ Error receiving WebSocket message: {e}")

    async def handle_typing(self, data):
        """Handle typing indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "typing_indicator",
                "sender": data["sender"]
            }
        )

    async def handle_stop_typing(self, data):
        """Handle stop typing indicator."""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "stop_typing_indicator",
                "sender": data["sender"]
            }
        )

    async def handle_mark_as_read(self, data):
        """Mark messages as read when the user checks them."""
        message_id = data.get("message_id")
        if message_id:
            await self.mark_message_as_read(message_id)

            # Broadcast the read status update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "message_status",
                    "message_id": message_id,
                    "is_read": True
                }
            )

    async def handle_message(self, data):
        """Handle sending a new message."""
        message = data.get("message")

        if not message:
            print("⚠️ No message content received.")
            return

        sender = self.scope["user"]
        receiver_username = self.scope["url_route"]["kwargs"]["username"]

        # Use the first name instead of username
        sender_name = sender.first_name if sender.first_name else sender.username

        # Save message to database
        message_id = await self.save_message(sender.username, receiver_username, message)

        # Broadcast message to all users in the chat room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_name": sender_name,
                "timestamp": self.format_timestamp(datetime.now()),  # Use consistent format
                "message_id": message_id["message_id"],  # FIXED: Extract message ID correctly
                "is_read": False  # New messages should be unread
            }
        )

    async def typing_indicator(self, event):
        """Send typing indicator to the WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "typing",
            "sender": event["sender"]
        }))

    async def stop_typing_indicator(self, event):
        """Send stop typing indicator to the WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "stop_typing",
            "sender": event["sender"]
        }))

    async def message_status(self, event):
        """Send message status update to the WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "message_status",
            "message_id": event["message_id"],
            "is_read": event["is_read"]
        }))

    async def chat_message(self, event):
        """Send a new message to the WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "new_message",
            "message": event["message"],
            "sender_name": event["sender_name"],
            "timestamp": event["timestamp"],  # Already formatted
            "message_id": event["message_id"],
            "is_read": event.get("is_read", False)
        }))

    @database_sync_to_async
    def get_chat_history(self, sender_email, receiver_email):
        """Retrieve past messages between the two users."""
        messages = Message.objects.filter(
            (Q(sender__username=sender_email, receiver__username=receiver_email) |
             Q(sender__username=receiver_email, receiver__username=sender_email))
        ).order_by("timestamp")

        return [{
            "message": msg.content,
            "sender": msg.sender.username,
            "timestamp": self.format_timestamp(msg.timestamp),  # Use consistent format
            "message_id": msg.id,
            "is_read": msg.is_read
        } for msg in messages]

    @database_sync_to_async
    def save_message(self, sender_email, receiver_email, message):
        """Save chat message to database with local time and return details."""
        sender = User.objects.get(username=sender_email)
        receiver = User.objects.get(username=receiver_email)

        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=message,
            timestamp=datetime.now(),  # Store in local time
        )
        
        return {
            "message_id": message.id,
            "timestamp": self.format_timestamp(message.timestamp),  # Use consistent format
            "is_read": message.is_read  # Include read status
        }

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark a message as read and ensure it updates in the database."""
        message = Message.objects.filter(id=message_id, receiver=self.scope["user"], is_read=False).first()
        if message:
            message.is_read = True
            message.save(update_fields=['is_read'])  # Optimize DB update

    def format_timestamp(self, timestamp):
        """Helper function to format timestamp in 12-hour format with AM/PM."""
        return timestamp.strftime("%I:%M %p")  # Example: 01:01 PM




import json
import re
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatGroup, GroupMessage

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the raw group name from the URL and manually sanitize it.
        raw_group_name = self.scope["url_route"]["kwargs"]["group_name"]
        print(f"Raw group name: {raw_group_name}")
        sanitized_group_name = raw_group_name.replace(" ", "-").lower()  # "New Group" -> "new-group"
        print(f"Sanitized group name: {sanitized_group_name}")
        self.group_name = sanitized_group_name
        self.room_group_name = f"group_{self.group_name}"
        
        # Retrieve the group; do not create a new one if it doesn't exist.
        self.group = await self.get_group(self.group_name)
        if self.group is None:
            print(f"Group '{self.group_name}' not found. Closing connection.")
            await self.close()
            return

        # Join the WebSocket group.
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Accept the connection.
        await self.accept()
        print(f"Connected to group: {self.group_name}")
        
        # Load chat history when user connects and send it to the client.
        chat_history = await self.get_chat_history()
        await self.send(text_data=json.dumps({
            "type": "chat_history",
            "messages": chat_history
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        sender = self.scope["user"]
        sender_name = sender.first_name if sender.first_name else sender.username

        if message:
            # Save the message using the existing group instance.
            await self.save_group_message(sender.username, self.group_name, message)
            # Broadcast the message to the group.
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "group_message",
                    "message": message,
                    "sender_name": sender_name
                }
            )

    async def group_message(self, event):
        # Send the new group message to the client.
        await self.send(text_data=json.dumps({
            "type": "new_group_message",
            "message": event["message"],
            "sender_name": event["sender_name"]
        }))

    @database_sync_to_async
    def get_group(self, group_name):
        """
        Retrieve the ChatGroup instance by matching the sanitized name.
        Do not create a new group if it doesn't exist.
        """
        try:
            for group in ChatGroup.objects.all():
                if group.name.replace(" ", "-").lower() == group_name:
                    # Ensure the current user is a member.
                    if self.scope["user"] not in group.members.all():
                        group.members.add(self.scope["user"])
                    return group
            return None
        except ChatGroup.DoesNotExist:
            return None

    @database_sync_to_async
    def save_group_message(self, sender_username, group_name, message):
        """
        Save the group message using the existing group instance.
        """
        try:
            sender = User.objects.get(username=sender_username)
            # Use self.group which was retrieved during connect().
            GroupMessage.objects.create(
                sender=sender,
                group=self.group,
                content=message,
                timestamp=datetime.now()
            )
        except Exception as e:
            print(f"Error saving group message: {e}")

    @database_sync_to_async
    def get_chat_history(self):
        """
        Retrieve past messages for the current group, ordered by timestamp (ascending).
        """
        messages = GroupMessage.objects.filter(group=self.group).order_by("timestamp")
        return [
            {
                "message": msg.content,
                "sender_name": msg.sender.first_name if msg.sender.first_name else msg.sender.username,
                "timestamp": msg.timestamp.strftime("%I:%M %p")
            }
            for msg in messages
        ]


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like
from DigitalAssets.models import Blog, Whitepaper, Insight
User = get_user_model()

class TimelineConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("timeline", self.channel_name)
        await self.accept()
        print("✅ WebSocket connected timeline:", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("timeline", self.channel_name)
        print("❌ WebSocket disconnected:", close_code)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "like":
            await self.handle_like(data)
        elif action == "comment":
            await self.handle_comment(data)
        elif action == "new_post":
            await self.handle_new_post(data)

    async def handle_like(self, data):
        post_id = data.get("post_id")
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return

        post = await sync_to_async(Post.objects.get)(id=post_id)
        user_profile = await sync_to_async(lambda: user.userprofile)()

        liked = await sync_to_async(post.likes.filter(user_profile=user_profile).exists)()
        if liked:
            await sync_to_async(post.likes.filter(user_profile=user_profile).delete)()
        else:
            like_instance = Like(post=post, user_profile=user_profile)
            await sync_to_async(like_instance.save)()

        likes_count = await sync_to_async(post.likes.count)()
        await self.channel_layer.group_send(
            "timeline",
            {
                "type": "broadcast_like",
                "post_id": post_id,
                "like_count": likes_count,
            }
        )

    async def broadcast_like(self, event):
        await self.send(text_data=json.dumps({
            "action": "like_update",
            "post_id": event["post_id"],
            "like_count": event["like_count"],
        }))

    async def handle_comment(self, data):
        post_id = data.get("post_id")
        comment_text = data.get("comment_text")
        parent_id = data.get("parent_id")
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return

        post = await sync_to_async(Post.objects.get)(id=post_id)
        user_profile = await sync_to_async(lambda: user.userprofile)()

        comment = await sync_to_async(Comment.objects.create)(
            post=post,
            user_profile=user_profile,
            text=comment_text,
            parent_id=parent_id,
        )
        comment_count = await sync_to_async(post.comments.count)()
        created_at_str = comment.created_at.isoformat() + "Z"
        print(f"Sent created_at: {created_at_str}")
        await self.channel_layer.group_send(
            "timeline",
            {
                "type": "new_comment",
                "post_id": str(post_id),
                "comment_id": str(comment.id),
                "text": comment_text,
                "username": user.username,
                "full_name": user.get_full_name(),
                "created_at": created_at_str,
                "parent_id": str(parent_id) if parent_id else None,
                "comment_count": comment_count,
            }
        )

    async def new_comment(self, event):
        await self.send(text_data=json.dumps({
            "action": "new_comment",
            "post_id": event["post_id"],
            "comment_id": event["comment_id"],
            "text": event["text"],
            "username": event["username"],
            "full_name": event["full_name"],
            "created_at": event["created_at"],
            "parent_id": event["parent_id"],
            "comment_count": event["comment_count"],
        }))

    async def handle_new_post(self, data):
        post_id = data.get("post_id")
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            return

        post = await sync_to_async(Post.objects.get)(id=post_id)
        user_profile = post.user_profile
        post_data = {
            "id": str(post.id),
            "user_id": str(user_profile.user.id),
            "username": user_profile.user.username,
            "full_name": user_profile.user.get_full_name(),
            "user_profile_image": user_profile.profile_image.url if user_profile.profile_image else None,
            "caption": post.caption,
            "image": post.image.url if post.image else None,
            "created_at": post.created_at.isoformat() + "Z",
            "like_count": await sync_to_async(post.likes.count)(),
            "comment_count": await sync_to_async(post.comments.count)(),
            "content_type": post.content_type,
            "content": None,
        }

        # Fetch related content based on content_type
        if post.content_type == "blog":
            blog = await sync_to_async(Blog.objects.get)(id=post.content_id)
            post_data["content"] = {
                "id": blog.id,
                "title": blog.title,
                "content": blog.content,
                "thumbnail": blog.thumbnail.url if blog.thumbnail else None,
            }
        elif post.content_type == "whitepaper":
            whitepaper = await sync_to_async(Whitepaper.objects.get)(id=post.content_id)
            post_data["content"] = {
                "id": whitepaper.id,
                "title": whitepaper.title,
                "summary": whitepaper.summary,
            }
        elif post.content_type == "insight":
            insight = await sync_to_async(Insight.objects.get)(id=post.content_id)
            post_data["content"] = {
                "id": insight.id,
                "title": insight.title,
                "summary": insight.summary,
            }

        await self.channel_layer.group_send(
            "timeline",
            {
                "type": "broadcast_post",
                "post": post_data,
            }
        )

    async def broadcast_post(self, event):
        post = event["post"]
        user = self.scope.get("user")
        current_user_id = str(user.id) if user and user.is_authenticated else None

        if current_user_id != post["user_id"]:
            # Notify other users to show the refresh button
            await self.send(text_data=json.dumps({
                "action": "show_refresh_button",
            }))
        else:
            await self.send(text_data=json.dumps({
                "action": "new_post",
                "post": post,
            }))

    async def show_refresh_button(self, event):
        await self.send(text_data=json.dumps({
            "action": "show_refresh_button",
        }))