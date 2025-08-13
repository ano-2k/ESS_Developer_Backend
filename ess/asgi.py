# # your_project_name/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chat.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ess.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})


# myproject/asgi.py
# import os
# from django.core.asgi import get_asgi_application
# from fastapi import FastAPI
# from fastapi_app import fastapi_app

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")

# django_asgi_app = get_asgi_application()

# # Add FastAPI app to the ASGI application
# from starlette.middleware.trustedhost import TrustedHostMiddleware
# from fastapi.middleware.wsgi import WSGIMiddleware

# # You can also apply custom middleware here
# django_asgi_app = TrustedHostMiddleware(django_asgi_app)

# application = WSGIMiddleware(fastapi_app)
