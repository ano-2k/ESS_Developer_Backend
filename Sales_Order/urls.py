from django.urls import path
from .views import *

urlpatterns = [
    path("sales-order/create/", ClientSalesOrderCreateAPIView.as_view(), name="create-client-sales-order"),
    path('sales-orders/', GetAllClientSalesOrdersAPIView.as_view(), name='get_all_sales_orders'),
    path('sales-orders/<int:id>/', GetSingleClientSalesOrderAPIView.as_view(), name='get_single_sales_order'),
    path('sales-orders/<int:id>/update/', UpdateClientSalesOrderAPIView.as_view(), name='update_sales_order'),
    path('sales-orders/<int:id>/delete/', DeleteClientSalesOrderAPIView.as_view(), name='delete_sales_order'),
    path('client-sales-order/<int:sales_order_id>/send-email/', SendClientSalesOrderEmailAPIView.as_view(), name='send_client_sales_order_email'),
]
