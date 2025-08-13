import base64
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import sib_api_v3_sdk
from django.db.models import Sum

from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from Quotation_Estimate.models import *

class CombinedProformaInvoiceCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Create Proforma Invoice and its items in one request"""
        
        # Validate and process the data coming from the request
        serializer = CombinedProformaInvoiceSerializer(data=request.data)
        
        # Check if the serializer is valid
        if serializer.is_valid():
            # Save the Proforma Invoice and its related items
            proforma_invoice = serializer.save()
            
            # Optionally, check if a TotalAmount entry exists for the Proforma Invoice
            total_amount_obj, created = ProformaTotalAmount.objects.get_or_create(
                proforma_invoice=proforma_invoice
            )
            
            if created:
                # If the TotalAmount didn't exist, calculate the total and save
                total_amount = proforma_invoice.proforma_invoice_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
                total_amount_obj.total = total_amount
                total_amount_obj.save()
            else:
                # If TotalAmount exists, update the total
                total_amount = proforma_invoice.proforma_invoice_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
                total_amount_obj.total = total_amount
                total_amount_obj.save()
            
            # Return the response with serialized data
            response_serializer = ProformaInvoiceResponseSerializer(proforma_invoice)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CombinedProformaInvoiceUpdateAPIView(APIView):
    def put(self, request, pk, *args, **kwargs):
        """Update existing Proforma Invoice and its items"""
        try:
            instance = ProformaInvoice.objects.get(pk=pk)
        except ProformaInvoice.DoesNotExist:
            return Response({"error": "ProformaInvoice not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CombinedProformaInvoiceSerializer(instance, data=request.data)
        
        if serializer.is_valid():
            proforma_invoice = serializer.save()
            
            # Update or create total amount
            total_amount_obj, _ = ProformaTotalAmount.objects.get_or_create(
                proforma_invoice=proforma_invoice
            )
            total_amount = proforma_invoice.proforma_invoice_items.aggregate(Sum("amount"))["amount__sum"] or 0.00
            total_amount_obj.total = total_amount
            total_amount_obj.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RetrieveProformaInvoiceAPIView(APIView):
    def post(self, request):
        """ Retrieve a proforma invoice along with its related items """
        proforma_invoice_id = request.data.get("proforma_invoice_id")  # Get from JSON body
        
        if not proforma_invoice_id:
            return Response({"error": "proforma_invoice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)
        serializer = ProformaInvoiceSerializer(proforma_invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)


def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()


class SendProformaInvoiceEmailAPIView(APIView):
    def post(self, request, proforma_invoice_id):
        """Send a proforma invoice email with a PDF attachment via Brevo"""
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)

        # Fetch items directly from the database
        items = ProformaInvoiceItem.objects.filter(proforma_invoice=proforma_invoice)

        if not items:
            return Response({"error": "Proforma Invoice has no items."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the final total
        final_total = sum(item.amount for item in items)

        # Prepare context for the email and PDF generation
        context = {
            "proforma_invoice_number": proforma_invoice.proforma_invoice_number,
            "proforma_invoice_date": proforma_invoice.proforma_invoice_date,
            "party_name": proforma_invoice.party_name,
            "party_mobile_number": proforma_invoice.party_mobile_number,
            "shipping_address": proforma_invoice.shipping_address,
            "proforma_invoice_items": items,  # Use the correct field for items
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Render email content using the proforma invoice email template
        email_content = render_to_string("proforma_invoice_email_template.html", context)

        # Generate PDF content using the proforma invoice PDF template
        pdf_content = generate_pdf_from_html(context, "proforma_invoice_pdf_template.html")
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
                to=[{"email": proforma_invoice.party.email}],
                subject=f"Proforma Invoice {proforma_invoice.proforma_invoice_number}",
                html_content=email_content,  # HTML content from the template
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Proforma_Invoice_{proforma_invoice.proforma_invoice_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            # Send the email via Brevo API
            api_response = api_instance.send_transac_email(email_data)
            print(f"Brevo API Response: {api_response}")

            return Response({"message": "Proforma invoice email sent successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetProformaInvoicesByPartyIdAPIView(APIView):
    """API View to retrieve all ProformaInvoices by Party ID"""
    
    def get(self, request, party_id, *args, **kwargs):
        proforma_invoices = ProformaInvoice.objects.filter(party_id=party_id)
        
        if not proforma_invoices.exists():
            return Response({"error": "No Proforma Invoices found for this Party."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProformaInvoiceSerializer(proforma_invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetProformaInvoiceByIdAPIView(APIView):
    """API View to retrieve a ProformaInvoice by ID"""
    
    def get(self, request, proforma_invoice_id, *args, **kwargs):
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)
        serializer = ProformaInvoiceSerializer(proforma_invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProformaInvoiceByIdAPIView(APIView):
    """API View to update ProformaInvoice by ID"""

    def patch(self, request, proforma_invoice_id, *args, **kwargs):
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)
        serializer = CombinedProformaInvoiceSerializer(proforma_invoice, data=request.data, partial=True)

        if serializer.is_valid():
            updated_proforma_invoice = serializer.save()

            # Recalculate and update total amount
            total_amount = updated_proforma_invoice.proforma_invoice_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
            ProformaTotalAmount.objects.update_or_create(
                proforma_invoice=updated_proforma_invoice,
                defaults={"total": total_amount}
            )

            return Response({
                "message": "ProformaInvoice updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteProformaInvoiceByIdAPIView(APIView):
    """API View to delete ProformaInvoice by ID"""

    def delete(self, request, proforma_invoice_id, *args, **kwargs):
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)

        # Optionally delete the total amount object if needed
        ProformaTotalAmount.objects.filter(proforma_invoice=proforma_invoice).delete()
        
        proforma_invoice.delete()
        return Response({"message": "ProformaInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

# views.py
class DeleteProformaInvoiceByNumberAPIView(APIView):
    def delete(self, request, proforma_invoice_number, *args, **kwargs):
        proforma_invoice = get_object_or_404(ProformaInvoice, proforma_invoice_number=proforma_invoice_number)

        # Delete related total amount if applicable
        ProformaTotalAmount.objects.filter(proforma_invoice=proforma_invoice).delete()

        proforma_invoice.delete()
        return Response({"message": "ProformaInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)



class GetProformaInvoicesByPartyIdAPIView(APIView):
    """API View to retrieve all ProformaInvoices by Party ID"""
    
    def get(self, request, party_id, *args, **kwargs):
        proforma_invoices = ProformaInvoice.objects.filter(party__id=party_id)
        
        if not proforma_invoices.exists():
            return Response({"error": "No Proforma Invoices found for this Party."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProformaInvoiceSerializer(proforma_invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateProformaInvoicesByPartyIdAPIView(APIView):
    """API View to update ProformaInvoices by Party ID"""
    
    def put(self, request, party_id, *args, **kwargs):
        # Fetch ProformaInvoice by Party ID and update
        proforma_invoice = get_object_or_404(ProformaInvoice, party__id=party_id)
        serializer = ProformaInvoiceSerializer(proforma_invoice, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_proforma_invoice = serializer.save()
            return Response({"message": "ProformaInvoice updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteProformaInvoicesByPartyIdAPIView(APIView):
    """API View to delete ProformaInvoices by Party ID"""
    
    def delete(self, request, party_id, *args, **kwargs):
        proforma_invoice = get_object_or_404(ProformaInvoice, party__id=party_id)
        proforma_invoice.delete()
        return Response({"message": "ProformaInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class DownloadProformaInvoicePDFAPIView(APIView):
    """API view to generate and download ProformaInvoice PDF"""

    def get(self, request, proforma_invoice_id, *args, **kwargs):
        """Generate and download PDF for a ProformaInvoice"""

        # Get the ProformaInvoice
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)

        # Fetch items associated with the invoice
        items = ProformaInvoiceItem.objects.filter(proforma_invoice=proforma_invoice)

        # Calculate the final total for the invoice
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "proforma_invoice_number": proforma_invoice.proforma_invoice_number,
            "proforma_invoice_date": proforma_invoice.proforma_invoice_date,
            "party_name": proforma_invoice.party_name,
            "shipping_address": proforma_invoice.shipping_address,
            "items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "proforma_invoice_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response for downloading
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=proforma_invoice_{proforma_invoice.proforma_invoice_number}.pdf'
        return response

class PrintProformaInvoicePDFAPIView(APIView):
    """API view to generate and print ProformaInvoice PDF"""

    def get(self, request, proforma_invoice_id, *args, **kwargs):
        """Generate PDF for ProformaInvoice and open print dialog"""

        # Get the ProformaInvoice
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)

        # Fetch items associated with the invoice
        items = ProformaInvoiceItem.objects.filter(proforma_invoice=proforma_invoice)

        # Calculate the final total for the invoice
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "proforma_invoice_number": proforma_invoice.proforma_invoice_number,
            "proforma_invoice_date": proforma_invoice.proforma_invoice_date,
            "party_name": proforma_invoice.party_name,
            "shipping_address": proforma_invoice.shipping_address,
            "items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "proforma_invoice_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response to be printed
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=proforma_invoice_{proforma_invoice.proforma_invoice_number}.pdf'
        return response

class ProformaInvoiceListAPIView(APIView):
    """
    API view to retrieve all Proforma Invoices along with related details.
    """

    def get(self, request, *args, **kwargs):
        """
        Get the list of all proforma invoices along with their items and total amount.
        """
        try:
            proforma_invoices = ProformaInvoice.objects.all()
            serializer = ProformaInvoiceSerializer(proforma_invoices, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)