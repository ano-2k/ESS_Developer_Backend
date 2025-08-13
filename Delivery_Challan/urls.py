from django.urls import path
from .views import *

urlpatterns = [
    path('create/', CombinedDeliveryChallanCreateAPIView.as_view(), name='combined-delivery-challan-create'),
    path('retrieve/', RetrieveDeliveryChallanAPIView.as_view(), name='retrieve_delivery_challan'),
    path('delivery-challans/', DeliveryChallanListAPIView.as_view(), name='delivery-challan-list'),
    path("delivery-challan/<int:pk>/update/", CombinedDeliveryChallanUpdateAPIView.as_view(), name="delivery-challan-update"),
    path('send_delivery_challan_email/<int:delivery_challan_id>/', SendDeliveryChallanEmailAPIView.as_view(), name="send_delivery_challan_email"),
    path("delivery-challan/<int:id>/update/", DeliveryChallanUpdateAPIView.as_view(), name="update-delivery-challan"),
    path("delivery-challan/<int:id>/delete/", DeliveryChallanDeleteAPIView.as_view(), name="delete-delivery-challan"),
    path("delivery-challan/delete/<str:delivery_challan_number>/", DeliveryChallanDeleteByNumberAPIView.as_view(),name="delete-delivery-challan-by-number"),
]
