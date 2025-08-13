from django.urls import path
from .views import *

urlpatterns = [
    path('retrieve/', RetrieveQuotationEstimateAPIView.as_view(), name="retrieve_quotation_estimate"),
    path('send_email/<int:quotation_id>/', SendQuotationEstimateEmailAPIView.as_view(), name="send_quotation_estimate_email"),
    path('quotation/', CombinedQuotationEstimateCreateAPIView.as_view(), name='combined-quotation-estimate-create'),
    path('quotation-estimates/', GetAllQuotationEstimatesView.as_view(), name='get-all-quotation-estimates'),  # GET all
    path('quotation-estimate/<int:quotation_estimate_id>/', GetQuotationEstimateByIdView.as_view(), name='get-quotation-estimate-by-id'),  # GET by ID
    path('quotation-estimate/update/<int:quotation_estimate_id>/', UpdateQuotationEstimateByIdView.as_view(), name='update-quotation-estimate-by-id'),  # PUT by ID
    path('quotation-estimate/delete/<int:quotation_estimate_id>/', DeleteQuotationEstimateByIdView.as_view(), name='delete-quotation-estimate-by-id'),  # DELETE by ID
    path('quotation-estimates/party/<int:party_id>/', GetQuotationEstimatesByPartyIdView.as_view(), name='get-quotation-estimates-by-party-id'),  # GET by Party ID
    path('quotation-estimates/update/party/<int:party_id>/', UpdateQuotationEstimatesByPartyIdView.as_view(), name='update-quotation-estimates-by-party-id'),  # PUT by Party ID
    path('quotation-estimates/delete/party/<int:party_id>/', DeleteQuotationEstimatesByPartyIdView.as_view(), name='delete-quotation-estimates-by-party-id'),  # DELETE by Party ID
     # Download PDF
    path('download-pdf/<int:quotation_estimate_id>/', DownloadQuotationEstimatePDFAPIView.as_view(), name='download-quotation-pdf'),
    # Print PDF (open in a new window and print)
    path('print-pdf/<int:quotation_estimate_id>/', PrintQuotationEstimatePDFAPIView.as_view(), name='print-quotation-pdf'),
     path("quotation-estimate/delete/<str:quotation_number>/",DeleteQuotationEstimateByNumberView.as_view(),name="delete-quotation-estimate-by-number"),
     path('quotation-estimate/<int:pk>/update/', CombinedQuotationEstimateUpdateAPIView.as_view(), name='quotation-estimate-update'),
]
