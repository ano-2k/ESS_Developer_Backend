from django.db import models

# Create your models here.


from django.db import models
from django.utils import timezone
from django.db.models import Sum, Q, F
from rest_framework import serializers, views, response, status
from rest_framework.decorators import api_view
from datetime import timedelta
from Pincode.models import AddParty
from authentication.models import Employee
from Sales_Invoice.models import SalesInvoice, SalesInvoiceItem, TotalAmount
from Payment_In.models import RecordPayment
from datetime import date
from Sales_Person.models import SalesPerson

# =============== MODELS ===============
class ARReminder(models.Model):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name="reminders")
    sent_at = models.DateTimeField(auto_now_add=True)
    expected_payment_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    sent_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

#NEWLY ADDED ON JUNE 09
class ARClientTarget(models.Model):
    client = models.ForeignKey(AddParty, on_delete=models.CASCADE, related_name="ar_targets")
    sales_person = models.ForeignKey(SalesPerson, on_delete=models.CASCADE,null=True, related_name="ar_client_targets")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['client', 'sales_person', 'start_date', 'end_date'],
                name='unique_target_per_client_salesperson_date'
            )
        ]
    def __str__(self):
        return f"Target for {self.client.party_name} by {self.sales_person.name}"
    
    
    
    
class AREmployeeTarget(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="collection_targets")
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()



class ClientAR(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class EmployeeAR(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Target(models.Model):
    client = models.CharField(max_length=100, null=True, blank=True)
    employee = models.CharField(max_length=100, null=True, blank=True)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.client or self.employee} - ${self.target_amount}"
