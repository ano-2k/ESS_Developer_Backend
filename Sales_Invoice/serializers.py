from rest_framework import serializers
from .models import *
from Pincode.models import *

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

# 🧾 Item Serializer
class SalesInvoiceItemSerializer(serializers.ModelSerializer):
    price_per_item = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tax = TaxSerializer(read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all(), write_only=True, source="tax")
    type = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measuring_unit = serializers.SerializerMethodField()

    class Meta:
        model = SalesInvoiceItem
        fields = [
            "product_item", "service_item", "quantity", "discount", "price_per_item",
            "amount", "tax", "tax_id", "type", "name", "measuring_unit"
        ]

    def get_type(self, obj):
        if obj.product_item:
            return "Product"
        elif obj.service_item:
            return "Service"
        return "Unknown"

    def get_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        return "Unnamed"

    def get_measuring_unit(self, obj):
        if obj.product_item:
            return obj.product_item.measuring_unit or "Unit"
        return ""

# 💼 Total Amount Serializer
class TotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalAmount
        fields = ["sales_invoice", "total"]

# 📄 Invoice Serializer for listing
from datetime import date

from django.core.exceptions import ObjectDoesNotExist

class SalesInvoiceSerializer(serializers.ModelSerializer):
    party = serializers.PrimaryKeyRelatedField(queryset=AddParty.objects.all())
    sales_invoice_items = SalesInvoiceItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    sales_person = SalesPersonSerializer(read_only=True)

    outstanding_amount = serializers.SerializerMethodField()
    overdue_amount = serializers.SerializerMethodField()
    party_email = serializers.CharField(source='party.email', allow_blank=True, required=False)
    party_mobile_number = serializers.CharField(source='party.mobile_number', allow_blank=True, required=False)
    shipping_address = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = SalesInvoice
        fields = [
            "id", "invoice_number", "invoice_date", "due_date", "payment_status", 
            "total_paid_amount", "balance_amount", "party","party_name","sales_invoice_items",
            "sales_person", "outstanding_amount", "overdue_amount", "shipping_address","total_amount", "party_email", "party_mobile_number",
        ]

    def get_total_amount(self, obj):
        try:
            if obj.payment_status == "partially_paid":
                return {"total": obj.balance_amount}
            return {"total": obj.total_amount.total}
        except ObjectDoesNotExist:
            return {"total": 0.00}

    def get_outstanding_amount(self, obj):
        try:
            if obj.payment_status == "paid":
                return 0.00
            elif obj.payment_status == "partially_paid":
                return float(obj.balance_amount)
            return float(obj.total_amount.total)
        except ObjectDoesNotExist:
            return 0.00

    def get_overdue_amount(self, obj):
        today = date.today()
        if obj.due_date and obj.due_date < today and obj.payment_status != "paid":
            return self.get_outstanding_amount(obj)
        return 0.00

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response["amount_paid"] = str(instance.total_paid_amount)
        response["outstanding_amount"] = str(self.get_outstanding_amount(instance))
        response["overdue_amount"] = str(self.get_overdue_amount(instance))
        return response


# ✍️ Combined Create Serializer
class CombinedSalesInvoiceSerializer(serializers.ModelSerializer):
    items = SalesInvoiceItemSerializer(many=True, write_only=True)

    class Meta:
        model = SalesInvoice
        fields = ["party", "invoice_date", "due_date", "sales_person", "invoice_number", "payment_terms", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sales_invoice = SalesInvoice.objects.create(**validated_data)

        for item_data in items_data:
            product_item = item_data.get("product_item")
            service_item = item_data.get("service_item")
            quantity = item_data["quantity"]

            # Check stock
            if product_item:
                if product_item.opening_stock < quantity:
                    raise serializers.ValidationError({"quantity": f"Insufficient stock for {product_item.item_name}"})
                product_item.opening_stock -= quantity
                product_item.save()
            elif service_item:
                if service_item.opening_stock < quantity:
                    raise serializers.ValidationError({"quantity": f"Insufficient stock for {service_item.service_name}"})
                service_item.opening_stock -= quantity
                service_item.save()

            SalesInvoiceItem.objects.create(sales_invoice=sales_invoice, **item_data)

        TotalAmount.objects.create(sales_invoice=sales_invoice)
        return sales_invoice

    def to_representation(self, instance):
        return SalesInvoiceSerializer(instance, context=self.context).data
    
    def update(self, instance, validated_data):
     items_data = validated_data.pop('items', [])

    # Update basic SalesInvoice fields
     for attr, value in validated_data.items():
        setattr(instance, attr, value)
     instance.save()

    # Handle stock properly for each item
     old_items = {item.id: item for item in instance.sales_invoice_items.all()}
    
    # First, clear old invoice items
     instance.sales_invoice_items.all().delete()

     for item_data in items_data:
        product_item = item_data.get("product_item")
        service_item = item_data.get("service_item")
        quantity = item_data["quantity"]

        # If product_item exists
        if product_item:
            # Check if item already existed
            old_item = next((oi for oi in old_items.values() if oi.product_item == product_item), None)
            if old_item:
                # Add back old quantity
                product_item.opening_stock += old_item.quantity

            # Now check new stock availability
            if product_item.opening_stock < quantity:
                raise serializers.ValidationError({"quantity": f"Insufficient stock for {product_item.item_name}"})

            # Reduce new quantity
            product_item.opening_stock -= quantity
            product_item.save()

        elif service_item:
            old_item = next((oi for oi in old_items.values() if oi.service_item == service_item), None)
            if old_item:
                service_item.opening_stock += old_item.quantity

            if service_item.opening_stock < quantity:
                raise serializers.ValidationError({"quantity": f"Insufficient stock for {service_item.service_name}"})

            service_item.opening_stock -= quantity
            service_item.save()

        SalesInvoiceItem.objects.create(sales_invoice=instance, **item_data)

     return instance

class SalesInvoiceFromPOSerializer(serializers.ModelSerializer):
    sales_invoice_items = SalesInvoiceItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(source="total_amount.total", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = SalesInvoice
        fields = '__all__'