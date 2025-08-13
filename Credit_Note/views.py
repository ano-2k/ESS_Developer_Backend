import base64
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from .models import *
from .serializers import *

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .serializers import CombinedCreditNoteSerializer, CreditNoteResponseSerializer
from .models import CreditNoteTotalAmount

class CombinedCreditNoteCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Create Credit Note and its items in one request"""
        
        with transaction.atomic():
            serializer = CombinedCreditNoteSerializer(data=request.data)
            
            if serializer.is_valid():
                credit_note = serializer.save()

                total = credit_note.credit_note_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
                total_amount_obj, _ = CreditNoteTotalAmount.objects.get_or_create(credit_note=credit_note)
                total_amount_obj.total = total
                total_amount_obj.save()

                credit_note.refresh_from_db()  # ✅ Ensure fresh data for response

                response_serializer = CreditNoteResponseSerializer(credit_note)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class CombinedCreditNoteUpdateAPIView(APIView):
    def put(self, request, pk, *args, **kwargs):
        """Update an existing Credit Note and its items"""
        
        # Fetch the existing credit note
        credit_note_instance = get_object_or_404(CreditNote, pk=pk)
        
        # Validate and process the update data
        serializer = CombinedCreditNoteSerializer(credit_note_instance, data=request.data)
        
        if serializer.is_valid():
            # Save updated credit note and its related items
            credit_note = serializer.save()

            # Recalculate and update the total amount
            total_amount_obj, created = CreditNoteTotalAmount.objects.get_or_create(
                credit_note=credit_note
            )

            total_amount = credit_note.credit_note_items.aggregate(
                models.Sum("amount")
            )["amount__sum"] or 0.00

            total_amount_obj.total = total_amount
            total_amount_obj.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveCreditNoteAPIView(APIView):
    def post(self, request):
        """ Retrieve a credit note along with its related items """
        credit_note_id = request.data.get("credit_note_id")  # Get from JSON body
        
        if not credit_note_id:
            return Response({"error": "credit_note_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        credit_note = get_object_or_404(CreditNote, id=credit_note_id)
        serializer = CreditNoteSerializer(credit_note)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreditNotesByPartyView(APIView):
    def get(self, request, party_id):
        creditnotes = CreditNote.objects.filter(party_id=party_id)
        serializer = CreditNoteSerializer(creditnotes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()


class SendCreditNoteEmailAPIView(APIView):
    def post(self, request, credit_note_id):
        """Send a credit note email with a PDF attachment via Brevo"""
        credit_note = get_object_or_404(CreditNote, id=credit_note_id)

        # Fetch items directly from the database
        items = CreditNoteItem.objects.filter(credit_note=credit_note)

        if not items:
            return Response({"error": "Credit Note has no items."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the final total
        final_total = sum(item.amount for item in items)

        # Prepare context for the email and PDF generation
        context = {
            "credit_note_number": credit_note.credit_note_number,
            "credit_note_date": credit_note.credit_note_date,
            "party_name": credit_note.party_name,
            "party_mobile_number": credit_note.party_mobile_number,
            "shipping_address": credit_note.shipping_address,
            "credit_note_items": items,  # Use the correct field for items
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Render email content using the credit note email template
        email_content = render_to_string("credit_note_email_template.html", context)

        # Generate PDF content using the credit note PDF template
        pdf_content = generate_pdf_from_html(context, "credit_note_pdf_template.html")
        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Base64 encode the PDF content
        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        try:
            # Set up Brevo API configuration
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            # Prepare email data (subject, sender, recipient, body, and attachment)
            email_data = sib_api_v3_sdk.SendSmtpEmail(
                sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
                to=[{"email": credit_note.party.email}],
                subject=f"Credit Note {credit_note.credit_note_number}",
                html_content=email_content,  # HTML content from the template
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Credit_Note_{credit_note.credit_note_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            # Send the email via Brevo API
            api_response = api_instance.send_transac_email(email_data)
            print(f"Brevo API Response: {api_response}")

            return Response({"message": "Credit Note email sent successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreditNotesListAPIView(APIView):
    """
    API view to retrieve a list of credit notes with related items and total amounts.
    """

    def get(self, request, *args, **kwargs):
        # Retrieve all credit notes with their related CreditNoteItem and CreditNoteTotalAmount
        credit_notes = CreditNote.objects.all().prefetch_related(
            'credit_note_items',  # Prefetch related CreditNoteItem objects
            'total_amount'  # Prefetch related CreditNoteTotalAmount objects
        )
        # Serialize the data using the CreditNoteSerializer
        serializer = CreditNoteSerializer(credit_notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class CreditNoteUpdateAPIView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        """Update a Credit Note by ID"""
        try:
            credit_note = CreditNote.objects.get(pk=pk)
        except CreditNote.DoesNotExist:
            return Response({"error": "Credit Note not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CombinedCreditNoteSerializer(credit_note, data=request.data, partial=True)
        if serializer.is_valid():
            credit_note = serializer.save()

            # Update total amount after update
            total = credit_note.credit_note_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
            CreditNoteTotalAmount.objects.update_or_create(
                credit_note=credit_note,
                defaults={"total": total}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreditNoteDeleteAPIView(APIView):
    def delete(self, request, pk, *args, **kwargs):
        """Delete a Credit Note by ID"""
        try:
            credit_note = CreditNote.objects.get(pk=pk)
        except CreditNote.DoesNotExist:
            return Response({"error": "Credit Note not found."}, status=status.HTTP_404_NOT_FOUND)

        credit_note.delete()
        return Response({"message": "Credit Note deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class CreditNoteDeleteByNumberAPIView(APIView):
    """Delete a Credit Note by credit_note_number"""

    def delete(self, request, credit_note_number, *args, **kwargs):
        credit_note = get_object_or_404(CreditNote, credit_note_number=credit_note_number)
        credit_note.delete()
        return Response({"message": "Credit Note deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
