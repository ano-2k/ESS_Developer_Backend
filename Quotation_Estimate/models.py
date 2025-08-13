from django.db import models
from django.utils import timezone
from Pincode.models import *
from decimal import Decimal
from Create_New_Item.models import *
#make a xhange 
class QuotationEstimate(models.Model):
    STATUS_CHOICES = [
        ("Open", "open"),  # 'Open' has 4 characters
        ("Convert_into_Invoice", "convert_into_invoice"),  # 'Convert_into_Invoice' has 20 characters
    ]

    party = models.ForeignKey(AddParty, on_delete=models.CASCADE, related_name="quotation_estimates")
    quotation_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generated
    quotation_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(blank=True, null=True)  # New field for due date
    party_name = models.CharField(max_length=255, blank=True)
    party_mobile_number = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True, null=True)
    sales_person = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL, related_name="quotation_estimate", null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="Open")  # Increased max_length to 30

    def save(self, *args, **kwargs):
        """Ensure quotation_number is set correctly"""
        if not self.quotation_number:
            last_quotation = QuotationEstimate.objects.order_by('-id').first()
            next_number = 1 if not last_quotation else int(last_quotation.quotation_number.split('-')[1]) + 1
            self.quotation_number = f"QUO-{next_number:05d}"

        # Fetch party details
        if self.party:
            self.party_name = self.party.party_name
            self.party_mobile_number = self.party.mobile_number
            try:
                shipping_address = self.party.shipping_address
                self.shipping_address = f"{shipping_address.street}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pincode}"
            except ShippingAddress.DoesNotExist:
                self.shipping_address = "No Shipping Address"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Quotation Estimate {self.quotation_number} for {self.party_name}"



class QuotationEstimateItem(models.Model):
    quotation = models.ForeignKey(QuotationEstimate, on_delete=models.CASCADE, related_name="quotation_items")
    
    product_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotation_items")
    service_item = models.ForeignKey(ServiceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotation_services")

    item_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    hsn_sac_code = models.CharField(max_length=20, blank=True, null=True)
    measuring_unit = models.CharField(max_length=10, blank=True)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.ForeignKey(GSTTax, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
     if self.product_item:
        self.item_name = self.product_item.item_name
        self.description = self.product_item.description
        self.hsn_sac_code = self.product_item.hsn_code
        self.measuring_unit = self.product_item.measuring_unit

        if self.product_item.sales_price_without_tax is not None:
            self.price_per_item = self.product_item.sales_price_without_tax
        elif self.product_item.sales_price_with_tax is not None:
            self.price_per_item = self.product_item.sales_price_with_tax

        # ✅ Only auto-assign tax if not already provided
        if not self.tax and self.product_item.gst_tax:
            self.tax = self.product_item.gst_tax

     elif self.service_item:
        self.item_name = self.service_item.service_name
        self.description = self.service_item.service_description
        self.hsn_sac_code = self.service_item.sac_code
        self.measuring_unit = self.service_item.measuring_unit

        if self.service_item.sales_price_without_tax is not None:
            self.price_per_item = self.service_item.sales_price_without_tax
        elif self.service_item.sales_price_with_tax is not None:
            self.price_per_item = self.service_item.sales_price_with_tax

        if not self.tax and self.service_item.gst_tax_rate and self.service_item.gst_tax_rate != "exempted":
            try:
                # Optional: fetch GSTTax object if needed
                self.tax = GSTTax.objects.get(gst_rate=self.service_item.gst_tax_rate)
            except GSTTax.DoesNotExist:
                self.tax = None
 
     if self.price_per_item and self.quantity:
        subtotal = self.quantity * self.price_per_item
        self.amount = subtotal - self.discount

     super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.item_name} - {self.quantity} x {self.price_per_item}"



class TotalQuotationEstimateAmount(models.Model):
    quotation = models.OneToOneField(QuotationEstimate, on_delete=models.CASCADE, related_name="total_amount")
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        """Calculate and store the total for the related Quotation"""
        if self.quotation:
            self.total = self.quotation.quotation_items.aggregate(models.Sum("amount"))["amount__sum"] or 0.00
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Total Amount for {self.quotation.quotation_number}: {self.total}"

class QuotationEstimateEmailLog(models.Model):
    quotation_estimate = models.ForeignKey('QuotationEstimate', on_delete=models.CASCADE, related_name="email_logs")
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[("sent", "Sent"), ("failed", "Failed")], default="sent")

    def __str__(self):
        return f"Email to {self.email} - {self.quotation_estimate.quotation_number}"
