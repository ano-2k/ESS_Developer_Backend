from rest_framework import serializers
from .models import *
from ClientPurchaseOrder.models import ClientPurchaseOrder  # ✅ Correct import
from Create_New_Item.models import ProductItem, ServiceItem, GSTTax


class ClientSalesOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    gst_rate = serializers.DecimalField(source='tax.gst_rate', max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = ClientSalesOrderItem
        fields = [
            'id', 'product_item', 'service_item', 'item_name', 'description', 'hsn_sac_code',
            'measuring_unit', 'quantity', 'price_per_item', 'discount', 'tax', 'total_amount',
            'product_name', 'gst_rate'
        ]
        read_only_fields = ['total_amount']

    def get_product_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        return None


class PurchaseOrderTotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSalesOrderTotalAmount
        fields = ['total']


class ClientSalesOrderSerializer(serializers.ModelSerializer):
    items = ClientSalesOrderItemSerializer(many=True)
    total_amount = PurchaseOrderTotalAmountSerializer(read_only=True)
    vendor_name = serializers.CharField(source='customer.party_name', read_only=True)

    class Meta:
        model = ClientSalesOrder
        fields = [
            'id', 'so_number','po_number', 'customer', 'vendor_name', 'sales_person',
            'so_date', 'delivery_date', 'remarks', 'status',
            'items', 'total_amount'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')

        # ❌ Removed purchase_order_id dependency

        # ✅ Create the ClientSalesOrder without linking to purchase_order
        client_sales_order = ClientSalesOrder.objects.create(**validated_data)

        # ✅ Create related items
        for item_data in items_data:
            ClientSalesOrderItem.objects.create(sales_order=client_sales_order, **item_data)

        # ✅ Recalculate total amount
        client_sales_order.update_total_amount()

        return client_sales_order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                ClientSalesOrderItem.objects.create(sales_order=instance, **item_data)
            instance.update_total_amount()

        return instance


class ClientSalesOrderEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSalesOrderEmailLog
        fields = '__all__'
        read_only_fields = ['status', 'sent_at', 'updated_at']