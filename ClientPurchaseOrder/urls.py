# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path("create-client-po/", ClientPurchaseOrderCreateAPIView.as_view(), name="create-client-po"),
    path("update-client-po/<int:pk>/", ClientPurchaseOrderUpdateAPIView.as_view(), name="update-client-po"),
]
