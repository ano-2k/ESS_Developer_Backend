from django.db import models
from django.utils.timezone import now
from Sales_Person.models import *
import requests
 
class AddParty(models.Model):
    party_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    opening_balance_to_collect = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    opening_balance_to_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gstin = models.CharField(max_length=15, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    party_type = models.CharField(max_length=50, choices=[("customer", "Customer"), ("supplier", "Supplier")])
    party_category = models.TextField()
    credit_period_days = models.IntegerField(default=0)
    credit_limit_rupees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sales_person = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL, null=True, blank=True, related_name="parties")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.sales_person:
            self.sales_person.clients_handled = self.sales_person.parties.count()
            self.sales_person.save()

    def __str__(self):
        return self.party_name

# Billing Address Model
class BillingAddress(models.Model):
    party = models.OneToOneField(AddParty, on_delete=models.CASCADE, related_name="billing_address")
    street = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    city = models.CharField(max_length=100,blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.city:  # Fetch city if not provided
            self.city = fetch_city_from_pincode(self.pincode)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Billing Address for {self.party.party_name}"


# Shipping Address Model
class ShippingAddress(models.Model):
    party = models.OneToOneField(AddParty, on_delete=models.CASCADE, related_name="shipping_address")
    street = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    is_same_as_billing_address = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_same_as_billing_address:
            billing = self.party.billing_address
            self.street = billing.street
            self.state = billing.state
            self.pincode = billing.pincode
            self.city = billing.city
        else:
            if self.pincode:  # Fetch city if different address
                self.city = fetch_city_from_pincode(self.pincode)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Shipping Address for {self.party.party_name}"


# Function to Fetch City from Pincode
def fetch_city_from_pincode(pincode):
    url = f"https://api.postalpincode.in/pincode/{pincode}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data[0]['Status'] == 'Success':
        return data[0]['PostOffice'][0]['District']
    return None  # Return None if API fails

class BankDetails(models.Model):
    party = models.OneToOneField(AddParty, on_delete=models.CASCADE, related_name="bank_details")
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)

    def __str__(self):
        return f"Bank Details for {self.party.party_name}"