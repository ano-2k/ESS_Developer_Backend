from django.urls import path
from .views import *

urlpatterns = [
    # 🔹 Purchase Orders
    path('purchase-orders/', PurchaseOrderListAPIView.as_view(), name='purchase-order-list'),
    path('purchase-orders/create/', PurchaseOrderCreateAPIView.as_view(), name='purchase-order-create'),
    path('purchase-orders/<int:pk>/', PurchaseOrderDetailAPIView.as_view(), name='purchase-order-detail'),
    path('purchase-orders/<int:pk>/update/', PurchaseOrderUpdateAPIView.as_view(), name='purchase-order-update'),
    path('purchase-orders/<int:pk>/delete/', PurchaseOrderDeleteAPIView.as_view(), name='purchase-order-delete'),

    # 🔹 Send Email for Purchase Order
    path('purchase-orders/<int:purchase_order_id>/send-email/', SendPurchaseOrderEmailAPIView.as_view(), name='purchase-order-send-email'),
    
    path('vendor-invoices/', VendorInvoiceListAPIView.as_view(), name='vendor-invoice-list'),
    path('vendor-invoices/create/', VendorInvoiceCreateAPIView.as_view(), name='vendor-invoice-create'),
    path('vendor-invoices/<int:pk>/', VendorInvoiceRetrieveAPIView.as_view(), name='vendor-invoice-detail'),
    path('vendor-invoices/update/<int:pk>/', VendorInvoiceUpdateAPIView.as_view(), name='vendor-invoice-update'),
    path('vendor-invoices/delete/<int:pk>/', VendorInvoiceDeleteAPIView.as_view(), name='vendor-invoice-delete'),

   
    # 🔹 Vendor Invoice Payments
    path('vendor-invoice-payment/<int:vendor_invoice_id>/', ConvertVendorInvoiceToPaymentAPIView.as_view(), name='convert-vendor-invoice-payment'),
    path('vendors/<int:vendor_id>/pending-invoices/', PendingVendorInvoicesAPIView.as_view(), name='pending-vendor-invoices'),
    path("vendor-invoice/payments/", ListVendorInvoicePaymentsAPIView.as_view(), name="list-vendor-payments"),
    path('vendor-invoice-payments/<int:pk>/delete/', VendorInvoicePaymentDeleteAPIView.as_view(), name='vendor-invoice-payment-delete'),
]
