from django.urls import path
from .views import *

urlpatterns = [
    path('unpaid-invoices/<int:party_id>/', GetUnpaidInvoicesAPIView.as_view(), name="get-unpaid-invoices"),
   # path('convert-invoice/', ConvertSalesInvoiceToPaymentAPIView.as_view(), name="convert-invoice-to-payment"),
    path('convert-invoice/<int:party_id>/', ConvertSalesInvoiceToPaymentAPIView.as_view(), name="convert-multiple-invoices-to-payment"),
    path('send-payment-email/<int:payment_id>/', SendPaymentEmailAPIView.as_view(), name='send-payment-email'),  # new
    path('create-payment-in/', CreatePaymentInAPIView.as_view(), name="create-payment-in"),
    path("payment-in/list/", ListPaymentInAPIView.as_view(), name="payment-in-list"),
    path('payment/yearly-revenue/', YearlyRevenueView.as_view(), name='yearly-revenue'),
    path('payment/monthly-revenue/', MonthlyRevenueView.as_view(), name='monthly-revenue'),
    path('update/<int:id>/',UpdatePaymentInAPIView.as_view(),name="update-payment-in"),
    path('delete/<int:id>/',DeletePaymentInAPIView.as_view(),name="delete-payment-in"),
    path('delete/<str:payment_in_number>/', DeletePaymentInnoAPIView.as_view(), name="delete-payment-in"),
    path('payments-in/party/<int:party_id>/', PaymentsInByPartyView.as_view(), name='payments-in-by-party'),
]
