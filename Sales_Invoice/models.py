from django.db import models
from django.utils import timezone
from Sales_Person.models import *
from Pincode.models import *
from datetime import date
from decimal import Decimal
from Create_New_Item.models import *
from ClientPurchaseOrder.models import *

class SalesInvoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ("partially paid", "Partially Paid"),
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
    ]
    PAYMENT_TERM_CHOICES = [
        ("0", "Due on Receipt"),
        ("15", "Net 15"),
        ("30", "Net 30"),
        ("45", "Net 45"),
        ("60", "Net 60"),
    ]
    party = models.ForeignKey(AddParty, on_delete=models.CASCADE, related_name="sales_invoices")
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generated
    invoice_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField(blank=True, null=True)  # New field for due date
    payment_terms = models.CharField(max_length=5,choices=PAYMENT_TERM_CHOICES,default="30",blank=True, null=True,help_text="Select payment term (e.g., Net 30)")
    party_name = models.CharField(max_length=255, blank=True)
    party_mobile_number = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True, null=True)
    sales_person = models.ForeignKey(SalesPerson, on_delete=models.CASCADE, related_name="sales_invoices", null=True, blank=True)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    total_paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    purchase_order = models.ForeignKey(ClientPurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_invoices")

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = SalesInvoice.objects.order_by('-id').first()
            next_number = 1 if not last_invoice else int(last_invoice.invoice_number.split('-')[1]) + 1
            self.invoice_number = f"INV-{next_number:05d}"

        if self.party:
            self.party_name = self.party.party_name
            self.party_mobile_number = self.party.mobile_number
            try:
                shipping_address = self.party.shipping_address
                self.shipping_address = f"{shipping_address.street}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pincode}"
            except ShippingAddress.DoesNotExist:
                self.shipping_address = "No Shipping Address"

        super().save(*args, **kwargs)

    def update_payment_status(self):
        total_amount = self.total_amount.total if self.total_amount else Decimal("0.00")

        if self.total_paid_amount == Decimal("0.00"):
            self.payment_status = "unpaid"
        elif self.total_paid_amount < total_amount:
            self.payment_status = "partially paid"
        else:
            self.payment_status = "paid"

        self.balance_amount = total_amount - self.total_paid_amount
        self.save(update_fields=["payment_status", "balance_amount"])

    def __str__(self):
        return f"Sales Invoice {self.invoice_number} for {self.party_name}"
    
    def get_purchase_order_info(self):
        if self.purchase_order:
            return f"PO Number: {self.purchase_order.po_number}, PO ID: {self.purchase_order.id}"
        return "No purchase order linked"
    
    # @property
    # def outstanding_amount(self):
    #     return self.total_amount.total - self.amount_paid if self.total_amount else 0

    @property
    def outstanding_amount(self):
     if self.total_amount:
         return self.total_amount.total - self.total_paid_amount
     return Decimal("0.00")

    @property
    def overdue_amount(self):
        if self.due_date and self.due_date < date.today() and self.payment_status != "paid":
            return self.outstanding_amount
        return 0

class SalesInvoiceItem(models.Model):
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name="sales_invoice_items")
    product_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_invoice_items")
    service_item = models.ForeignKey(ServiceItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_invoice_services")
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


class TotalAmount(models.Model):
    sales_invoice = models.OneToOneField(SalesInvoice, on_delete=models.CASCADE, related_name="total_amount")
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
     """Calculate and store the total for the related SalesInvoice"""
     if self.sales_invoice:
        self.total = self.sales_invoice.sales_invoice_items.aggregate(
            models.Sum("amount")
        )["amount__sum"] or 0.00

        # ✅ Update total_sales for the associated SalesPerson
        sales_person = getattr(self.sales_invoice, "sales_person", None)
        if sales_person:
            from django.db.models import Sum  # ensure import at the top

            total_sales = TotalAmount.objects.filter(
                sales_invoice__sales_person=sales_person
            ).aggregate(Sum("total"))["total__sum"] or 0.00

            sales_person.total_sales = total_sales
            sales_person.save()

     super().save(*args, **kwargs)



class SalesInvoiceEmailLog(models.Model):
    sales_invoice = models.ForeignKey('SalesInvoice', on_delete=models.CASCADE, related_name="email_logs")
    email = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[("sent", "Sent"), ("failed", "Failed")], default="sent")

    def __str__(self):
        return f"Email to {self.email} - {self.sales_invoice.invoice_number}"
