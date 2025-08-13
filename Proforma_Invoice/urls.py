from django.urls import path
from .views import *

urlpatterns = [
    # Endpoint to retrieve a ProformaInvoice by ID
    path('retrieve/', RetrieveProformaInvoiceAPIView.as_view(), name="retrieve_proforma_invoice"),
    
    # Endpoint to send a ProformaInvoice email with PDF attachment
    path('send_email/<int:proforma_invoice_id>/', SendProformaInvoiceEmailAPIView.as_view(), name="send_proforma_invoice_email"),
    
    # Endpoint to create a Proforma Invoice and its items in one request
    path('proforma-invoice/', CombinedProformaInvoiceCreateAPIView.as_view(), name='combined-proforma-invoice-create'),
    path("proforma-invoice/<int:pk>/update/", CombinedProformaInvoiceUpdateAPIView.as_view(), name="proforma-invoice-update"),

     # ProformaInvoice Views
    path('proforma-invoices/', GetProformaInvoicesByPartyIdAPIView.as_view(), name='get-all-proforma-invoices'),  # GET all
    path('proforma-invoice/<int:proforma_invoice_id>/', GetProformaInvoiceByIdAPIView.as_view(), name='get-proforma-invoice-by-id'),  # GET by ID
    path('proforma-invoice/update/<int:proforma_invoice_id>/', UpdateProformaInvoiceByIdAPIView.as_view(), name='update-proforma-invoice-by-id'),  # PUT by ID
    path('proforma-invoice/delete/<int:proforma_invoice_id>/', DeleteProformaInvoiceByIdAPIView.as_view(), name='delete-proforma-invoice-by-id'),  # DELETE by ID
    
    # ProformaInvoice by Party ID
    path('proforma-invoices/party/<int:party_id>/', GetProformaInvoicesByPartyIdAPIView.as_view(), name='get-proforma-invoices-by-party-id'),  # GET by Party ID
    path('proforma-invoices/update/party/<int:party_id>/', UpdateProformaInvoicesByPartyIdAPIView.as_view(), name='update-proforma-invoices-by-party-id'),  # PUT by Party ID
    path('proforma-invoices/delete/party/<int:party_id>/', DeleteProformaInvoicesByPartyIdAPIView.as_view(), name='delete-proforma-invoices-by-party-id'),  # DELETE by Party ID
    
    # PDF Views
    path('download-pdf/<int:proforma_invoice_id>/', DownloadProformaInvoicePDFAPIView.as_view(), name='download-proforma-invoice-pdf'),
    path('print-pdf/<int:proforma_invoice_id>/', PrintProformaInvoicePDFAPIView.as_view(), name='print-proforma-invoice-pdf'),
     path('proforma-invoices-list/', ProformaInvoiceListAPIView.as_view(), name='proforma_invoice_list'),
     path('proforma-invoice/delete/<str:proforma_invoice_number>/', DeleteProformaInvoiceByNumberAPIView.as_view(),name='delete-proforma-invoice-by-number'),
]
