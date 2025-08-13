import logging
import pandas as pd
from django.http import JsonResponse
from rest_framework import generics
import openpyxl
from rest_framework import viewsets
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

# ProductItem API View
class ProductItemListAPIView(APIView):
    """ GET all Product Items """
    def get(self, request):
        product_items = ProductItem.objects.all()
        serializer = ProductItemSerializer(product_items, many=True)
        return Response(serializer.data)

# Set up logging
logger = logging.getLogger(__name__)

class ProductItemCreateAPIView(APIView):
    """ POST a new Product Item """
    
    def post(self, request):
        try:
            # Deserialize the request data
            serializer = ProductItemSerializer(data=request.data)
            
            if serializer.is_valid():
                # Save the product item to the database
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Log validation errors
                logger.error(f"Validation failed for ProductItem: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AssertionError as e:
            # Log the error if an assertion fails
            logger.error(f"AssertionError: {str(e)}")
            return Response({"error": "An error occurred while processing your request."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any other exceptions
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": "An unexpected error occurred. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductItemRetrieveAPIView(APIView):
    """ GET Product Item by ID """
    def get(self, request, pk):
        product_item = get_object_or_404(ProductItem, pk=pk)
        serializer = ProductItemSerializer(product_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductItemUpdateAPIView(APIView):
    """ PUT Product Item by ID """
    def put(self, request, pk):
        product_item = get_object_or_404(ProductItem, pk=pk)
        serializer = ProductItemSerializer(product_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductItemDeleteAPIView(APIView):
    """ DELETE Product Item by ID """
    def delete(self, request, pk):
        product_item = get_object_or_404(ProductItem, pk=pk)
        product_item.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk):
        product_item = get_object_or_404(ProductItem, pk=pk)
        product_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ServiceItemListAPIView(APIView):
    """ GET all Service Items """
    def get(self, request):
        service_items = ServiceItem.objects.all()
        serializer = ServiceItemSerializer(service_items, many=True)
        return Response(serializer.data)

class ServiceItemCreateAPIView(APIView):
    """ POST a new Service Item """
    def post(self, request):
        serializer = ServiceItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceItemRetrieveAPIView(APIView):
    """ GET Service Item by ID """
    def get(self, request, pk):
        service_item = get_object_or_404(ServiceItem, pk=pk)
        serializer = ServiceItemSerializer(service_item)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceItemUpdateAPIView(APIView):
    """ PUT Service Item by ID """
    def put(self, request, pk):
        service_item = get_object_or_404(ServiceItem, pk=pk)
        serializer = ServiceItemSerializer(service_item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceItemDeleteAPIView(APIView):
    """ DELETE Service Item by ID """
    def delete(self, request, pk):
        service_item = get_object_or_404(ServiceItem, pk=pk)
        service_item.delete()
        return Response({"detail": "Deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class ImportHSNData(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name="HSN_MSTR")  # Adjust sheet name if necessary

            hsn_objects = [
                HSNCode(hsn_code=row["HSN_CD"], description=row["HSN_Description"])
                for _, row in df.iterrows()
            ]

            with transaction.atomic():
                HSNCode.objects.bulk_create(hsn_objects, batch_size=1000)  # Adjust batch size

            return Response({"message": "HSN Codes imported successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ImportSACData(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file, sheet_name=0)  # Adjust sheet name if needed

            sac_objects = [
                SACCode(sac_code=row["SAC_CD"], description=row["SAC_Description"])
                for _, row in df.iterrows()
            ]

            with transaction.atomic():
                SACCode.objects.bulk_create(sac_objects, batch_size=1000)  # Adjust batch size

            return Response({"message": "SAC Codes imported successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BulkGSTTaxView(APIView):
    """API to upload multiple GST rates in JSON format"""

    def post(self, request):
        """Handles bulk GST tax posting"""
        serializer = GSTTaxSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "GST rates added successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GSTTaxListView(generics.ListAPIView):
    queryset = GSTTax.objects.all()  # Retrieves all GSTTax records
    serializer_class = GSTTaxSerializer

class ProductAndServiceItemListAPIView(APIView):
    """ GET all Product and Service Items with type """
    def get(self, request):
        product_items = ProductItem.objects.all()
        service_items = ServiceItem.objects.all()

        # Serialize both product and service items
        product_serializer = ProductItemSerializer(product_items, many=True)
        service_serializer = ServiceItemSerializer(service_items, many=True)

        # Adding 'type' to each product and service item
        for item in product_serializer.data:
            item['type'] = 'product'

        for item in service_serializer.data:
            item['type'] = 'service'

        # Combine product and service items into one list
        combined_items = product_serializer.data + service_serializer.data

        return Response(combined_items)

class GenerateBarcodeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Generate Product Code (ITM00001, ITM00002, ...)
            last_item = ProductItem.objects.order_by("-id").first()
            if last_item and last_item.product_code:
                # Extract numeric part and increment
                last_number = last_item.product_code[3:]  # Extract part after 'ITM'
                if last_number.isdigit():  # Check if the number is valid
                    next_number = int(last_number) + 1
                else:
                    next_number = 1  # Default to 1 if the number is invalid
            else:
                next_number = 1  # If no products exist, start from 1

            product_code = f"ITM{next_number:05d}"

            # Generate Barcode for the product code
            barcode_class = barcode.get_barcode_class("code128")
            barcode_instance = barcode_class(product_code, writer=ImageWriter())
            buffer = BytesIO()
            barcode_instance.write(buffer)
            buffer.seek(0)

            # Save the barcode image
            filename = f"{product_code}.png"
            barcode_image = ContentFile(buffer.read())
            product_item = ProductItem(product_code=product_code, barcode_image=barcode_image)
            product_item.save()

            return JsonResponse({
                "product_code": product_code,
                "barcode_image_url": product_item.barcode_image.url  # Return the image URL
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return JsonResponse({'error': f'ValueError: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ItemDeleteAPIView(APIView):
    """ DELETE Product or Service Item by ID based on item_type ('product' or 'service') """

    def delete(self, request, item_type, pk):
        if item_type == "product":
            item = get_object_or_404(ProductItem, pk=pk)
        elif item_type == "service":
            item = get_object_or_404(ServiceItem, pk=pk)
        else:
            return Response({"detail": "Invalid item_type. Must be 'product' or 'service'."},
                            status=status.HTTP_400_BAD_REQUEST)

        item.delete()
        return Response({"detail": f"{item_type.capitalize()} item deleted successfully."},
                        status=status.HTTP_204_NO_CONTENT)