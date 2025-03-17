import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import waiting_room.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyp.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(waiting_room.routing.websocket_urlpatterns)
    ),
})
