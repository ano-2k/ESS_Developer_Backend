from django.urls import path
from .views import *

urlpatterns = [
    path('sales-invoice/', CombinedSalesInvoiceCreateAPIView.as_view(), name='combined-sales-invoice-create'),
    path('retrieve/', RetrieveSalesInvoiceAPIView.as_view(), name="retrieve_sales_invoice"),
    path('send_email/<int:invoice_id>/', SendSalesInvoiceEmailAPIView.as_view(), name="send_sales_invoice_email"),
    path("convert_from_quotation/<int:quotation_id>/", ConvertQuotationToInvoiceAPIView.as_view(), name="convert_quotation_to_invoice"),
     path('sales-invoice/<int:pk>/update/', CombinedSalesInvoiceUpdateAPIView.as_view(), name='sales-invoice-update'),
     
    path('convert_from_proforma/<int:proforma_invoice_id>/', ConvertProformaToSalesInvoiceAPIView.as_view(), name='convert_proforma_to_sales_invoice'),
    path('convert_from_delivery_challan/<int:delivery_challan_id>/', ConvertDeliveryChallanToSalesInvoiceAPIView.as_view(), name="convert_delivery_challan_to_sales_invoice"),
      # SalesInvoice Views
    path('sales-invoices/', GetAllSalesInvoicesAPIView.as_view(), name='get-all-sales-invoices'),  # GET all
    path('sales-invoice/<int:sales_invoice_id>/', GetSalesInvoiceByIdAPIView.as_view(), name='get-sales-invoice-by-id'),  # GET by ID
    path('sales-invoice/update/<int:sales_invoice_id>/', UpdateSalesInvoiceByIdAPIView.as_view(), name='update-sales-invoice-by-id'),  # PUT by ID
    path('sales-invoice/delete/<int:sales_invoice_id>/', DeleteSalesInvoiceByIdAPIView.as_view(), name='delete-sales-invoice-by-id'),  # DELETE by ID
    
    # SalesInvoice by Party ID
    path('sales-invoices/party/<int:party_id>/', GetSalesInvoicesByPartyIdAPIView.as_view(), name='get-sales-invoices-by-party-id'),  # GET by Party ID
    path('sales-invoices/update/party/<int:party_id>/', UpdateSalesInvoicesByPartyIdAPIView.as_view(), name='update-sales-invoices-by-party-id'),  # PUT by Party ID
    path('sales-invoices/delete/party/<int:party_id>/', DeleteSalesInvoicesByPartyIdAPIView.as_view(), name='delete-sales-invoices-by-party-id'),  # DELETE by Party ID
    
    # PDF Views
    path('download-pdf/<int:sales_invoice_id>/', DownloadSalesInvoicePDFAPIView.as_view(), name='download-sales-invoice-pdf'),
    path('print-pdf/<int:sales_invoice_id>/', PrintSalesInvoicePDFAPIView.as_view(), name='print-sales-invoice-pdf'),
    path('sales-invoice/delete/<str:invoice_number>/', DeleteSalesInvoiceByNumberAPIView.as_view(), name='delete-sales-invoice-by-number'),
    path('payment-terms/', PaymentTermChoicesView.as_view(), name='payment-terms'),
    # convert so to si
    path("sales-orders/<int:sales_order_id>/convert-to-invoice/", ConvertClientSalesOrderToSalesInvoiceAPIView.as_view(), name="convert-sales-order-to-invoice"),
    
    path('invoices/with-amounts/', SalesInvoiceWithAmountsAPIView.as_view(), name='sales-invoice-with-amounts'),
    path('sales-invoices/party/<int:party_id>/', SalesInvoiceWithAmountsByPartyAPIView.as_view(), name='sales-invoices-by-party'),

    #employee access ar url
    path('sales-invoices/sales-person/<int:sales_person_id>/', SalesInvoiceBySalesPersonAPIView.as_view(), name='sales_invoices_by_sales_person'),

    #all sale person api
    path('all-sales-invoices/', AllSalesInvoicesAPIView.as_view(), name='all-sales-invoices'),
    path('sales-persons/totals/', AllSalesPersonsInvoiceTotalsAPIView.as_view(), name='all-sales-persons-invoice-totals'),
]

#add all

