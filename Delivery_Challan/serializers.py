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

class DeliveryChallanItemSerializer(serializers.ModelSerializer):
    product_item_name = serializers.CharField(source="product_item.name", read_only=True)
    service_item_name = serializers.CharField(source="service_item.name", read_only=True)
    item_name = serializers.SerializerMethodField()
    tax = TaxSerializer(read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all(), write_only=True, source="tax")
  
    class Meta:
        model = DeliveryChallanItem
        fields = ["product_item", "service_item","tax", "tax_id", "quantity", "discount", "price_per_item", "amount","product_item_name", "service_item_name", "item_name"]
        extra_kwargs = {
            "delivery_challan": {"required": False}  # Make delivery_challan optional
        }
    def get_item_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        else:
            return None

class CombinedDeliveryChallanSerializer(serializers.ModelSerializer):
    items = DeliveryChallanItemSerializer(many=True, write_only=True)

    class Meta:
        model = DeliveryChallan
        fields = ["party","sales_person", "delivery_challan_date","delivery_challan_number", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        delivery_challan = DeliveryChallan.objects.create(**validated_data)
        
        # Create DeliveryChallanItem instances and assign the delivery_challan
        for item_data in items_data:
            DeliveryChallanItem.objects.create(delivery_challan=delivery_challan, **item_data)
        
        # Create and save the total amount for the delivery_challan
        DeliveryChallanTotalAmount.objects.create(delivery_challan=delivery_challan)

        return delivery_challan
    
    def update(self, instance, validated_data):
     items_data = validated_data.pop('items', [])

    # Update basic DeliveryChallan fields
     for attr, value in validated_data.items():
        setattr(instance, attr, value)
     instance.save()

    # Delete existing DeliveryChallanItems
     instance.delivery_challan_items.all().delete()

    # Create new DeliveryChallanItems
     for item_data in items_data:
        DeliveryChallanItem.objects.create(delivery_challan=instance, **item_data)

     return instance


class DeliveryChallanSerializer(serializers.ModelSerializer):
    delivery_challan_items = DeliveryChallanItemSerializer(many=True, read_only=True)

    class Meta:
        model = DeliveryChallan
        fields = "__all__"

class DeliveryChallanTotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallanTotalAmount
        fields = ["delivery_challan", "total"]

class DeliveryChallanEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallanEmailLog
        fields = ['delivery_challan', 'email', 'sent_at', 'updated_at', 'status']

class DeliveryChallanItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryChallanItem
        fields = "__all__"

class DeliveryChallanDetailSerializer(serializers.ModelSerializer):
    delivery_challan_items = DeliveryChallanItemReadSerializer(many=True, read_only=True)
    total_amount = DeliveryChallanTotalAmountSerializer(read_only=True)

    class Meta:
        model = DeliveryChallan
        fields = "__all__"

class DeliveryChallanResponseSerializer(serializers.ModelSerializer):
    delivery_challan_items = DeliveryChallanItemSerializer(many=True, read_only=True)
    delivery_challan_total = DeliveryChallanTotalAmountSerializer(source="total_amount", read_only=True)
    delivery_challan_number = serializers.CharField
    delivery_challan_date = serializers.DateField
    party_name = serializers.CharField(source="party.name", read_only=True)
    party_mobile_number = serializers.CharField(source="party.mobile_number", read_only=True)
    shipping_address = serializers.CharField(source="party.shipping_address", read_only=True)
    sales_person = SalesPersonSerializer(read_only=True)

    class Meta:
        model = DeliveryChallan
        fields = [
            "id", "party", "delivery_challan_items", "delivery_challan_total","sales_person",
            "delivery_challan_number", "delivery_challan_date",
            "party_name", "party_mobile_number", "shipping_address", "status"
        ]
