from rest_framework import serializers
from .models import SalesPerson  # Make sure this is imported
from Sales_Invoice.serializers import * # Import SalesPersonInvoiceListSerializer

# 👨‍💼 SalesPerson Invoice List Serializer
class SalesPersonInvoiceListSerializer(serializers.ModelSerializer):
    sales_invoice_items = SalesInvoiceItemSerializer(many=True, read_only=True)
  #  total_amount = TotalAmountSerializer(read_only=True)
    party_name = serializers.CharField(source="party.party_name", read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            "id", "invoice_number", "invoice_date", "due_date", "party_name",
            "payment_status", "sales_invoice_items"
        ]

class SalesPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPerson
        fields = ['id', 'name', 'email', 'phone', 'region', 'target', 'commission_rate', 'total_sales', 'deals_closed', 'clients_handled']

class SalesPersonWithInvoicesSerializer(serializers.ModelSerializer):
    sales_invoices = SalesPersonInvoiceListSerializer(many=True, read_only=True)

    class Meta:
        model = SalesPerson
        fields = ["id", "name", "email", "total_sales", "deals_closed", "sales_invoices",]