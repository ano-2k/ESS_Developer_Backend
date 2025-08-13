# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from rest_framework.generics import get_object_or_404
from .models import ClientPurchaseOrder


class ClientPurchaseOrderCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = ClientPurchaseOrderSerializer(data=request.data)
        if serializer.is_valid():
            purchase_order = serializer.save()
            return Response({
                "message": "Client Purchase Order created successfully.",
                "po_id": purchase_order.id,
                "po_number": purchase_order.po_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientPurchaseOrderUpdateAPIView(APIView):
    def put(self, request, pk, format=None):
        purchase_order = get_object_or_404(ClientPurchaseOrder, pk=pk)
        serializer = ClientPurchaseOrderUpdateSerializer(purchase_order, data=request.data)
        if serializer.is_valid():
            updated_po = serializer.save()
            return Response({
                "message": "Client Purchase Order updated successfully.",
                "po_id": updated_po.id,
                "po_number": updated_po.po_number
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)