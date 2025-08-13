from rest_framework import serializers
from .models import *
from datetime import datetime

class GSTTaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = GSTTax
        fields = ['id', 'name', 'gst_rate', 'cess_rate']

# ProductItem Serializer
class ProductItemSerializer(serializers.ModelSerializer):
    gst_tax = serializers.PrimaryKeyRelatedField(queryset=GSTTax.objects.all())  
    type = serializers.SerializerMethodField()
    
    # Custom field to handle datetime to date conversion
    def validate_as_of_date(self, value):
        """ Convert datetime to date if it's a datetime object """
        if isinstance(value, datetime):
            return value.date()  # Return only the date part of datetime
        return value  # Otherwise return the value as is

    def get_type(self, obj):
        return "product"

    class Meta:
        model = ProductItem
        fields = ['id', 'item_name', 'sales_price_without_tax', 'sales_price_with_tax', 
                  'gst_tax', 'measuring_unit', 'opening_stock', 'final_total', 'type', 
                  'product_code', 'hsn_code', 'stock_image', 'barcode_image', 'description', 
                  'low_stock_warning', 'purchase_price', 'stock_threshold', 'as_of_date']

    # Ensure that as_of_date is converted to date if it is datetime
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if isinstance(representation.get('as_of_date'), str):
            # If it's a datetime string, convert to date
            try:
                representation['as_of_date'] = representation['as_of_date'].split('T')[0]
            except Exception as e:
                pass  # Handle exception if necessary
        
        return representation

class ServiceItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    description = serializers.CharField(read_only=True)  # Make description read-only as it's auto-filled in the model

    def get_type(self, obj):
        return "service"

    class Meta:
        model = ServiceItem
        fields = ['id', 'service_name', 'sales_price_without_tax', 'sales_price_with_tax', 
                  'gst_tax_rate','opening_stock', 'measuring_unit', 'service_code', 'final_total', 'service_description',
                  'sac_code', 'description', 'type']  # Include 'sac_code' and 'description'

    def validate_sac_code(self, value):
        """Ensure SAC code exists in the SACCode model"""
        if not SACCode.objects.filter(sac_code=value).exists():
            raise serializers.ValidationError(f"SAC Code {value} does not exist. Please enter a valid SAC code.")
        return value

class HSNCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HSNCode
        fields = '__all__'
        
class SACCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SACCode
        fields = ["sac_code", "description"]
