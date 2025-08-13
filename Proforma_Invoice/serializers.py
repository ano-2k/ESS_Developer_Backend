from rest_framework import serializers
from .models import *

# 🧾 Tax Serializer
class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSTTax
        fields = ["id", "name", "gst_rate", "cess_rate"]

# 👨‍💼 Sales Person Serializer
class SalesPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPerson
        fields = ["id", "name", "email"]

class ProformaInvoiceItemSerializer(serializers.ModelSerializer):
    product_item_name = serializers.CharField(source="product_item.name", read_only=True)
    service_item_name = serializers.CharField(source="service_item.name", read_only=True)
    item_name = serializers.SerializerMethodField()
    tax = TaxSerializer(read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all(), write_only=True, source="tax")
  
    class Meta:
        model = ProformaInvoiceItem
        fields = ["product_item", "service_item", "quantity", "discount", "price_per_item", "amount"
                  ,"product_item_name","tax","tax_id" ,"service_item_name", "item_name"]
        extra_kwargs = {
            "proforma_invoice": {"required": False}  # Make proforma_invoice optional
        }
    def get_item_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        else:
            return None

class CombinedProformaInvoiceSerializer(serializers.ModelSerializer):
    items = ProformaInvoiceItemSerializer(many=True, write_only=True)

    class Meta:
        model = ProformaInvoice
        fields = ["party", "proforma_invoice_date","sales_person","due_date","proforma_invoice_number", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        proforma_invoice = ProformaInvoice.objects.create(**validated_data)
        
        # Create ProformaInvoiceItem instances and assign the proforma_invoice
        for item_data in items_data:
            ProformaInvoiceItem.objects.create(proforma_invoice=proforma_invoice, **item_data)
        
        # Create and save the total amount for the proforma_invoice
        ProformaTotalAmount.objects.create(proforma_invoice=proforma_invoice)

        return proforma_invoice
    def update(self, instance, validated_data):
     items_data = validated_data.pop('items', [])

    # Update basic ProformaInvoice fields
     for attr, value in validated_data.items():
        setattr(instance, attr, value)
     instance.save()

    # Delete existing ProformaInvoiceItems
     instance.proforma_invoice_items.all().delete()

    # Create new ProformaInvoiceItems
     for item_data in items_data:
        ProformaInvoiceItem.objects.create(proforma_invoice=instance, **item_data)

     return instance



class ProformaTotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProformaTotalAmount
        fields = ["proforma_invoice", "total"]
        
class ProformaInvoiceSerializer(serializers.ModelSerializer):
    proforma_invoice_items = ProformaInvoiceItemSerializer(many=True, read_only=True)
    total_amount = ProformaTotalAmountSerializer(read_only=True)

    class Meta:
        model = ProformaInvoice
        fields = "__all__"

class ProformaInvoiceResponseSerializer(serializers.ModelSerializer):
    proforma_invoice_items = ProformaInvoiceItemSerializer(many=True, read_only=True)
    proforma_invoice_total = ProformaTotalAmountSerializer(source="total_amount", read_only=True)
    proforma_invoice_number = serializers.CharField()  # No need for source here
    proforma_invoice_date = serializers.DateField()
    party_name = serializers.CharField(source="party.name", read_only=True)
    party_mobile_number = serializers.CharField(source="party.mobile_number", read_only=True)
    shipping_address = serializers.CharField(source="party.shipping_address", read_only=True)
    sales_person = SalesPersonSerializer(read_only=True)
    class Meta:
        model = ProformaInvoice
        fields = [
            "id", "party", "proforma_invoice_items","sales_person", "proforma_invoice_total",
            "proforma_invoice_number", "proforma_invoice_date", "due_date",
            "party_name", "party_mobile_number", "shipping_address", "status"
        ]



