from rest_framework import serializers
from .models import *
from Pincode.models import *
from Sales_Invoice.models import *

class CreatePaymentInSerializer(serializers.ModelSerializer):
    party_id = serializers.PrimaryKeyRelatedField(
        queryset=AddParty.objects.all(), source='party', write_only=True
    )

    class Meta:
        model = RecordPayment
        fields = ["party_id", "payment_mode", "payment_amount", "notes", "payment_in_number","payment_date"]
        read_only_fields = ["payment_in_number"]

    def create(self, validated_data):
        """Auto-generate unique payment number and create RecordPayment"""
        last_payment = RecordPayment.objects.order_by('-id').first()
        next_number = 1 if not last_payment else int(last_payment.payment_in_number.split('-')[1]) + 1
        validated_data["payment_in_number"] = f"PAYIN-{next_number:05d}"
        validated_data["sales_invoice"] = None  # No invoice for this payment
        return super().create(validated_data)

class ConvertSalesInvoiceSerializer(serializers.Serializer):
    invoice_id = serializers.IntegerField()
    payment_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = serializers.CharField(max_length=50)
    notes = serializers.CharField(allow_blank=True, required=False)
    payment_in_number = serializers.CharField(required=False)
    payment_date = serializers.DateField(required=False)

    def create(self, validated_data):
        invoice_id = validated_data.pop("invoice_id")
        sales_invoice = SalesInvoice.objects.get(id=invoice_id)

        # Generate payment number if not provided
        if "payment_in_number" not in validated_data or not validated_data["payment_in_number"]:
            last_payment = RecordPayment.objects.order_by("-id").first()
            next_number = 1 if not last_payment else int(last_payment.payment_in_number.split("-")[1]) + 1
            validated_data["payment_in_number"] = f"PAYIN-{next_number:05d}"

        payment = RecordPayment.objects.create(
            sales_invoice=sales_invoice,
            party=sales_invoice.party,
            **validated_data
        )

        return payment

    
class ListPaymentInSerializer(serializers.ModelSerializer):
    party_name = serializers.CharField(source="party.party_name", read_only=True)
    invoice_number = serializers.CharField(source="sales_invoice.invoice_number", read_only=True, allow_null=True)

    class Meta:
        model = RecordPayment
        fields = ["id","payment_in_number", "payment_date", "payment_mode", "payment_amount", "party_name", "invoice_number", "notes"]

# Yearly Revenue Serializer
class YearlyRevenueSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

# Monthly Revenue Serializer
class MonthlyRevenueSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()  # 1 for January, 2 for February, etc.
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)

