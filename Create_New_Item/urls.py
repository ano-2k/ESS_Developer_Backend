from django.urls import path
from .views import *

urlpatterns = [
  # **Product Item Endpoints**
    path('product-items/', ProductItemListAPIView.as_view(), name='product_item_list'),
    #get ,put and delete
     path('product-item/<int:pk>/', ProductItemRetrieveAPIView.as_view(), name='product_item_retrieve'),
    path('product-item/<int:pk>/update/', ProductItemUpdateAPIView.as_view(), name='product_item_update'),
    path('product-item/<int:pk>/delete/', ProductItemDeleteAPIView.as_view(), name='product_item_delete'),
    path('product-item/create/', ProductItemCreateAPIView.as_view(), name='product_item_create'),
    # **Service Item Endpoints**
    path('service-items/', ServiceItemListAPIView.as_view(), name='service_item_list'),
    #get put and delete
    path('service-item/<int:pk>/', ServiceItemRetrieveAPIView.as_view(), name='service_item_retrieve'),
    path('service-item/<int:pk>/update/', ServiceItemUpdateAPIView.as_view(), name='service_item_update'),
    path('service-item/<int:pk>/delete/', ServiceItemDeleteAPIView.as_view(), name='service_item_delete'),
    path('service-item/create/', ServiceItemCreateAPIView.as_view(), name='service_item_create'),
    
  path('item/<str:item_type>/<int:pk>/delete/', ItemDeleteAPIView.as_view(), name='item_delete'),
    

    # add bulk hsn code and descreption
    path("import-hsn/", ImportHSNData.as_view(), name="import-hsn"),
    #add bulk sac code and dec
    path("import-sac/", ImportSACData.as_view(), name="import-sac"),
    path('gst-taxes/', GSTTaxListView.as_view(), name='gst-tax-list'),
    path('api/gsttax/bulk-upload/', BulkGSTTaxView.as_view(), name="bulk-gst-upload"),  
    path('api/product-service-items/', ProductAndServiceItemListAPIView.as_view(), name='product-service-items'),
    path('generate-barcode/', GenerateBarcodeAPIView.as_view(), name='generate-barcode'),
]
