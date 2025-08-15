# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r'ws/chat/private/(?P<username>[\w.@+-]+)/$',
        consumers.PrivateChatConsumer.as_asgi()
    ),
    re_path(r'ws/chat/group/(?P<room_id>\d+)/$', consumers.GroupChatConsumer.as_asgi()),
]
