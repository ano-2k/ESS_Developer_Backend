from django.urls import path
from .views import *

urlpatterns = [
    # Create Credit Note
    path('create/', CombinedCreditNoteCreateAPIView.as_view(), name="create_credit_note"),
    
    # Retrieve Credit Note by ID
    path('retrieve/', RetrieveCreditNoteAPIView.as_view(), name="retrieve_credit_note"),
    path('credit-note/<int:pk>/update/',CombinedCreditNoteUpdateAPIView.as_view(),name='credit-note-update'),
    
    # Send Credit Note Email with PDF
    path('send-email/<int:credit_note_id>/', SendCreditNoteEmailAPIView.as_view(), name="send_credit_note_email"),

    path('list/', CreditNotesListAPIView.as_view(), name="credit_notes_list"),
    path('credit-notes/<int:pk>/update/', CreditNoteUpdateAPIView.as_view(), name='update-credit-note'),
    path('credit-notes/<int:pk>/delete/', CreditNoteDeleteAPIView.as_view(), name='delete-credit-note'),
    path('creditnotes/party/<int:party_id>/', CreditNotesByPartyView.as_view(), name='creditnotes-by-party'),
     path("credit-note/delete/<str:credit_note_number>/",CreditNoteDeleteByNumberAPIView.as_view(),name="delete-credit-note-by-number"),
]
