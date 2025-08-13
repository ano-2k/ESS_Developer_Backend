# documents/serializers.py
from rest_framework import serializers
from .models import Document, ManagerDocument, SupervisorDocument

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id',
            'user_id',
            'email',
            'aadhar_card',
            'pan_card',
            'bank_details',
            'previous_payslip',
            'experience_certificate',
            'degree_certificate',
            'description',
            'created_at',
            'updated_at',
        ]

class ManagerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerDocument
        fields = [
            'id',
            'user_id',
            'email',
            'aadhar_card',
            'pan_card',
            'bank_details',
            'previous_payslip',
            'experience_certificate',
            'degree_certificate',
            'description',
            'created_at',
            'updated_at',
        ]

class SupervisorDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorDocument
        fields = [
            'id',
            'user_id',
            'email',
            'aadhar_card',
            'pan_card',
            'bank_details',
            'previous_payslip',
            'experience_certificate',
            'degree_certificate',
            'description',
            'created_at',
            'updated_at',
        ]
