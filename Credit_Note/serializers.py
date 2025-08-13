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

class CreditNoteItemSerializer(serializers.ModelSerializer):
    product_item_name = serializers.CharField(source="product_item.name", read_only=True)
    service_item_name = serializers.CharField(source="service_item.name", read_only=True)
    item_name = serializers.SerializerMethodField()
    tax = TaxSerializer(read_only=True)
    tax_id = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all(), write_only=True, source="tax")
  
    class Meta:
        model = CreditNoteItem
        fields = ["product_item", "service_item", "quantity", "discount", "price_per_item", "amount"
                  ,"product_item_name","tax", "tax_id", "service_item_name", "item_name"]
        extra_kwargs = {
            "credit_note": {"required": False}  # Allow optional credit_note field
        }

    def get_item_name(self, obj):
        if obj.product_item:
            return obj.product_item.item_name
        elif obj.service_item:
            return obj.service_item.service_name
        else:
            return None

    def create(self, validated_data):
        # Ensure credit_note is set if not provided, otherwise get it from context (e.g., parent model)
        credit_note = self.context.get("credit_note", None)  # Get from view context if it's a child object

        if credit_note and "credit_note" not in validated_data:
            validated_data["credit_note"] = credit_note

        return super().create(validated_data)


class CombinedCreditNoteSerializer(serializers.ModelSerializer):
    items = CreditNoteItemSerializer(many=True, write_only=True)

    class Meta:
        model = CreditNote
        fields = ["party","sales_person", "credit_note_date","due_date","credit_note_number", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        credit_note = CreditNote.objects.create(**validated_data)
        
        # Create CreditNoteItem instances and assign the credit_note
        for item_data in items_data:
            CreditNoteItem.objects.create(credit_note=credit_note, **item_data)
        
        # Create and save the total amount for the credit_note
        CreditNoteTotalAmount.objects.create(credit_note=credit_note)

        return credit_note
    def update(self, instance, validated_data):
     items_data = validated_data.pop('items', [])

    # Update basic CreditNote fields
     for attr, value in validated_data.items():
        setattr(instance, attr, value)
     instance.save()

    # Delete existing CreditNoteItems
     instance.credit_note_items.all().delete()

    # Create new CreditNoteItems
     for item_data in items_data:
        CreditNoteItem.objects.create(credit_note=instance, **item_data)

     return instance



class CreditNoteTotalAmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNoteTotalAmount
        fields = ["credit_note", "total"]


class CreditNoteSerializer(serializers.ModelSerializer):
    credit_note_items = CreditNoteItemSerializer(many=True, read_only=True)
    total_amount = CreditNoteTotalAmountSerializer(read_only=True)


    class Meta:
        model = CreditNote
        fields = "__all__"

class CreditNoteEmailLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNoteEmailLog
        fields = ['credit_note', 'email', 'sent_at', 'updated_at', 'status']

class CreditNoteResponseSerializer(serializers.ModelSerializer):
    credit_note_items = CreditNoteItemSerializer(many=True, read_only=True)
    credit_note_total = CreditNoteTotalAmountSerializer(source="total_amount", read_only=True)
    credit_note_number = serializers.CharField()
    credit_note_date = serializers.DateField()
    party_name = serializers.CharField(source="party.name", read_only=True)
    party_mobile_number = serializers.CharField(source="party.mobile_number", read_only=True)
    shipping_address = serializers.CharField(source="party.shipping_address", read_only=True)
    sales_person = SalesPersonSerializer(read_only=True)

    class Meta:
        model = CreditNote
        fields = [
            "id", "party", "credit_note_items", "credit_note_total","sales_person",
            "credit_note_number", "credit_note_date", "due_date",
            "party_name", "party_mobile_number", "shipping_address", "status"
        ]
