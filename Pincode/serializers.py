from rest_framework import serializers
from .models import *
from Sales_Person.serializers import*

# class AddPartySerializer(serializers.ModelSerializer):
#     sales_person = serializers.PrimaryKeyRelatedField(queryset=SalesPerson.objects.all(), required=True)  # Use ID to reference SalesPerson
    
#     class Meta:
#         model = AddParty
#         fields = '__all__'

class AddPartySerializer(serializers.ModelSerializer):
    sales_person_id = serializers.PrimaryKeyRelatedField(
        queryset=SalesPerson.objects.all(),
        source='sales_person',
        write_only=True,
        required=False  
    )
    sales_person = SalesPersonSerializer(read_only=True)

    class Meta:
        model = AddParty
        fields = [
            'id', 'party_name', 'mobile_number', 'email',
            'opening_balance_to_collect', 'opening_balance_to_pay',
            'gstin', 'pan_number', 'party_type', 'party_category',
            'credit_period_days', 'credit_limit_rupees',
            'sales_person', 'sales_person_id'
        ]

    def create(self, validated_data):
        sales_person = validated_data.pop('sales_person', None)
        party = AddParty.objects.create(**validated_data, sales_person=sales_person)
        return party

    def update(self, instance, validated_data):
        sales_person = validated_data.pop('sales_person', None)
        if sales_person is not None:
            instance.sales_person = sales_person
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class BillingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields =  ['party', 'street', 'state', 'pincode', 'city']

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['party', 'street', 'state', 'pincode', 'city', 'is_same_as_billing_address']

    def validate(self, data):
        if data.get('is_same_as_billing_address') and not data.get('street'):
            # Automatically copy the billing address if "same as billing address" is selected
            billing_address = data.get('party').billing_address
            data['street'] = billing_address.street
            data['state'] = billing_address.state
            data['pincode'] = billing_address.pincode
            data['city'] = billing_address.city
        return data

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = "__all__"
        
# General Details Serializer
class GeneralDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddParty
        fields = ['party_name', 'party_type', 'mobile_number', 'party_category', 'email', 'opening_balance']

# Business Details Serializer (GSTIN, PAN, Address)
class BusinessDetailsSerializer(serializers.ModelSerializer):
    billing_address = serializers.CharField(source="billing_address.street")
    billing_state = serializers.CharField(source="billing_address.state")
    billing_pincode = serializers.CharField(source="billing_address.pincode")
    billing_city = serializers.CharField(source="billing_address.city")
    shipping_address = serializers.CharField(source="shipping_address.street")
    shipping_state = serializers.CharField(source="shipping_address.state")
    shipping_pincode = serializers.CharField(source="shipping_address.pincode")
    shipping_city = serializers.CharField(source="shipping_address.city")
    
    class Meta:
        model = AddParty
        fields = ['gstin', 'pan_number', 'billing_address', 'billing_state', 'billing_pincode', 'billing_city', 'shipping_address', 'shipping_state', 'shipping_pincode', 'shipping_city']
# Credit Details Serializer
class CreditDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddParty
        fields = ['credit_period_days', 'credit_limit_rupees']

# Fetch all Party Details
class PartyDetailsSerializer(serializers.ModelSerializer):
    general_details = GeneralDetailsSerializer(source='*', read_only=True)
    business_details = BusinessDetailsSerializer(source='*', read_only=True)
    credit_details = CreditDetailsSerializer(source='*', read_only=True)

    class Meta:
        model = AddParty
        fields = ['general_details', 'business_details', 'credit_details']
        
# Party List Serializer
class PartyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddParty
        fields = ['party_name', 'party_category', 'mobile_number', 'party_type', 'opening_balance']     

class AddPartyDetailSerializer(serializers.ModelSerializer):
    """Serializer for Party Details including Billing & Shipping Address."""
    billing_address = BillingAddressSerializer(read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = AddParty
        fields = ["id", "party_name", "mobile_number", "email", "gstin", "pan_number", "billing_address", "shipping_address"]


class SalesPersonDetailSerializer(serializers.ModelSerializer):
    parties = AddPartySerializer(many=True, read_only=True)  # Use AddPartySerializer for nested party data

    class Meta:
        model = SalesPerson
        fields = "__all__"