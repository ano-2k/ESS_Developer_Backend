from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from django.shortcuts import get_object_or_404

# POST - Create a SalesPerson
class SalesPersonCreateView(APIView):
    def post(self, request):
        serializer = SalesPersonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUES)

# GET/PUT/DELETE - Retrieve, Update or Delete by ID

class SalesPersonDetailView(APIView):
    def get(self, request, pk):
        salesperson = get_object_or_404(SalesPerson, pk=pk)
        serializer = SalesPersonSerializer(salesperson)
        return Response(serializer.data)

    def put(self, request, pk):
        salesperson = get_object_or_404(SalesPerson, pk=pk)
        serializer = SalesPersonSerializer(salesperson, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        salesperson = get_object_or_404(SalesPerson, pk=pk)
        salesperson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SalesPersonInvoicesView(APIView):
    def get(self, request, id):
        try:
            salesperson = SalesPerson.objects.get(id=id)
        except SalesPerson.DoesNotExist:
            return Response({"detail": "SalesPerson not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SalesPersonWithInvoicesSerializer(salesperson, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SalesPersonListView(APIView):
    def get(self, request):
        salespersons = SalesPerson.objects.all()
        serializer = SalesPersonWithInvoicesSerializer(salespersons, many=True)
        return Response(serializer.data)




 