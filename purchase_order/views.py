from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.generics import ListAPIView
from .models import *
from .serializers import *
from purchase_order.utils.invoice_parser import extract_text_from_pdf, parse_invoice_text


# 🔹 Purchase Order Views

class PurchaseOrderListAPIView(APIView):
    def get(self, request):
        orders = PurchaseOrder.objects.all().order_by('-order_date')
        serializer = PurchaseOrderSerializer(orders, many=True)
        return Response(serializer.data)


class PurchaseOrderDetailAPIView(APIView):
    def get(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        serializer = PurchaseOrderSerializer(order)
        return Response(serializer.data)


class PurchaseOrderCreateAPIView(APIView):
    def post(self, request):
        serializer = PurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderUpdateAPIView(APIView):
    def put(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        serializer = PurchaseOrderSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderDeleteAPIView(APIView):
    def delete(self, request, pk):
        order = get_object_or_404(PurchaseOrder, pk=pk)
        order.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# 🔹 Send Email
class SendPurchaseOrderEmailAPIView(APIView):
    def post(self, request, purchase_order_id):
        # Get the purchase order
        po = get_object_or_404(PurchaseOrder, id=purchase_order_id)
        supplier_email = po.vendor.email

        subject = f"Purchase Order - {po.po_number}"  # Corrected the field name
        message = f"""
Dear {po.vendor.party_name},

We are sending you the purchase order with the following details:

Purchase Order No: {po.po_number}  # Corrected the field name
Order Date: {po.order_date}
Delivery Date: {po.delivery_date or 'N/A'}
Total Amount: ₹{po.total_amount}  # Assuming 'total_amount' is a field of the PurchaseOrder

Notes: {po.notes or 'N/A'}

Regards,
Your Company
"""

        try:
            # Send the email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [supplier_email])
            
            # Update the status of the Purchase Order to 'issued'
            po.status = 'issued'
            po.save()
            
            status_text = 'sent'
        except Exception as e:
            status_text = 'failed'

        # Log the email status in the PurchaseOrderEmailLog model
        PurchaseOrderEmailLog.objects.create(
            purchase_order=po,  # Associate the email log with the purchase order
            email=supplier_email,  # Corrected field name
            subject=subject,
            body=message,
            status=status_text
        )

        # Return response based on the email sending result
        if status_text == 'sent':
            return Response({"message": "Email sent and status updated to 'issued'."}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Email sending failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 🔹 Upload & Parse Vendor Invoice PDF
class VendorInvoiceUploadAPIView(APIView):
    def post(self, request, purchase_order_id):
        purchase_order = get_object_or_404(PurchaseOrder, id=purchase_order_id)
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f'vendor_invoices/{uploaded_file.name}', uploaded_file)
        file_path = default_storage.path(path)

        try:
            text = extract_text_from_pdf(file_path)
            parsed_data = parse_invoice_text(text)

            invoice = VendorInvoice.objects.create(
                purchase_order=purchase_order,
                invoice_number=parsed_data["invoice_number"],
                invoice_date=parsed_data["invoice_date"],
                total_amount=parsed_data["total_amount"],
                uploaded_file=path
            )

            for item in parsed_data["items"]:
                VendorInvoiceItem.objects.create(
                    vendor_invoice=invoice,
                    product_description=item.get("description"),
                    quantity=item.get("quantity"),
                    rate=item.get("rate"),
                    tax_amount=item.get("tax_amount"),
                    total=item.get("total")
                )

            return Response({
                'message': 'Invoice uploaded and parsed successfully',
                'data': {
                    'invoice_number': invoice.invoice_number,
                    'invoice_date': invoice.invoice_date,
                    'total_amount': invoice.total_amount,
                    'items': parsed_data["items"]
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VendorInvoice Creation
class VendorInvoiceCreateAPIView(APIView):
    def post(self, request):
        serializer = VendorInvoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# List All VendorInvoices
class VendorInvoiceListAPIView(APIView):
    def get(self, request):
        invoices = VendorInvoice.objects.all().order_by('-id')
        serializer = VendorInvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Retrieve a Single VendorInvoice
class VendorInvoiceRetrieveAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(VendorInvoice, pk=pk)

    def get(self, request, pk):
        invoice = self.get_object(pk)
        serializer = VendorInvoiceSerializer(invoice)
        return Response(serializer.data)


# Update an Existing VendorInvoice
class VendorInvoiceUpdateAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(VendorInvoice, pk=pk)

    def put(self, request, pk):
        invoice = self.get_object(pk)
        serializer = VendorInvoiceSerializer(invoice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a VendorInvoice
class VendorInvoiceDeleteAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(VendorInvoice, pk=pk)

    def delete(self, request, pk):
        invoice = self.get_object(pk)
        invoice.delete()
        return Response({"message": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    
# 🔹 Create VendorInvoice manually (if not using PDF)
class VendorInvoiceCreateAPIView(generics.CreateAPIView):
    queryset = VendorInvoice.objects.all()
    serializer_class = VendorInvoiceSerializer


class ConvertVendorInvoiceToPaymentAPIView(APIView):
    def post(self, request, vendor_invoice_id):  # <- Make sure this matches your URL
        serializer = ConvertVendorInvoicePaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Fetch VendorInvoice object using ID from URL
            vendor_invoice = VendorInvoice.objects.get(id=vendor_invoice_id)

            # Inject vendor_invoice into validated data
            serializer.validated_data['vendor_invoice'] = vendor_invoice

            payment = serializer.save()

            return Response({
                "message": "Vendor invoice payment recorded successfully.",
                "payment_id": payment.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ListVendorInvoicePaymentsAPIView(ListAPIView):
    queryset = VendorInvoicePayment.objects.all().order_by('-payment_date')
    serializer_class = ListVendorPaymentSerializer


# 🔹 Delete a VendorInvoicePayment and update status
class VendorInvoicePaymentDeleteAPIView(APIView):
    def delete(self, request, pk):
        payment = get_object_or_404(VendorInvoicePayment, pk=pk)
        vendor_invoice = payment.vendor_invoice
        payment.delete()

        vendor_invoice.update_payment_status()
        return Response({"message": "Payment deleted and invoice status updated."}, status=status.HTTP_204_NO_CONTENT)

class PendingVendorInvoicesAPIView(APIView):
    def get(self, request, vendor_id):
        pending_invoices = VendorInvoice.objects.filter(
            vendor_id=vendor_id,
            payment_status__in=['unpaid', 'partially_paid']
        ).prefetch_related('items', 'vendor')

        serializer = VendorInvoiceSerializer(pending_invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)