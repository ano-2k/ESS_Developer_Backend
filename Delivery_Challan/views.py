import base64
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import sib_api_v3_sdk
from django.db.models import Sum
from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
from .models import *
from .serializers import *

class CombinedDeliveryChallanCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Create Delivery Challan and its items in one request"""
        
        # Validate and process the data coming from the request
        serializer = CombinedDeliveryChallanSerializer(data=request.data)
        
        # Check if the serializer is valid
        if serializer.is_valid():
            # Save the Delivery Challan and its related items
            delivery_challan = serializer.save()
            
            # Optionally, check if a TotalAmount entry exists for the Delivery Challan
            total_amount_obj, created = DeliveryChallanTotalAmount.objects.get_or_create(
                delivery_challan=delivery_challan
            )
            
            if created:
                # If the TotalAmount didn't exist, calculate the total and save
                total_amount = delivery_challan.delivery_challan_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
                total_amount_obj.total = total_amount
                total_amount_obj.save()
            else:
                # If TotalAmount exists, update the total
                total_amount = delivery_challan.delivery_challan_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
                total_amount_obj.total = total_amount
                total_amount_obj.save()
            
            # Return the response with serialized data
            response_serializer = DeliveryChallanResponseSerializer(delivery_challan)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        # If data is invalid, return errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CombinedDeliveryChallanUpdateAPIView(APIView):
    def put(self, request, pk, *args, **kwargs):
        """Update existing Delivery Challan and its items"""
        try:
            instance = DeliveryChallan.objects.get(pk=pk)
        except DeliveryChallan.DoesNotExist:
            return Response({"error": "Delivery Challan not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CombinedDeliveryChallanSerializer(instance, data=request.data)
        
        if serializer.is_valid():
            delivery_challan = serializer.save()
            
            # Update or create total amount
            total_amount_obj, _ = DeliveryChallanTotalAmount.objects.get_or_create(
                delivery_challan=delivery_challan
            )
            total_amount = delivery_challan.delivery_challan_items.aggregate(Sum("amount"))["amount__sum"] or 0.00
            total_amount_obj.total = total_amount
            total_amount_obj.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveDeliveryChallanAPIView(APIView):
    def post(self, request):
        """ Retrieve a delivery challan along with its related items """
        challan_id = request.data.get("challan_id")  # Get from JSON body
        
        if not challan_id:
            return Response({"error": "challan_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        challan = get_object_or_404(DeliveryChallan, id=challan_id)
        serializer = DeliveryChallanSerializer(challan)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeliveryChallanListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        delivery_challans = DeliveryChallan.objects.all().order_by('-id')
        serializer = DeliveryChallanDetailSerializer(delivery_challans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class DeliveryChallanUpdateAPIView(APIView):
    def patch(self, request, id):
        delivery_challan = get_object_or_404(DeliveryChallan, id=id)
        serializer = CombinedDeliveryChallanSerializer(delivery_challan, data=request.data, partial=True)

        if serializer.is_valid():
            updated_challan = serializer.save()

            # Recalculate total amount
            total_amount = updated_challan.delivery_challan_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
            DeliveryChallanTotalAmount.objects.update_or_create(
                delivery_challan=updated_challan,
                defaults={"total": total_amount}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        delivery_challan = get_object_or_404(DeliveryChallan, id=id)
        serializer = CombinedDeliveryChallanSerializer(delivery_challan, data=request.data)

        if serializer.is_valid():
            updated_challan = serializer.save()

            total_amount = updated_challan.delivery_challan_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
            DeliveryChallanTotalAmount.objects.update_or_create(
                delivery_challan=updated_challan,
                defaults={"total": total_amount}
            )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryChallanDeleteAPIView(APIView):
    def delete(self, request, id):
        delivery_challan = get_object_or_404(DeliveryChallan, id=id)

        # Optional: delete related total amount
        DeliveryChallanTotalAmount.objects.filter(delivery_challan=delivery_challan).delete()
        
        delivery_challan.delete()
        return Response({"message": "Delivery Challan deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
class DeliveryChallanDeleteByNumberAPIView(APIView):
    def delete(self, request, delivery_challan_number):
        delivery_challan = get_object_or_404(DeliveryChallan, delivery_challan_number=delivery_challan_number)

        # Optional: Delete related total amount
        DeliveryChallanTotalAmount.objects.filter(delivery_challan=delivery_challan).delete()

        delivery_challan.delete()
        return Response({"message": "Delivery Challan deleted successfully."}, status=status.HTTP_204_NO_CONTENT)




def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()


class SendDeliveryChallanEmailAPIView(APIView):
    def post(self, request, delivery_challan_id):
        """Send a delivery challan email with a PDF attachment via Brevo"""
        delivery_challan = get_object_or_404(DeliveryChallan, id=delivery_challan_id)

        # Fetch items directly from the database
        items = DeliveryChallanItem.objects.filter(delivery_challan=delivery_challan)

        if not items:
            return Response({"error": "Delivery Challan has no items."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the final total
        final_total = sum(item.amount for item in items)

        # Prepare context for the email and PDF generation
        context = {
            "delivery_challan_number": delivery_challan.delivery_challan_number,
            "delivery_challan_date": delivery_challan.delivery_challan_date,
            "party_name": delivery_challan.party_name,
            "party_mobile_number": delivery_challan.party_mobile_number,
            "shipping_address": delivery_challan.shipping_address,
            "delivery_challan_items": items,  # Use the correct field for items
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Render email content using the delivery challan email template
        email_content = render_to_string("delivery_challan_email_template.html", context)

        # Generate PDF content using the delivery challan PDF template
        pdf_content = generate_pdf_from_html(context, "delivery_challan_pdf_template.html")
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
                to=[{"email": delivery_challan.party.email}],
                subject=f"Delivery Challan {delivery_challan.delivery_challan_number}",
                html_content=email_content,  # HTML content from the template
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Delivery_Challan_{delivery_challan.delivery_challan_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            # Send the email via Brevo API
            api_response = api_instance.send_transac_email(email_data)
            print(f"Brevo API Response: {api_response}")

            return Response({"message": "Delivery challan email sent successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

