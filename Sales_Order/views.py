from django.utils import timezone 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.shortcuts import get_object_or_404
from django.conf import settings
from ClientPurchaseOrder.models import *
from .serializers import *
from django.core.mail import send_mail

class ClientSalesOrderCreateAPIView(APIView):
    def post(self, request):
        serializer = ClientSalesOrderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sales_order = serializer.save()  # Serializer handles everything
                return Response(ClientSalesOrderSerializer(sales_order).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 🔹 GET ALL SALES ORDERS
class GetAllClientSalesOrdersAPIView(APIView):
    def get(self, request):
        sales_orders = ClientSalesOrder.objects.all()
        serializer = ClientSalesOrderSerializer(sales_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# 🔹 GET SINGLE SALES ORDER BY ID
class GetSingleClientSalesOrderAPIView(APIView):
    def get(self, request, id):
        try:
            sales_order = ClientSalesOrder.objects.get(id=id)
        except ClientSalesOrder.DoesNotExist:
            return Response({'error': 'ClientSalesOrder not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClientSalesOrderSerializer(sales_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateClientSalesOrderAPIView(APIView):
    def put(self, request, id):
        try:
            instance = ClientSalesOrder.objects.get(id=id)
        except ClientSalesOrder.DoesNotExist:
            return Response({'error': 'ClientSalesOrder not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ClientSalesOrderSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteClientSalesOrderAPIView(APIView):
    def delete(self, request, id):
        try:
            instance = ClientSalesOrder.objects.get(id=id)
            instance.delete()
            return Response({'message': 'Deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ClientSalesOrder.DoesNotExist:
            return Response({'error': 'ClientSalesOrder not found.'}, status=status.HTTP_404_NOT_FOUND)

class SendClientSalesOrderEmailAPIView(APIView):
    def post(self, request, sales_order_id):
        # Get the Sales Order object
        so = get_object_or_404(ClientSalesOrder, id=sales_order_id)
        customer_email = so.customer.email  # assuming AddParty has an email field

        subject = f"Sales Order - {so.so_number}"
        message = f"""
Dear {so.customer.party_name},

We are sending you the sales order with the following details:

Sales Order No: {so.so_number}
Order Date: {so.so_date}
Delivery Date: {so.delivery_date or 'N/A'}
Total Amount: ₹{so.total_amount.total if so.total_amount else 'N/A'}

Remarks: {so.remarks or 'N/A'}

Regards,
Your Company
"""

        try:
            # Attempt to send the email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [customer_email])
            email_status = 'sent'

            # Update the Sales Order status to 'sent'
            so.status = 'sent'
            so.save()

        except Exception as e:
            email_status = 'failed'

        # Log the email
        ClientSalesOrderEmailLog.objects.create(
            sales_order=so,
            email=customer_email,
            subject=subject,
            body=message,
            status=email_status
        )

        if email_status == 'sent':
            return Response({"message": "Email sent and sales order status updated to 'sent'."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)