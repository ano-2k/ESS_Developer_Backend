from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Sales_Invoice.models import *
from django.template.loader import render_to_string
import base64
from decimal import Decimal
from io import BytesIO
from xhtml2pdf import pisa
from django.conf import settings
import sib_api_v3_sdk
from .serializers import *
from sib_api_v3_sdk.rest import ApiException
from .models import *  # Ensure all necessary imports are included

class GetUnpaidInvoicesAPIView(APIView):
    """Fetch unpaid and partially paid invoices for a given party with specific fields"""

    def get(self, request, party_id):
        # Fetch invoices with either 'unpaid' or 'partially paid' status
        invoices = SalesInvoice.objects.filter(
            party_id=party_id,
            payment_status__in=["unpaid", "partially_paid"]
        )

        if not invoices.exists():
            return Response({"message": "No unpaid or partially paid invoices found for this party."},
                            status=status.HTTP_404_NOT_FOUND)

        invoices_data = []
        for invoice in invoices:
            total_amount = TotalAmount.objects.filter(sales_invoice=invoice).first()
            invoice_amount = total_amount.total if total_amount else 0.00

            # If partially paid, show balance amount instead
            if invoice.payment_status == "partially_paid":
                invoice_amount = invoice.balance_amount  # assuming this field exists

            invoices_data.append({
                "id": invoice.id,
                "Date": invoice.invoice_date,
                "Invoice_Number": invoice.invoice_number,
                "Invoice_Amount": invoice_amount,
                "Due_Date": invoice.due_date,
                "Payment_Status": invoice.payment_status,
            })

        return Response(invoices_data, status=status.HTTP_200_OK)


    
class UpdatePaymentInAPIView(APIView):
    def patch(self, request, id):
        payment = get_object_or_404(RecordPayment, id=id)
        serializer = CreatePaymentInSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Payment updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePaymentInAPIView(APIView):
    def delete(self, request, id):
        payment = get_object_or_404(RecordPayment, id=id)
        payment.delete()
        return Response({"message": "Payment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    
class DeletePaymentInnoAPIView(APIView):
    def delete(self, request, payment_in_number):
        payment = get_object_or_404(RecordPayment, payment_in_number=payment_in_number)
        payment.delete()
        return Response({"message": "Payment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()

from django.db.models import Sum

from decimal import Decimal

class ConvertSalesInvoiceToPaymentAPIView(APIView):
    def post(self, request, party_id):
        serializer = ConvertSalesInvoiceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        invoice_id = data["invoice_id"]
        payment_amount = Decimal(str(data["payment_amount"]))
        payment_mode = data["payment_mode"]
        notes = data.get("notes", "")
        payment_in_number = data.get("payment_in_number")
        payment_date = data.get("payment_date", timezone.now().date())

        party = get_object_or_404(AddParty, id=party_id)
        sales_invoice = get_object_or_404(SalesInvoice, id=invoice_id, party=party)

        total_amount_obj = TotalAmount.objects.filter(sales_invoice=sales_invoice).first()
        if not total_amount_obj:
            return Response({"error": "Total amount not found for invoice."}, status=status.HTTP_404_NOT_FOUND)

        total_due = total_amount_obj.total
        total_paid = sales_invoice.payments.aggregate(Sum("payment_amount"))["payment_amount__sum"] or Decimal("0.00")
        balance_amount = total_due - total_paid

        if payment_amount <= 0:
            return Response({"error": "Payment amount must be greater than zero."}, status=status.HTTP_400_BAD_REQUEST)

        if payment_amount > balance_amount:
            return Response({
                "error": "Payment amount exceeds remaining balance.",
                "invoice_status": sales_invoice.payment_status,
                "total_due": total_due,
                "total_paid": total_paid,
                "balance_amount": balance_amount
            }, status=status.HTTP_400_BAD_REQUEST)

        if not payment_in_number:
            last_payment = RecordPayment.objects.order_by('-id').first()
            next_number = 1 if not last_payment else int(last_payment.payment_in_number.split('-')[1]) + 1
            payment_in_number = f"PAYIN-{next_number:05d}"

        new_total_paid = total_paid + payment_amount
        payment_status = "paid" if new_total_paid >= total_due else "partially_paid"

        payment = RecordPayment.objects.create(
            party=party,
            sales_invoice=sales_invoice,
            payment_amount=payment_amount,
            payment_mode=payment_mode,
            payment_in_number=payment_in_number,
            payment_date=payment_date,
            notes=notes
        )

        sales_invoice.payment_status = payment_status
        sales_invoice.save(update_fields=["payment_status"])

        # Only Generate PDF and Save it if you want (optional), no email here.
        context = {
            "party_name": party.party_name,
            "payment_in_number": payment.payment_in_number,
            "payment_date": payment.payment_date,
            "payment_mode": payment.payment_mode,
            "payment_amount": payment.payment_amount,
            "notes": payment.notes,
            "business_name": "Suriya Dcruz'e CARGO",
        }

        pdf_content = generate_pdf_from_html(context, "Normal_payment_in_receipt_template.html")

        if not pdf_content:
            return Response({
                "payment_in_number": payment.payment_in_number,
                "status": "created_without_pdf"
            }, status=status.HTTP_201_CREATED)

        # Optional: Save the PDF somewhere if needed.

        return Response({
    "payment_id": payment.id,
    "payment_in_number": payment.payment_in_number,
    "status": "payment_created",
    "sales_invoice": {
        "invoice_id": sales_invoice.id,
        "invoice_number": sales_invoice.invoice_number,
        "invoice_date": sales_invoice.invoice_date,
        "payment_status": sales_invoice.payment_status,
        "total_amount": total_due,
    },
    "party": {
        "party_id": party.id,
        "party_name": party.party_name,
        "email": party.email,
        "mobile_number": party.mobile_number,
        "gstin": party.gstin,
        "pan_number": party.pan_number,
        "party_type": party.party_type,
        "party_category": party.party_category,
        "credit_period_days": party.credit_period_days,
        "credit_limit_rupees": party.credit_limit_rupees,
        "address": {
            "street": party.billing_address.street if party.billing_address else None,
            "city": party.billing_address.city if party.billing_address else None,
            "state": party.billing_address.state if party.billing_address else None,
            "pincode": party.billing_address.pincode if party.billing_address else None,
        }
    }
}, status=status.HTTP_201_CREATED)



class SendPaymentEmailAPIView(APIView):
    def post(self, request, payment_id):
        payment = get_object_or_404(RecordPayment, id=payment_id)
        party = payment.party

        context = {
            "party_name": party.party_name,
            "payment_in_number": payment.payment_in_number,
            "payment_date": payment.payment_date,
            "payment_mode": payment.payment_mode,
            "payment_amount": payment.payment_amount,
            "notes": payment.notes,
            "business_name": "Suriya Dcruz'e CARGO",
        }

        pdf_content = generate_pdf_from_html(context, "Normal_payment_in_receipt_template.html")
        if not pdf_content:
            return Response({"error": "Failed to generate PDF."}, status=status.HTTP_400_BAD_REQUEST)

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            email_data = sib_api_v3_sdk.SendSmtpEmail(
                sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
                to=[{"email": party.email}],
                subject=f"Payment In Received - {payment.payment_in_number}",
                html_content=render_to_string("Normal_payment_in_email_template.html", context),
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Payment_In_{payment.payment_in_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            api_instance.send_transac_email(email_data)

            return Response({"status": "email_sent_successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentInAPIView(APIView):
    """Create a Payment In for a Party without an Invoice"""

    def post(self, request):
        serializer = CreatePaymentInSerializer(data=request.data)
        if serializer.is_valid():
            payment = serializer.save()

            # ✅ Prepare email content
            context = {
                "party_name": payment.party.party_name,
                "payment_in_number": payment.payment_in_number,
                "payment_date": payment.payment_date,
                "payment_mode": payment.payment_mode,
                "payment_amount": payment.payment_amount,
                "notes": payment.notes,
                "business_name": "Suriya Dcruz'e CARGO",
            }

            # ✅ Generate PDF receipt
            pdf_content = generate_pdf_from_html(context, "Normal_payment_in_receipt_template.html")
            if not pdf_content:
                return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

            # ✅ Send email via Brevo
            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key["api-key"] = settings.BREVO_API_KEY
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

                email_data = sib_api_v3_sdk.SendSmtpEmail(
                    sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
                    to=[{"email": payment.party.email}],
                    subject=f"Payment In Received - {payment.payment_in_number}",
                    html_content=render_to_string("Normal_payment_in_email_template.html", context),
                    attachment=[{
                        "content": pdf_base64,
                        "name": f"Payment_In_{payment.payment_in_number}.pdf",
                        "contentType": "application/pdf"
                    }]
                )

                api_instance.send_transac_email(email_data)

                return Response(
                    {"message": "Payment In created and email sent successfully.", "payment_in_number": payment.payment_in_number},
                    status=status.HTTP_201_CREATED
                )

            except ApiException as e:
                return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DownloadPaymentPDFAPIView(APIView):
    """Download Payment In PDF"""

    def get(self, request, payment_in_number):
        payment = get_object_or_404(RecordPayment, payment_in_number=payment_in_number)

        context = {
            "payment_in_number": payment.payment_in_number,
            "payment_date": payment.payment_date,
            "payment_amount": payment.payment_amount,
            "payment_mode": payment.payment_mode,
            "notes": payment.notes,
            "party_name": payment.party.party_name,
            "business_name": "Your Business Name"
        }

        # Generate the PDF using the provided template
        pdf_content = generate_pdf_from_html(context, "payment_in_receipt_template.html")
        
        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response for downloading
        response = Response(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=Payment_In_{payment_in_number}.pdf'
        return response

class PrintPaymentPDFAPIView(APIView):
    """Print Payment In PDF"""

    def get(self, request, payment_in_number):
        payment = get_object_or_404(RecordPayment, payment_in_number=payment_in_number)

        context = {
            "payment_in_number": payment.payment_in_number,
            "payment_date": payment.payment_date,
            "payment_amount": payment.payment_amount,
            "payment_mode": payment.payment_mode,
            "notes": payment.notes,
            "party_name": payment.party.party_name,
            "business_name": "Your Business Name"
        }

        # Generate the PDF using the provided template
        pdf_content = generate_pdf_from_html(context, "payment_in_receipt_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response to be printed
        response = Response(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=Payment_In_{payment_in_number}.pdf'
        return response

class ListPaymentInAPIView(APIView):
    """List all Payment In details"""

    def get(self, request):
        payments = RecordPayment.objects.all().order_by("-id")
        serializer = ListPaymentInSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PaymentsInByPartyView(APIView):
    def get(self, request, party_id):
        payments = RecordPayment.objects.filter(party_id=party_id).order_by('-payment_date')
        serializer = ListPaymentInSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RecordPayment
from .serializers import YearlyRevenueSerializer, MonthlyRevenueSerializer

# View for Yearly Revenue
class YearlyRevenueView(APIView):
    def get(self, request, *args, **kwargs):
        # Aggregate yearly revenue and rename fields to match the serializer
        yearly_revenue = (
            RecordPayment.objects
            .values('payment_date__year')  # Group by year
            .annotate(total_revenue=Sum('payment_amount'))
            .order_by('payment_date__year')
        )

        # Rename the field 'payment_date__year' to 'year'
        for item in yearly_revenue:
            item['year'] = item.pop('payment_date__year')

        # Serialize the data
        serializer = YearlyRevenueSerializer(yearly_revenue, many=True)

        return Response({'yearly_revenue': serializer.data})

# View for Monthly Revenue
class MonthlyRevenueView(APIView):
    def get(self, request, *args, **kwargs):
        # Aggregate monthly revenue and rename fields to match the serializer
        monthly_revenue = (
            RecordPayment.objects
            .values('payment_date__year', 'payment_date__month')  # Group by year and month
            .annotate(total_revenue=Sum('payment_amount'))
            .order_by('payment_date__year', 'payment_date__month')
        )

        # Rename the fields to match the expected names in the serializer
        for item in monthly_revenue:
            item['year'] = item.pop('payment_date__year')
            item['month'] = item.pop('payment_date__month')

        # Serialize the data
        serializer = MonthlyRevenueSerializer(monthly_revenue, many=True)

        return Response({'monthly_revenue': serializer.data})
