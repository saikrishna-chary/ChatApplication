
# chat_config/asgi.py
import os
import django

# Setup Django before importing anything else from Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_config.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})



