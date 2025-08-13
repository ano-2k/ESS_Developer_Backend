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

class QuotationEstimateItemSerializer(serializers.ModelSerializer):
    product_item_name = serializers.CharField(source="product_item.name", read_only=True)
    service_item_name = serializers.CharField(source="service_item.name", read_only=True)
    item_name = serializers.SerializerMethodField()
    tax = TaxSerializer(read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all(), write_only=True, source="tax")
  

    class Meta:
        model = QuotationEstimateItem
        fields = [
            "product_item", "service_item", "quantity", "discount", "price_per_item", "amount",
            "product_item_name","tax", "tax_id", "service_item_name", "item_name"  # <-- new
        ]
        extra_kwargs = {
            "quotation": {"required": False}
        }

    def get_item_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        else:
            return None

class CombinedQuotationEstimateSerializer(serializers.ModelSerializer):
    items = QuotationEstimateItemSerializer(many=True, write_only=True)

    class Meta:
        model = QuotationEstimate
        fields = ["party","sales_person", "quotation_date","due_date","quotation_number", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        quotation = QuotationEstimate.objects.create(**validated_data)
        
        # Create QuotationEstimateItem instances and assign the quotation
        for item_data in items_data:
            QuotationEstimateItem.objects.create(quotation=quotation, **item_data)
        
        # Create and save the total amount for the quotation
        TotalQuotationEstimateAmount.objects.create(quotation=quotation)

        return quotation
    def update(self, instance, validated_data):
     items_data = validated_data.pop('items', [])

    # Update basic QuotationEstimate fields
     for attr, value in validated_data.items():
        setattr(instance, attr, value)
     instance.save()

    # Delete existing QuotationEstimateItems
     instance.quotation_estimate_items.all().delete()

    # Create new QuotationEstimateItems
     for item_data in items_data:
        QuotationEstimateItem.objects.create(quotation=instance, **item_data)

     return instance



class TotalQuotationEstimateAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotalQuotationEstimateAmount
        fields = ["total"]


class QuotationEstimateSerializer(serializers.ModelSerializer):
    quotation_items = QuotationEstimateItemSerializer(many=True, read_only=True)
    total_amount = TotalQuotationEstimateAmountSerializer(read_only=True)

    class Meta:
        model = QuotationEstimate
        fields = "__all__"
class QuotationEstimateResponseSerializer(serializers.ModelSerializer):
    quotation_estimate_item = QuotationEstimateItemSerializer(source="quotation_items", many=True, read_only=True)
    quotation_estimate = TotalQuotationEstimateAmountSerializer(source="total_amount", read_only=True)

    # Use field name as-is (no source needed here)
    quotation_number = serializers.CharField()
    quotation_date = serializers.DateField()
    sales_person = SalesPersonSerializer(read_only=True)
    party_name = serializers.CharField(source="party.name", read_only=True)
    party_mobile_number = serializers.CharField(source="party.mobile_number", read_only=True)
    shipping_address = serializers.CharField(source="party.shipping_address", read_only=True)

    class Meta:
        model = QuotationEstimate
        fields = [
            "id", "party", "quotation_estimate_item", "quotation_estimate","sales_person",
            "quotation_number", "quotation_date", "due_date",
            "party_name", "party_mobile_number", "shipping_address"
        ]


