import base64
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from ClientPurchaseOrder.models import *
from Delivery_Challan.models import *
from .models import *
from .serializers import *
import sib_api_v3_sdk
from Sales_Order.models import *
from sib_api_v3_sdk.rest import ApiException
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.db import transaction
from datetime import timedelta
from django.conf import settings
from Quotation_Estimate.models import *
from Proforma_Invoice.models import *
 
from decimal import Decimal
from django.db.models import Sum

class CombinedSalesInvoiceCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        """Create Sales Invoice and its items in one request"""

        serializer = CombinedSalesInvoiceSerializer(data=request.data)

        if serializer.is_valid():
            # Save the SalesInvoice and its related items
            sales_invoice = serializer.save()

            # Get or create the total amount for this invoice
            total_amount_obj, created = TotalAmount.objects.get_or_create(
                sales_invoice=sales_invoice
            )

            total_amount = sales_invoice.sales_invoice_items.aggregate(
                models.Sum("amount")
            )["amount__sum"] or 0.00

            total_amount_obj.total = total_amount
            total_amount_obj.save()

            # ✅ Update SalesPerson's total_sales
            salesperson = sales_invoice.sales_person
            if salesperson:
                total_sales = TotalAmount.objects.filter(
                    sales_invoice__sales_person=salesperson
                ).aggregate(
                    total=Sum("total")
                )["total"] or Decimal("0.00")

                salesperson.total_sales = total_sales
                salesperson.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CombinedSalesInvoiceUpdateAPIView(APIView):
    def put(self, request, pk, *args, **kwargs):
        """Update existing Sales Invoice and its items"""
        try:
            instance = SalesInvoice.objects.get(id=pk)
        except SalesInvoice.DoesNotExist:
            return Response({"error": "SalesInvoice not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CombinedSalesInvoiceSerializer(instance, data=request.data)
        
        if serializer.is_valid():
            updated_invoice = serializer.save()

            total_amount = updated_invoice.sales_invoice_items.aggregate(
                models.Sum("amount")
            )["amount__sum"] or 0.00
            
            TotalAmount.objects.update_or_create(
                sales_invoice=updated_invoice,
                defaults={"total": total_amount}
            )
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RetrieveSalesInvoiceAPIView(APIView):
    def post(self, request):
        """ Retrieve a sales invoice along with its related items """
        invoice_id = request.data.get("invoice_id")  # Get from JSON body
        
        if not invoice_id:
            return Response({"error": "invoice_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        invoice = get_object_or_404(SalesInvoice, id=invoice_id)
        serializer = SalesInvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
def generate_pdf_from_html(context, template_name):
    """Helper function to generate PDF from HTML template"""
    html = render_to_string(template_name, context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if pdf.err:
        return None
    return result.getvalue()


class SendSalesInvoiceEmailAPIView(APIView):
    def post(self, request, invoice_id):
        """Send a sales invoice email with a PDF attachment via Brevo"""
        invoice = get_object_or_404(SalesInvoice, id=invoice_id)

        # Fetch items directly from the database
        items = list(SalesInvoiceItem.objects.filter(sales_invoice=invoice).values(
            "item_name", "quantity", "price_per_item", "tax", "amount"
        ))

        if not items:
            return Response({"error": "Sales Invoice has no items."}, status=status.HTTP_400_BAD_REQUEST)

        final_total = sum(float(item.get("amount", 0.0)) for item in items)

        context = {
            "invoice_number": invoice.invoice_number,
            "invoice_date": invoice.invoice_date,
            "party_name": invoice.party_name,
            "shipping_address": invoice.shipping_address,
            "items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Render email content
        email_content = render_to_string("sales_invoice_email_template.html", context)

        # Generate PDF
        pdf_content = generate_pdf_from_html(context, "sales_invoice_pdf_template.html")
        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        pdf_base64 = base64.b64encode(pdf_content).decode("utf-8")

        try:
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key["api-key"] = settings.BREVO_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

            email_data = sib_api_v3_sdk.SendSmtpEmail(
                sender={"name": settings.BREVO_SENDER_NAME, "email": settings.BREVO_SENDER_EMAIL},
                to=[{"email": invoice.party.email}],
                subject=f"Sales Invoice {invoice.invoice_number}",
                html_content=email_content,
                attachment=[{
                    "content": pdf_base64,
                    "name": f"Invoice_{invoice.invoice_number}.pdf",
                    "contentType": "application/pdf"
                }]
            )

            api_response = api_instance.send_transac_email(email_data)
            print(f"Brevo API Response: {api_response}")

            return Response({"message": "Sales invoice email sent successfully"}, status=status.HTTP_200_OK)

        except ApiException as e:
            return Response({"error": f"Brevo API Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Unexpected error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ConvertQuotationToInvoiceAPIView(APIView):
    def post(self, request, quotation_id):
        """Convert a Quotation into a Sales Invoice and update status"""

        # ✅ Fetch the Quotation
        quotation = get_object_or_404(QuotationEstimate, id=quotation_id)
        
        # ✅ Check if the status is "Open"
        if quotation.status != "Open":
            return Response(
                {"error": "Quotation is already converted to invoice or not in 'Open' status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Fetch items from the quotation
        quotation_items = QuotationEstimateItem.objects.filter(quotation=quotation)
        if not quotation_items.exists():
            return Response({"error": "No items found in quotation."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create a new Sales Invoice
        sales_invoice = SalesInvoice.objects.create(
            party=quotation.party,
            invoice_number="",  # Auto-generated
            invoice_date=quotation.quotation_date,
            party_name=quotation.party_name,
            party_mobile_number=quotation.party_mobile_number,
            shipping_address=quotation.shipping_address,
        )

        # ✅ Copy Quotation Items to SalesInvoice Items
        invoice_items = []
        total_amount = 0  # Initialize total amount
        for item in quotation_items:
            invoice_items.append(
                SalesInvoiceItem(
                    sales_invoice=sales_invoice,
                    product_item=item.product_item,
                    service_item=item.service_item,
                    item_name=item.item_name,
                    description=item.description,
                    hsn_sac_code=item.hsn_sac_code,
                    measuring_unit=item.measuring_unit,
                    price_per_item=item.price_per_item,
                    quantity=item.quantity,
                    discount=item.discount,
                    tax=item.tax,
                    amount=item.amount,
                )
            )
            total_amount += item.amount  # Add the item amount to the total

        # ✅ Bulk create Sales Invoice Items
        SalesInvoiceItem.objects.bulk_create(invoice_items)

        # ✅ Create or update the TotalAmount model for the Sales Invoice
        total_obj, created = TotalAmount.objects.get_or_create(sales_invoice=sales_invoice)
        total_obj.total = total_amount  # Set the calculated total
        total_obj.save()

        # ✅ Change the status of the quotation to "Convert_into_Invoice"
        quotation.status = "Convert_into_Invoice"
        quotation.save()

        # ✅ Serialize and return the new Sales Invoice
        serializer = SalesInvoiceSerializer(sales_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConvertProformaToSalesInvoiceAPIView(APIView):
    def post(self, request, proforma_invoice_id):
        """Convert a Proforma Invoice into a Sales Invoice and update status"""

        # Fetch the Proforma Invoice
        proforma_invoice = get_object_or_404(ProformaInvoice, id=proforma_invoice_id)

        # Check if the status is not already "Converted"
        if proforma_invoice.status == "Converted to Sales Invoice":
            return Response(
                {"error": "Proforma Invoice is already converted to Sales Invoice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch items from the Proforma Invoice
        proforma_invoice_items = ProformaInvoiceItem.objects.filter(proforma_invoice=proforma_invoice)
        if not proforma_invoice_items.exists():
            return Response({"error": "No items found in Proforma Invoice."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Sales Invoice
        sales_invoice = SalesInvoice.objects.create(
            party=proforma_invoice.party,
            invoice_number="",  # Auto-generated
            invoice_date=proforma_invoice.proforma_invoice_date,
            party_name=proforma_invoice.party_name,
            party_mobile_number=proforma_invoice.party_mobile_number,
            shipping_address=proforma_invoice.shipping_address,
        )

        # Copy Proforma Invoice Items to Sales Invoice Items
        invoice_items = []
        total_amount = 0  # Initialize total amount
        for item in proforma_invoice_items:
            invoice_items.append(
                SalesInvoiceItem(
                    sales_invoice=sales_invoice,
                    product_item=item.product_item,
                    service_item=item.service_item,
                    item_name=item.item_name,
                    description=item.description,
                    hsn_sac_code=item.hsn_sac_code,
                    measuring_unit=item.measuring_unit,
                    price_per_item=item.price_per_item,
                    quantity=item.quantity,
                    discount=item.discount,
                    tax=item.tax,
                    amount=item.amount,
                )
            )
            total_amount += item.amount  # Add the item amount to the total

        # Bulk create Sales Invoice Items
        SalesInvoiceItem.objects.bulk_create(invoice_items)

        # Create or update the TotalAmount model for the Sales Invoice
        # The issue is likely due to incorrectly referencing `sales_invoice` for the `TotalAmount`
        # Ensure `sales_invoice` is properly passed into the TotalAmount object
        total_obj, created = TotalAmount.objects.get_or_create(sales_invoice=sales_invoice)
        total_obj.total = total_amount  # Set the calculated total
        total_obj.save()

        # Update the Proforma Invoice status to "Converted to Sales Invoice"
        proforma_invoice.status = "Converted to Sales Invoice"
        proforma_invoice.save()

        # Serialize and return the new Sales Invoice
        serializer = SalesInvoiceSerializer(sales_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ConvertDeliveryChallanToSalesInvoiceAPIView(APIView):
    def post(self, request, delivery_challan_id):
        """Convert a Delivery Challan into a Sales Invoice and update status"""

        # ✅ Fetch the Delivery Challan
        delivery_challan = get_object_or_404(DeliveryChallan, id=delivery_challan_id)

        # ✅ Check if the status is not already converted
        if delivery_challan.status == "Converted to Sales Invoice":
            return Response(
                {"error": "Delivery Challan is already converted to Sales Invoice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Fetch items from the Delivery Challan
        delivery_challan_items = DeliveryChallanItem.objects.filter(delivery_challan=delivery_challan)
        if not delivery_challan_items.exists():
            return Response({"error": "No items found in Delivery Challan."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Create a new Sales Invoice
        sales_invoice = SalesInvoice.objects.create(
            party=delivery_challan.party,
            invoice_number="",  # Auto-generated in model
            invoice_date=delivery_challan.delivery_challan_date,
            party_name=delivery_challan.party_name,
            party_mobile_number=delivery_challan.party_mobile_number,
            shipping_address=delivery_challan.shipping_address,
        )

        # ✅ Copy Delivery Challan Items to Sales Invoice Items
        invoice_items = []
        total_amount = 0  # Initialize total amount
        for item in delivery_challan_items:
            invoice_items.append(
                SalesInvoiceItem(
                    sales_invoice=sales_invoice,
                    product_item=item.product_item,
                    service_item=item.service_item,
                    item_name=item.item_name,
                    description=item.description,
                    hsn_sac_code=item.hsn_sac_code,
                    measuring_unit=item.measuring_unit,
                    price_per_item=item.price_per_item,
                    quantity=item.quantity,
                    discount=item.discount,
                    tax=item.tax,
                    amount=item.amount,
                )
            )
            total_amount += item.amount  # Add the item amount to the total

        # ✅ Bulk create Sales Invoice Items
        SalesInvoiceItem.objects.bulk_create(invoice_items)

        # ✅ Create or update the TotalAmount model for the Sales Invoice
        total_obj, created = TotalAmount.objects.get_or_create(sales_invoice=sales_invoice)
        total_obj.total = total_amount  # Set the calculated total
        total_obj.save()

        # ✅ Update the Delivery Challan status to "Converted to Sales Invoice"
        delivery_challan.status = "Converted to Sales Invoice"
        delivery_challan.save()

        # ✅ Serialize and return the new Sales Invoice
        serializer = SalesInvoiceSerializer(sales_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class GetAllSalesInvoicesAPIView(APIView):
    """API View to retrieve all Sales Invoices"""

    def get(self, request, *args, **kwargs):
        sales_invoices = SalesInvoice.objects.all()\
            .select_related("party", "total_amount")\
            .prefetch_related("sales_invoice_items")

        serializer = SalesInvoiceSerializer(sales_invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GetSalesInvoiceByIdAPIView(APIView):
    """API View to retrieve a SalesInvoice by ID"""
    
    def get(self, request, sales_invoice_id, *args, **kwargs):
        sales_invoice = get_object_or_404(SalesInvoice, id=sales_invoice_id)
        serializer = SalesInvoiceSerializer(sales_invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateSalesInvoiceByIdAPIView(APIView):
    """API View to update SalesInvoice and its items by ID"""

    def put(self, request, sales_invoice_id, *args, **kwargs):
        sales_invoice = get_object_or_404(SalesInvoice, id=sales_invoice_id)
        
        # Use the same Combined Serializer for nested update
        serializer = CombinedSalesInvoiceSerializer(sales_invoice, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_sales_invoice = serializer.save()

            # Recalculate total
            total_amount_obj, _ = TotalAmount.objects.get_or_create(sales_invoice=updated_sales_invoice)
            total_amount = updated_sales_invoice.sales_invoice_items.aggregate(
                models.Sum("amount")
            )["amount__sum"] or 0.00

            total_amount_obj.total = total_amount
            total_amount_obj.save()

            return Response({
                "message": "SalesInvoice updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteSalesInvoiceByIdAPIView(APIView):
    """API View to delete a SalesInvoice and its related total by ID"""

    def delete(self, request, sales_invoice_id, *args, **kwargs):
        sales_invoice = get_object_or_404(SalesInvoice, id=sales_invoice_id)

        # Optionally delete total amount manually
        TotalAmount.objects.filter(sales_invoice=sales_invoice).delete()
        
        # Delete the main invoice (assumes related items deleted via on_delete)
        sales_invoice.delete()

        return Response({"message": "SalesInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class DeleteSalesInvoiceByNumberAPIView(APIView):
    """API View to delete a SalesInvoice and its related total by invoice_number"""

    def delete(self, request, invoice_number, *args, **kwargs):
        # Get the SalesInvoice object by invoice_number
        sales_invoice = get_object_or_404(SalesInvoice, invoice_number=invoice_number)

        # Optionally delete total amount manually
        TotalAmount.objects.filter(sales_invoice=sales_invoice).delete()
        
        # Delete the main invoice (assumes related items are deleted via on_delete)
        sales_invoice.delete()

        return Response({"message": "SalesInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)



class GetSalesInvoicesByPartyIdAPIView(APIView):
    """API View to retrieve all SalesInvoices by Party ID"""
    
    def get(self, request, party_id, *args, **kwargs):
        sales_invoices = SalesInvoice.objects.filter(party__id=party_id)
        
        if not sales_invoices.exists():
            return Response({"error": "No Sales Invoices found for this Party."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SalesInvoiceSerializer(sales_invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateSalesInvoicesByPartyIdAPIView(APIView):
    """API View to update SalesInvoices by Party ID"""
    
    def put(self, request, party_id, *args, **kwargs):
        # Fetch SalesInvoice by Party ID and update
        sales_invoice = get_object_or_404(SalesInvoice, party__id=party_id)
        serializer = SalesInvoiceSerializer(sales_invoice, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_sales_invoice = serializer.save()
            return Response({"message": "SalesInvoice updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteSalesInvoicesByPartyIdAPIView(APIView):
    """API View to delete SalesInvoices by Party ID"""
    
    def delete(self, request, party_id, *args, **kwargs):
        sales_invoice = get_object_or_404(SalesInvoice, party__id=party_id)
        sales_invoice.delete()
        return Response({"message": "SalesInvoice deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

class DownloadSalesInvoicePDFAPIView(APIView):
    """API view to generate and download SalesInvoice PDF"""

    def get(self, request, sales_invoice_id, *args, **kwargs):
        """Generate and download PDF for a SalesInvoice"""

        # Get the SalesInvoice
        sales_invoice = get_object_or_404(SalesInvoice, id=sales_invoice_id)

        # Fetch items associated with the invoice
        items = SalesInvoiceItem.objects.filter(sales_invoice=sales_invoice)

        # Calculate the final total for the invoice
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "invoice_number": sales_invoice.invoice_number,
            "invoice_date": sales_invoice.invoice_date,
            "party_name": sales_invoice.party_name,
            "shipping_address": sales_invoice.shipping_address,
            "items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "sales_invoice_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response for downloading
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{sales_invoice.invoice_number}.pdf'
        return response

class PrintSalesInvoicePDFAPIView(APIView):
    """API view to generate and print SalesInvoice PDF"""

    def get(self, request, sales_invoice_id, *args, **kwargs):
        """Generate PDF for SalesInvoice and open print dialog"""

        # Get the SalesInvoice
        sales_invoice = get_object_or_404(SalesInvoice, id=sales_invoice_id)

        # Fetch items associated with the invoice
        items = SalesInvoiceItem.objects.filter(sales_invoice=sales_invoice)

        # Calculate the final total for the invoice
        final_total = sum(float(item.amount) for item in items)

        # Prepare the context for rendering the PDF template
        context = {
            "invoice_number": sales_invoice.invoice_number,
            "invoice_date": sales_invoice.invoice_date,
            "party_name": sales_invoice.party_name,
            "shipping_address": sales_invoice.shipping_address,
            "items": items,
            "final_total": final_total,
            "business_name": "Your Business Name"
        }

        # Generate PDF content
        pdf_content = generate_pdf_from_html(context, "sales_invoice_pdf_template.html")

        if not pdf_content:
            return Response({"error": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return the PDF as an HTTP response to be printed
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=invoice_{sales_invoice.invoice_number}.pdf'
        return response

class PaymentTermChoicesView(APIView):
    def get(self, request):
        return Response(dict(SalesInvoice.PAYMENT_TERM_CHOICES))
    
class SalesInvoiceWithAmountsAPIView(APIView):
    def get(self, request):
        # Get all invoices ordered by invoice date
        invoices = SalesInvoice.objects.all().order_by('-invoice_date')

        # Filter by payment statuses
        paid_invoices = invoices.filter(payment_status='paid')
        unpaid_invoices = invoices.filter(payment_status='unpaid')
        partially_paid_invoices = invoices.filter(payment_status='partially paid')

        # Total amounts by status
        total_paid = paid_invoices.aggregate(total=Sum('total_paid_amount'))['total'] or 0.00
        total_unpaid = unpaid_invoices.aggregate(total=Sum('total_amount__total'))['total'] or 0.00
        total_partially_paid = partially_paid_invoices.aggregate(total=Sum('balance_amount'))['total'] or 0.00

        # Overall total sales
        total_sales = invoices.aggregate(total=Sum('total_paid_amount'))['total'] or 0.00

        # Overall payment status
        if paid_invoices.count() == invoices.count():
            overall_status = "All Paid"
        elif unpaid_invoices.count() == invoices.count():
            overall_status = "None Paid"
        else:
            overall_status = "Some Paid"

        # Outstanding = sum of balance amounts of unpaid + partially paid
        outstanding_invoices = invoices.filter(payment_status__in=['unpaid', 'partially paid'])
        total_outstanding = outstanding_invoices.aggregate(total=Sum('balance_amount'))['total'] or 0.00

        # Overdue = unpaid or partially paid and due_date < today
        today = timezone.now().date()
        overdue_invoices = outstanding_invoices.filter(due_date__lt=today)
        total_overdue = overdue_invoices.aggregate(total=Sum('balance_amount'))['total'] or 0.00

        # Serialize all invoices
        serializer = SalesInvoiceSerializer(invoices, many=True)

        # Return combined data
        response_data = {
            "total_paid": total_paid,
            "total_unpaid": total_unpaid,
            "total_partially_paid": total_partially_paid,
            "total_outstanding": total_outstanding,
            "total_overdue": total_overdue,
            "total_sales": total_sales,
            "overall_status": overall_status,
            "invoices": serializer.data
        }

        return Response(response_data)

class SalesInvoiceWithAmountsByPartyAPIView(APIView):
    def get(self, request):
        party_id = request.query_params.get('party_id', None)
        if party_id:
            invoices = SalesInvoice.objects.filter(party=party_id).order_by('-invoice_date')
        else:
            invoices = SalesInvoice.objects.all().order_by('-invoice_date')

        serializer = SalesInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    

class ConvertClientSalesOrderToSalesInvoiceAPIView(APIView):
    def post(self, request, sales_order_id):
        sales_order = get_object_or_404(ClientSalesOrder, id=sales_order_id)

        if sales_order.status == "converted":
            return Response({"error": "Sales Order already converted"}, status=status.HTTP_400_BAD_REQUEST)

        # Use correct date field
        invoice_date = getattr(sales_order, 'order_date', timezone.now().date())  # fallback to today if missing

        shipping = getattr(sales_order.customer, "shipping_address", None)
        shipping_address = (
            f"{shipping.street}, {shipping.city}, {shipping.state} - {shipping.pincode}"
            if shipping else ""
        )

        sales_invoice = SalesInvoice.objects.create(
            party=sales_order.customer,
            invoice_number="",  # Optional: generate this dynamically
            invoice_date=invoice_date,
            party_name=sales_order.customer.party_name,
            party_mobile_number=sales_order.customer.mobile_number,
            shipping_address=shipping_address
        )

        order_items = sales_order.items.all()  # ✅ use related_name "items"
        if not order_items.exists():
            return Response({"error": "No items found in the Sales Order."}, status=status.HTTP_400_BAD_REQUEST)

        invoice_items = []
        total_amount = 0

        for item in order_items:
            invoice_items.append(
                SalesInvoiceItem(
                    sales_invoice=sales_invoice,
                    product_item=item.product_item,
                    service_item=item.service_item,
                    item_name=item.item_name,
                    description=item.description,
                    hsn_sac_code=item.hsn_sac_code,
                    measuring_unit=item.measuring_unit,
                    price_per_item=item.price_per_item,
                    quantity=item.quantity,
                    discount=item.discount,
                    tax=item.tax,
                    amount=item.total_amount,  # ✅ corrected from item.amount
                )
            )
            total_amount += item.total_amount or 0

        SalesInvoiceItem.objects.bulk_create(invoice_items)

        total_obj, created = TotalAmount.objects.get_or_create(sales_invoice=sales_invoice)
        total_obj.total = total_amount
        total_obj.save()

        sales_order.status = "Converted to Sales Invoice"
        sales_order.save()

        serializer = SalesInvoiceSerializer(sales_invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    


# new employee view ar api function
class SalesInvoiceBySalesPersonAPIView(APIView):
    def get(self, request, sales_person_id):
        invoices = SalesInvoice.objects.filter(sales_person__id=sales_person_id).order_by('-invoice_date')

        serializer = SalesInvoiceSerializer(invoices, many=True)
        data = serializer.data

        # Calculate overall totals
        total_outstanding = 0
        total_overdue = 0
        total_amount = 0

        for invoice in invoices:
            # Use serializer methods or fields to get amounts
            # Note: You can call the serializer methods manually or calculate here
            try:
                outstanding = float(invoice.balance_amount) if invoice.payment_status != "paid" else 0.0
                total_outstanding += outstanding

                overdue = outstanding if invoice.due_date and invoice.due_date < date.today() and invoice.payment_status != "paid" else 0.0
                total_overdue += overdue

                # Use total_amount.total (DecimalField) or 0.0 if None
                total_amount += float(invoice.total_amount.total) if invoice.total_amount else 0.0
            except Exception:
                pass

        return Response({
            "sales_person_id": sales_person_id,
            "total_outstanding_amount": round(total_outstanding, 2),
            "total_overdue_amount": round(total_overdue, 2),
            "total_amount": round(total_amount, 2),
            "invoices": data
        })
    

class AllSalesInvoicesAPIView(APIView):
    def get(self, request):
        invoices = SalesInvoice.objects.all().order_by('-invoice_date')
        serializer = SalesInvoiceSerializer(invoices, many=True)
        data = serializer.data

        # Initialize totals
        total_outstanding = 0
        total_overdue = 0
        total_amount = 0

        for invoice in invoices:
            try:
                outstanding = float(invoice.balance_amount) if invoice.payment_status != "paid" else 0.0
                total_outstanding += outstanding

                overdue = outstanding if invoice.due_date and invoice.due_date < date.today() and invoice.payment_status != "paid" else 0.0
                total_overdue += overdue

                total_amount += float(invoice.total_amount.total) if invoice.total_amount else 0.0
            except Exception:
                pass

        return Response({
            "total_outstanding_amount": round(total_outstanding, 2),
            "total_overdue_amount": round(total_overdue, 2),
            "total_amount": round(total_amount, 2),
            "invoices": data
        })


from django.db.models import Sum, F,FloatField
from datetime import date
class AllSalesPersonsInvoiceTotalsAPIView(APIView):
     def get(self, request):
        try:
            sales_persons = SalesPerson.objects.prefetch_related('sales_invoices__sales_invoice_items').all()
            employee_totals = []

            for person in sales_persons:
                invoices = person.sales_invoices.all()
                total_collected = 0
                total_outstanding = 0
                total_overdue = 0

                for invoice in invoices:
                    invoice_total = invoice.sales_invoice_items.aggregate(
                        total=Sum(F('quantity') * F('price_per_item') - F('discount'), output_field=FloatField())
                    )['total'] or 0

                    if invoice.payment_status == 'paid':
                        total_collected += invoice_total
                    elif invoice.payment_status == 'partially_paid':
                        paid_amount = invoice.total_paid_amount or 0
                        total_collected += paid_amount
                        total_outstanding += invoice_total - paid_amount
                        if invoice.due_date and invoice.due_date < date.today():
                            total_overdue += invoice_total - paid_amount
                    else:
                        total_outstanding += invoice_total
                        if invoice.due_date and invoice.due_date < date.today():
                            total_overdue += invoice_total

                employee_totals.append({
                    'id': person.id,
                    'name': person.name,
                    'email': person.email,
                    'total_collected': float(total_collected),
                    'total_outstanding': float(total_outstanding),
                    'total_overdue': float(total_overdue),
                })

            return Response({
                'status': 'success',
                'data': employee_totals
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("ERROR:", str(e))  # for debugging only
            return Response({
                'status': 'error',
                'message': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)