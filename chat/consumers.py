'''
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message, ChatRoom
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user = self.scope["url_route"]["kwargs"]["username"]

        # Generate consistent private room name
        self.room_name = f"chat_{min(self.user.username, self.other_user)}_{max(self.user.username, self.other_user)}"
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        sender = self.user
        receiver = await self.get_user(self.other_user)
        msg_obj = await self.save_message(sender, receiver, message)
        timestamp = self.format_timestamp(msg_obj.timestamp)

        # Send to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg_obj.content,
                "media_url": msg_obj.media.url if msg_obj.media else "",
                "sender": sender.username,  # keep as actual sender
                "timestamp": timestamp,
                "message_id": msg_obj.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "media_url": event["media_url"],
            "sender": event["sender"],  # ✅ keep as actual username
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        room_name = f"chat_{min(sender.username, receiver.username)}_{max(sender.username, receiver.username)}"
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            room_type="private",
            defaults={"room_type": "private"}
        )

        # ✅ Ensure members are set if new room
        if created:
            room.members.set([sender, receiver])
            room.save()

        message_obj = Message(sender=sender, room=room, content=message)
        message_obj.save()
        return message_obj

    def format_timestamp(self, timestamp):
        now = timezone.localtime(timezone.now())
        timestamp = timezone.localtime(timestamp)
        if timestamp.date() == now.date():
            day_str = "Today"
        elif timestamp.date() == (now - timedelta(days=1)).date():
            day_str = "Yesterday"
        else:
            day_str = timestamp.strftime("%d %b %Y")
        time_str = timestamp.strftime("%I:%M %p")
        return f"{time_str}, {day_str}"


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"group_chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()

        if not message:
            return

        sender = self.user
        msg_obj = await self.save_message(sender, self.room_id, message)
        timestamp = self.format_timestamp(msg_obj.timestamp)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group_chat_message",
                "message": msg_obj.content,
                "media_url": msg_obj.media.url if msg_obj.media else "",
                "sender": sender.username,
                "timestamp": timestamp,
                "message_id": msg_obj.id,
            }
        )

    async def group_chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "media_url": event["media_url"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def save_message(self, sender, room_id, message):
        room = ChatRoom.objects.get(id=room_id, room_type="group")
        message_obj = Message(sender=sender, room=room, content=message)
        message_obj.save()
        return message_obj

    def format_timestamp(self, timestamp):
        now = timezone.localtime(timezone.now())
        timestamp = timezone.localtime(timestamp)
        if timestamp.date() == now.date():
            day_str = "Today"
        elif timestamp.date() == (now - timedelta(days=1)).date():
            day_str = "Yesterday"
        else:
            day_str = timestamp.strftime("%d %b %Y")
        time_str = timestamp.strftime("%I:%M %p")
        return f"{time_str}, {day_str}"
'''

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import Message, ChatRoom
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.other_user = self.scope["url_route"]["kwargs"]["username"]

        # Consistent private room name
        self.room_name = f"chat_{min(self.user.username, self.other_user)}_{max(self.user.username, self.other_user)}"
        self.room_group_name = self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        media_url = data.get("media_url", "")

        sender = self.user
        receiver = await self.get_user(self.other_user)

        msg_obj = None
        if message or media_url:
            msg_obj = await self.save_message(sender, receiver, message, media_url)

        timestamp = self.format_timestamp(msg_obj.timestamp)

        # Broadcast to both users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": msg_obj.content if msg_obj else "",
                "media_url": msg_obj.media.url if msg_obj and msg_obj.media else "",
                "sender": sender.username,
                "timestamp": timestamp,
                "message_id": msg_obj.id if msg_obj else None,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "media_url": event["media_url"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def get_user(self, username):
        return User.objects.get(username=username)

    @database_sync_to_async
    def save_message(self, sender, receiver, message, media_url=""):
        room_name = f"chat_{min(sender.username, receiver.username)}_{max(sender.username, receiver.username)}"
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            room_type="private",
            defaults={"room_type": "private"}
        )
        if created:
            room.members.set([sender, receiver])
            room.save()

        message_obj = Message(sender=sender, room=room, content=message)

        # If uploading media through WebSocket, save it
        if media_url:
            from django.core.files.base import ContentFile
            import base64
            format, imgstr = media_url.split(';base64,')
            ext = format.split('/')[-1]
            file_data = ContentFile(base64.b64decode(imgstr), name=f"upload_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}")
            message_obj.media = file_data

        message_obj.save()
        return message_obj

    def format_timestamp(self, timestamp):
        now = timezone.localtime(timezone.now())
        timestamp = timezone.localtime(timestamp)
        if timestamp.date() == now.date():
            day_str = "Today"
        elif timestamp.date() == (now - timedelta(days=1)).date():
            day_str = "Yesterday"
        else:
            day_str = timestamp.strftime("%d %b %Y")
        time_str = timestamp.strftime("%I:%M %p")
        return f"{time_str}, {day_str}"

    async def delete_message_event(self, event):
        """
        Sends a delete message event to all connected clients in the room.
        """
        await self.send(text_data=json.dumps({
            "action": "delete_message",
            "message_id": event["message_id"]
        }))


class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"group_chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        media_url = data.get("media_url", "")

        sender = self.user
        msg_obj = await self.save_message(sender, self.room_id, message, media_url)
        timestamp = self.format_timestamp(msg_obj.timestamp)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "group_chat_message",
                "message": msg_obj.content,
                "media_url": msg_obj.media.url if msg_obj.media else "",
                "sender": sender.username,
                "timestamp": timestamp,
                "message_id": msg_obj.id,
            }
        )

    async def group_chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "media_url": event["media_url"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
            "message_id": event["message_id"],
        }))

    @database_sync_to_async
    def save_message(self, sender, room_id, message, media_url=""):
        room = ChatRoom.objects.get(id=room_id, room_type="group")
        message_obj = Message(sender=sender, room=room, content=message)

        if media_url:
            from django.core.files.base import ContentFile
            import base64
            format, imgstr = media_url.split(';base64,')
            ext = format.split('/')[-1]
            file_data = ContentFile(base64.b64decode(imgstr), name=f"upload_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}")
            message_obj.media = file_data

        message_obj.save()
        return message_obj

    def format_timestamp(self, timestamp):
        now = timezone.localtime(timezone.now())
        timestamp = timezone.localtime(timestamp)
        if timestamp.date() == now.date():
            day_str = "Today"
        elif timestamp.date() == (now - timedelta(days=1)).date():
            day_str = "Yesterday"
        else:
            day_str = timestamp.strftime("%d %b %Y")
        time_str = timestamp.strftime("%I:%M %p")
        return f"{time_str}, {day_str}"

    async def delete_message_event(self, event):
        """
        Sends a delete message event to all connected clients in the room.
        """
        await self.send(text_data=json.dumps({
            "action": "delete_message",
            "message_id": event["message_id"]
        }))
