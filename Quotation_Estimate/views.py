import base64
from email.message import EmailMessage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


class RetrieveQuotationEstimateAPIView(APIView):
    def post(self, request):
        """ Retrieve a quotation estimate along with its related items """
        quotation_id = request.data.get("quotation_id")

        if not quotation_id:
            return Response({"error": "quotation_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        quotation = get_object_or_404(QuotationEstimate, id=quotation_id)
        serializer = QuotationEstimateSerializer(quotation)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CombinedQuotationEstimateCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CombinedQuotationEstimateSerializer(data=request.data)

        if serializer.is_valid():
            quotation = serializer.save()  # Save the main quotation
            response_serializer = QuotationEstimateResponseSerializer(quotation)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CombinedQuotationEstimateUpdateAPIView(APIView):
    def put(self, request, pk, *args, **kwags):
        """Update existing Quotation Estimate and its items"""
        try:
            instance = QuotationEstimate.objects.get(pk=pk)
        except QuotationEstimate.DoesNotExist:
            return Response({"error": "QuotationEstimate not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CombinedQuotationEstimateSerializer(instance, data=request.data)
        
        if serializer.is_valid():
            updated_quotation = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()

class SendQuotationEstimateEmailAPIView(APIView):
    def post(self, request, quotation_id):
        """Send a quotation estimate email with a PDF attachment via Brevo"""
        quotation = get_object_or_404(QuotationEstimate, id=quotation_id)

        # Fetch items directly from the database
        items = list(QuotationEstimateItem.objects.filter(quotation=quotation).values(
            "item_name", "quantity", "price_per_item", "discount", "tax", "amount"
        ))

        if not items:
            return Response({"error": "Quotation Estimate has no items."}, status=status.HTTP_400_BAD_REQUEST)

        final_total = sum(float(item.get("amount", 0.0)) for item in items)

        context = {
            "quotation_number": quotation.quotation_number,
            "quotation_date": quotation.quotation_date,
            "party_name": quotation.party_name,
            "party_mobile_number": quotation.party_mobile_number,
            "shipping_address": quotation.shipping_address,
            "quotation_items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"  # Replace with your business name
        }

        # Render email content using the quotation email template
        email_content = render_to_string("email_template.html", context)

        # Generate PDF content using the same context and PDF template
        pdf_content = self.generate_pdf_from_html(context, "quotation_pdf_template.html")
        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        try:
            # Set up Brevo API configuration
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            # Prepare the email data (subject, sender, recipient, body, and attachment)
            email_data = sib_api_v3_sdk.SendSmtpEmail(
                sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
                to=[{"email": quotation.party.email}],
                subject=f"Quotation Estimate {quotation.quotation_number}",
                html_content=email_content,  # HTML content from the template
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Quotation_{quotation.quotation_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            # Send the email via Brevo API
            api_response = api_instance.send_transac_email(email_data)
            print(f"Brevo API Response: {api_response}")

            return Response({"message": "Quotation estimate email sent successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_pdf_from_html(self, context, template_name):
        """Helper function to generate PDF from HTML template"""
        # Render the template to HTML
        html = render_to_string(template_name, context)
        result = BytesIO()
        
        # Generate PDF using xhtml2pdf
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if pdf.err:
            return None
        return result.getvalue()

class GetAllQuotationEstimatesView(APIView):
    """API View to retrieve all QuotationEstimates"""
    
    def get(self, request, *args, **kwargs):
        quotation_estimates = QuotationEstimate.objects.all()
        serializer = QuotationEstimateSerializer(quotation_estimates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetQuotationEstimateByIdView(APIView):
    """API View to retrieve QuotationEstimate by ID"""
    
    def get(self, request, quotation_estimate_id, *args, **kwargs):
        quotation_estimate = get_object_or_404(QuotationEstimate, id=quotation_estimate_id)
        serializer = QuotationEstimateSerializer(quotation_estimate)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateQuotationEstimateByIdView(APIView):
    """API View to update QuotationEstimate and its items by ID"""
    
    def put(self, request, quotation_estimate_id, *args, **kwargs):
        quotation_estimate = get_object_or_404(QuotationEstimate, id=quotation_estimate_id)
        
        # Use CombinedQuotationEstimateSerializer to support nested updates
        serializer = CombinedQuotationEstimateSerializer(quotation_estimate, data=request.data, partial=True)

        if serializer.is_valid():
            updated_quotation_estimate = serializer.save()
            return Response(
                {
                    "message": "QuotationEstimate updated successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteQuotationEstimateByIdView(APIView):
    """API View to delete QuotationEstimate and its related items by ID"""
    
    def delete(self, request, quotation_estimate_id, *args, **kwargs):
        quotation_estimate = get_object_or_404(QuotationEstimate, id=quotation_estimate_id)
        
        # If needed, manually delete related items
        # quotation_estimate.quotation_items.all().delete()  # Uncomment if needed
        
        quotation_estimate.delete()
        return Response(
            {"message": "QuotationEstimate deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT
        )

class DeleteQuotationEstimateByNumberView(APIView):
    """API View to delete QuotationEstimate by quotation_number"""

    def delete(self, request, quotation_number, *args, **kwargs):
        quotation_estimate = get_object_or_404(QuotationEstimate, quotation_number=quotation_number)
        
        # Optional: Delete related items
        # quotation_estimate.quotation_items.all().delete()  # Uncomment if necessary
        
        quotation_estimate.delete()
        return Response(
            {"message": "QuotationEstimate deleted successfully!"},
            status=status.HTTP_204_NO_CONTENT
        )

class GetQuotationEstimatesByPartyIdView(APIView):
    """API View to retrieve all QuotationEstimates by Party ID"""
    
    def get(self, request, party_id, *args, **kwargs):
        quotation_estimates = QuotationEstimate.objects.filter(party__id=party_id)
        
        if not quotation_estimates.exists():
            return Response({"error": "No quotation estimates found for this party."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuotationEstimateSerializer(quotation_estimates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateQuotationEstimatesByPartyIdView(APIView):
    """API View to update QuotationEstimate by Party ID"""
    
    def put(self, request, party_id, *args, **kwargs):
        # Fetch the quotation estimate for the given Party ID
        quotation_estimate = get_object_or_404(QuotationEstimate, party__id=party_id)
        
        # Serialize and update the data
        serializer = QuotationEstimateSerializer(quotation_estimate, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_quotation_estimate = serializer.save()
            return Response(
                {"message": "QuotationEstimate updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteQuotationEstimatesByPartyIdView(APIView):
    """API View to delete QuotationEstimate by Party ID"""
    
    def delete(self, request, party_id, *args, **kwargs):
        quotation_estimate = get_object_or_404(QuotationEstimate, party__id=party_id)
        quotation_estimate.delete()
        return Response({"message": "QuotationEstimate deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class DownloadQuotationEstimatePDFAPIView(APIView):
    """API view to generate and download QuotationEstimate PDF"""

    def get(self, request, quotation_estimate_id, *args, **kwargs):
        """Generate and download PDF for the QuotationEstimate"""

        # Get the QuotationEstimate
        quotation_estimate = get_object_or_404(QuotationEstimate, id=quotation_estimate_id)

        # Fetch items associated with the quotation
        items = QuotationEstimateItem.objects.filter(quotation=quotation_estimate)

        # Calculate the final total for the quotation
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "quotation_number": quotation_estimate.quotation_number,
            "quotation_date": quotation_estimate.quotation_date,
            "party_name": quotation_estimate.party_name,
            "party_mobile_number": quotation_estimate.party_mobile_number,
            "shipping_address": quotation_estimate.shipping_address,
            "quotation_items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"  # Replace with your business name
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "quotation_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response for downloading
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=quotation_{quotation_estimate.quotation_number}.pdf'
        return response

class PrintQuotationEstimatePDFAPIView(APIView):
    """API view to generate and print QuotationEstimate PDF"""

    def get(self, request, quotation_estimate_id, *args, **kwargs):
        """Generate PDF for QuotationEstimate and open print dialog"""

        # Get the QuotationEstimate
        quotation_estimate = get_object_or_404(QuotationEstimate, id=quotation_estimate_id)

        # Fetch items associated with the quotation
        items = QuotationEstimateItem.objects.filter(quotation=quotation_estimate)

        # Calculate the final total for the quotation
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "quotation_number": quotation_estimate.quotation_number,
            "quotation_date": quotation_estimate.quotation_date,
            "party_name": quotation_estimate.party_name,
            "party_mobile_number": quotation_estimate.party_mobile_number,
            "shipping_address": quotation_estimate.shipping_address,
            "quotation_items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"  # Replace with your business name
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "quotation_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response to be printed
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=quotation_{quotation_estimate.quotation_number}.pdf'
        return response
