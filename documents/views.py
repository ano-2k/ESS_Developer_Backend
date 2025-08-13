from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Document, ManagerDocument, SupervisorDocument
from .serializers import DocumentSerializer, ManagerDocumentSerializer, SupervisorDocumentSerializer

# Upload Document API
class UploadDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Document List API
class DocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employee_id = request.query_params.get('employee_id', None)
        if employee_id:
            documents = Document.objects.filter(user_id=employee_id)
        else:
            documents = Document.objects.all()

        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Update Document API
class UpdateDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, document_id):
        document = get_object_or_404(Document, id=document_id)
        serializer = DocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Manager Upload Document API
class ManagerUploadDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ManagerDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Manager Document List API
class ManagerDocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        manager_id = request.query_params.get('manager_id', None)
        if manager_id:
            documents = ManagerDocument.objects.filter(user_id=manager_id)
        else:
            documents = ManagerDocument.objects.all()

        serializer = ManagerDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Manager Update Document API
class ManagerUpdateDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        document = get_object_or_404(ManagerDocument, user_id=user_id)
        serializer = ManagerDocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Supervisor Upload Document API
class SupervisorUploadDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SupervisorDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Supervisor Document List API
class SupervisorDocumentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        supervisor_id = request.query_params.get('supervisor_id', None)
        if supervisor_id:
            documents = SupervisorDocument.objects.filter(user_id=supervisor_id)
        else:
            documents = SupervisorDocument.objects.all()

        serializer = SupervisorDocumentSerializer(documents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Supervisor Update Document API
class SupervisorUpdateDocumentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id):
        document = get_object_or_404(SupervisorDocument, user_id=user_id)
        serializer = SupervisorDocumentSerializer(document, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    

    