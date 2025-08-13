
from rest_framework import serializers
from .models import *

class ARReminderSerializer(serializers.ModelSerializer):

    class Meta:
        model = ARReminder
        fields = '__all__'


# NEWLY ADDED ON JUNE 09 
class ARClientTargetSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.party_name', read_only=True)

    class Meta:
        model = ARClientTarget
        fields = ['id', 'client', 'sales_person', 'target_amount', 'start_date', 'end_date', 'client_name']
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ARClientTarget.objects.all(),
                fields=['client', 'sales_person', 'start_date', 'end_date'],
                message="A target for this client, salesperson, and date range already exists."
            )
        ]


class AREmployeeTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AREmployeeTarget
        fields = '__all__'


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = '__all__'