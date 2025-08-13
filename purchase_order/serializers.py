from rest_framework import serializers
from .models import *
from Create_New_Item.models import ProductItem, GSTTax
from Pincode.models import AddParty


# --- Purchase Order Serializers ---

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    gst_rate = serializers.DecimalField(source='gst.gst_rate', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product', 'custom_item_name', 'custom_hsn',
            'product_name', 'quantity', 'rate', 'discount',
            'gst', 'gst_rate', 'total_before_tax',
            'tax_amount', 'total_after_tax'
        ]
        read_only_fields = ['total_before_tax', 'tax_amount', 'total_after_tax']

    def get_product_name(self, obj):
        return obj.product.item_name if obj.product else obj.custom_item_name


class PurchaseOrderTotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderTotalAmount
        fields = ['total_before_tax', 'total_tax', 'total']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    total_amount = PurchaseOrderTotalAmountSerializer(read_only=True)
    vendor_name = serializers.CharField(source='vendor.party_name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'po_number', 'vendor', 'vendor_name',
            'order_date', 'delivery_date', 'shipping_address',
            'notes', 'status', 'items', 'total_amount'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)
        PurchaseOrderTotalAmount.objects.create(purchase_order=purchase_order)
        purchase_order.update_totals()
        return purchase_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(purchase_order=instance, **item_data)
            instance.update_totals()

        return instance


# --- Purchase Order Email Log ---

class PurchaseOrderEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderEmailLog
        fields = '__all__'


# --- Vendor Invoice Serializers ---

class VendorInvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    gst_rate = serializers.DecimalField(source='gst.gst_rate', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = VendorInvoiceItem
        fields = [
            'id', 'product', 'custom_item_name', 'custom_hsn',
            'product_name', 'quantity', 'rate', 'discount',
            'gst', 'gst_rate', 'total_before_tax',
            'tax_amount', 'total_after_tax'
        ]
        read_only_fields = ['total_before_tax', 'tax_amount', 'total_after_tax']

    def get_product_name(self, obj):
        return obj.product.item_name if obj.product else obj.custom_item_name


class VendorInvoiceSerializer(serializers.ModelSerializer):
    items = VendorInvoiceItemSerializer(many=True)
    purchase_order_number = serializers.CharField(source='purchase_order.po_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.party_name', read_only=True)

    class Meta:
        model = VendorInvoice
        fields = [
            'id', 'vendor', 'vendor_name',
            'purchase_order', 'purchase_order_number',
            'invoice_number', 'invoice_date', 'uploaded_file',
            'total_before_tax', 'total_tax', 'total_amount',
            'supplier_to_pay', 'payment_status', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        invoice = VendorInvoice.objects.create(**validated_data)
        for item_data in items_data:
            VendorInvoiceItem.objects.create(vendor_invoice=invoice, **item_data)
        invoice.update_payment_status()
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                VendorInvoiceItem.objects.create(vendor_invoice=instance, **item_data)
        instance.update_payment_status()
        return instance



# --- Vendor Invoice Payments ---

class ConvertVendorInvoicePaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_method = serializers.CharField(max_length=50)
    notes = serializers.CharField(allow_blank=True, required=False)
    payment_date = serializers.DateField(required=False)
    uploaded_file = serializers.FileField(required=False)

    # ✅ Add this to include auto-generated payment_out_number in the response
    payment_out_number = serializers.CharField(read_only=True)

    def create(self, validated_data):
        vendor_invoice = validated_data.pop("vendor_invoice")  # comes from the view
        payment = VendorInvoicePayment.objects.create(
            vendor_invoice=vendor_invoice,
            **validated_data
        )
        return payment




class ListVendorPaymentSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source="vendor_invoice.vendor.party_name", read_only=True)
    invoice_number = serializers.CharField(source="vendor_invoice.invoice_number", read_only=True)

    class Meta:
        model = VendorInvoicePayment
        fields = ["id", "payment_date", "payment_method","payment_out_number", "amount", "vendor_name", "invoice_number", "notes", "uploaded_file"]
