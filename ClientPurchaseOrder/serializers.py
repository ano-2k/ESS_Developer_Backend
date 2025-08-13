from rest_framework import serializers
from .models import ClientPurchaseOrder, ClientPurchaseOrderItem
from Create_New_Item.models import ProductItem, ServiceItem, GSTTax
from decimal import Decimal


class ClientPurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPurchaseOrderItem
        fields = [
            "id", "product", "service", "item_name",
            "quantity", "rate", "gst", "discount", "total_before_tax", "tax_amount", "total_after_tax"
        ]
        read_only_fields = ["item_name", "rate", "total_before_tax", "tax_amount", "total_after_tax"]


class ClientPurchaseOrderSerializer(serializers.ModelSerializer):
    items = ClientPurchaseOrderItemSerializer(many=True)
    po_file_upload = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ClientPurchaseOrder
        fields = [
            "id", "po_number", "po_date", "customer",
            "delivery_date", "remarks", "status", "po_file_upload", "created_at", "items"
        ]
        read_only_fields = ["created_at", "po_number"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        purchase_order = ClientPurchaseOrder.objects.create(**validated_data)

        for item_data in items_data:
            self._process_item_data(item_data)
            ClientPurchaseOrderItem.objects.create(purchase_order=purchase_order, **item_data)

        return purchase_order

    def _process_item_data(self, item_data):
        # Access the product and service
        product = item_data.get("product")  # Correct field name for product
        service = item_data.get("service")  # Correct field name for service

        if product:
            item_data["item_name"] = product.item_name
            item_data["rate"] = product.sales_price_without_tax or product.sales_price_with_tax
            item_data["gst"] = item_data.get("gst") or product.gst_tax
        elif service:
            item_data["item_name"] = service.service_name
            item_data["rate"] = service.sales_price_without_tax or service.sales_price_with_tax
            if not item_data.get("gst") and service.gst_tax_rate:
                item_data["gst"] = GSTTax.objects.filter(gst_rate=service.gst_tax_rate).first()

        # Calculate total amounts and taxes
        quantity = item_data.get("quantity", 0)
        rate = item_data.get("rate", 0)
        discount = item_data.get("discount", 0)
        item_data["total_before_tax"] = (quantity * rate) - discount
        
        # Calculate tax amount and total after tax
        gst_rate = item_data.get("gst").gst_rate if item_data.get("gst") else Decimal('0.00')
        item_data["tax_amount"] = (item_data["total_before_tax"] * gst_rate) / Decimal('100.00')
        item_data["total_after_tax"] = item_data["total_before_tax"] + item_data["tax_amount"]


class ClientPurchaseOrderUpdateSerializer(serializers.ModelSerializer):
    items = ClientPurchaseOrderItemSerializer(many=True)
    po_file_upload = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ClientPurchaseOrder
        fields = [
            "id", "po_number", "po_date", "customer", "sales_person",
            "delivery_date", "remarks", "status", "po_file_upload", "created_at", "items"
        ]
        read_only_fields = ["created_at", "po_number"]

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])

        # Update PO fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Remove old items and add new ones
        instance.items.all().delete()
        for item_data in items_data:
            self._process_item_data(item_data)
            ClientPurchaseOrderItem.objects.create(purchase_order=instance, **item_data)

        return instance

    def _process_item_data(self, item_data):
        product = item_data.get("product")  # Correct field name for product
        service = item_data.get("service")  # Correct field name for service

        if product:
            item_data["item_name"] = product.item_name
            item_data["rate"] = product.sales_price_without_tax or product.sales_price_with_tax
            item_data["gst"] = item_data.get("gst") or product.gst_tax
        elif service:
            item_data["item_name"] = service.service_name
            item_data["rate"] = service.sales_price_without_tax or service.sales_price_with_tax
            if not item_data.get("gst") and service.gst_tax_rate:
                item_data["gst"] = GSTTax.objects.filter(gst_rate=service.gst_tax_rate).first()

        quantity = item_data.get("quantity", 0)
        rate = item_data.get("rate", 0)
        discount = item_data.get("discount", 0)
        item_data["total_before_tax"] = (quantity * rate) - discount
        
        # Calculate tax amount and total after tax
        gst_rate = item_data.get("gst").gst_rate if item_data.get("gst") else Decimal('0.00')
        item_data["tax_amount"] = (item_data["total_before_tax"] * gst_rate) / Decimal('100.00')
        item_data["total_after_tax"] = item_data["total_before_tax"] + item_data["tax_amount"]
