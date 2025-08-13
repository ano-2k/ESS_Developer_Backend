from django.db import models
from datetime import date
from django.utils import timezone
from decimal import Decimal
from Pincode.models import AddParty
from Create_New_Item.models import ProductItem, GSTTax
from django.db import models
from django.utils import timezone

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        
    ]

    vendor = models.ForeignKey(AddParty,on_delete=models.CASCADE,limit_choices_to={'party_type': 'supplier'},related_name="purchase_orders")
    po_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    order_date = models.DateField(default=timezone.localdate)
    delivery_date = models.DateField(blank=True, null=True)

    vendor_name = models.CharField(max_length=255, blank=True)
    vendor_mobile_number = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            last_po = PurchaseOrder.objects.exclude(po_number__isnull=True).exclude(po_number='').order_by('-id').first()
            next_number = 1
            if last_po and last_po.po_number and '-' in last_po.po_number:
                try:
                    next_number = int(last_po.po_number.split('-')[1]) + 1
                except ValueError:
                    pass  # fallback to 1
            self.po_number = f"PO-{next_number:05d}"

        if self.vendor:
            self.vendor_name = self.vendor.party_name
            self.vendor_mobile_number = self.vendor.mobile_number
            try:
                shipping_address = self.vendor.shipping_address
                self.shipping_address = f"{shipping_address.street}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pincode}"
            except Exception:
                self.shipping_address = "No Shipping Address"

        super().save(*args, **kwargs)

    def update_totals(self):
        items = self.items.all()
        subtotal = sum(item.total_before_tax for item in items)
        tax_total = sum(item.tax_amount for item in items)
        total = subtotal + tax_total

        if hasattr(self, 'total_amount'):
            self.total_amount.total_before_tax = subtotal
            self.total_amount.total_tax = tax_total
            self.total_amount.total = total
            self.total_amount.save()

    def __str__(self):
        return f"{self.po_number} - {self.vendor_name}"


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True)

    custom_item_name = models.CharField(max_length=255, blank=True, null=True)
    custom_hsn = models.CharField(max_length=20, blank=True, null=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    gst = models.ForeignKey(GSTTax, on_delete=models.SET_NULL, null=True, blank=True)

    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_after_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_before_tax = (self.quantity * self.rate) - self.discount
        gst_rate = self.gst.gst_rate if self.gst else Decimal('0.00')
        self.tax_amount = (self.total_before_tax * gst_rate) / Decimal('100.00')
        self.total_after_tax = self.total_before_tax + self.tax_amount

        super().save(*args, **kwargs)
        self.purchase_order.update_totals()

    def __str__(self):
        item = self.product.item_name if self.product else self.custom_item_name or "Manual Item"
        return f"{item} - Qty: {self.quantity}"


class PurchaseOrderTotalAmount(models.Model):
    purchase_order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name="total_amount")
    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.purchase_order.po_number} - ₹{self.total}"


class PurchaseOrderEmailLog(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="email_logs")
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=[("sent", "Sent"), ("failed", "Failed")], default="sent")
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Email to {self.email} - {self.purchase_order.po_number}"


class VendorInvoice(models.Model):
    vendor = models.ForeignKey(
    AddParty,
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    limit_choices_to={'party_type': 'supplier'},
    related_name="vendor_invoices"
)

    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE,related_name='vendor_invoices', null=True)
    invoice_number = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    uploaded_file = models.FileField(upload_to='vendor_invoices/', null=True, blank=True)
    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    supplier_to_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partially_paid', 'Partially Paid'),
        ('paid', 'Paid'),
    ]
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')

    def update_payment_status(self):
        total_paid = sum(payment.amount for payment in self.payments.all())
        total_invoice_amount = self.total_amount or 0
        remaining = total_invoice_amount - total_paid
        self.supplier_to_pay = max(remaining, 0)

        if remaining <= 0:
            self.payment_status = 'paid'
        elif total_paid > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'unpaid'

        self.save()

        if self.purchase_order and self.purchase_order.vendor:
            supplier = self.purchase_order.vendor
            total_outstanding = VendorInvoice.objects.filter(
                purchase_order__vendor=supplier
            ).aggregate(
                total_due=models.Sum('supplier_to_pay')
            )['total_due'] or 0

            supplier.opening_balance_to_pay = total_outstanding
            supplier.save()

    def __str__(self):
        return f"Invoice {self.invoice_number} for PO {self.purchase_order.po_number if self.purchase_order else ''}"


class VendorInvoiceItem(models.Model):
    vendor_invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True)

    custom_item_name = models.CharField(max_length=255, blank=True, null=True)
    custom_hsn = models.CharField(max_length=20, blank=True, null=True)

    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    gst = models.ForeignKey(GSTTax, on_delete=models.SET_NULL, null=True, blank=True)

    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_after_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.total_before_tax = (self.quantity * self.rate) - self.discount
        gst_rate = self.gst.gst_rate if self.gst else Decimal('0.00')
        self.tax_amount = (self.total_before_tax * gst_rate) / Decimal('100.00')
        self.total_after_tax = self.total_before_tax + self.tax_amount

        super().save(*args, **kwargs)

        # Update invoice totals
        self.vendor_invoice.total_before_tax = sum(item.total_before_tax for item in self.vendor_invoice.items.all())
        self.vendor_invoice.total_tax = sum(item.tax_amount for item in self.vendor_invoice.items.all())
        self.vendor_invoice.total_amount = sum(item.total_after_tax for item in self.vendor_invoice.items.all())
        self.vendor_invoice.supplier_to_pay = self.vendor_invoice.total_amount or 0
        self.vendor_invoice.save()

    def __str__(self):
        item = self.product.item_name if self.product else self.custom_item_name or "Manual Item"
        return f"{item} - Qty: {self.quantity}"


class VendorInvoicePayment(models.Model):
    PAYMENT_MODES = [
        ("Cash", "Cash"),
        ("Bank Transfer", "Bank Transfer"),
        ("UPI", "UPI"),
        ("Cheque", "Cheque"),
        ("Other", "Other"),
    ]
    vendor = models.ForeignKey(AddParty,on_delete=models.CASCADE,limit_choices_to={'party_type': 'supplier'},related_name="vendor_invoice_payments",null=True)
    vendor_invoice = models.ForeignKey(VendorInvoice, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateField(default=timezone.localdate)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_MODES, default="Cash")
    payment_out_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generated
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    uploaded_file = models.FileField(upload_to='vendor_invoice_payments/', null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        # Auto-generate unique payment number
        if not self.payment_out_number:
            last_payment = VendorInvoicePayment.objects.order_by('-id').first()
            next_number = 1 if not last_payment else int(last_payment.payment_out_number.split('-')[1]) + 1
            self.payment_out_number = f"PAYOUT-{next_number:05d}"

        super().save(*args, **kwargs)

        # 🔄 Recalculate total paid and update status
        if self.vendor_invoice:
            total_paid = self.vendor_invoice.payments.aggregate(
                total=models.Sum('amount')
            )['total'] or Decimal("0.00")

            self.vendor_invoice.total_paid_amount = total_paid
            self.vendor_invoice.update_payment_status()

    def __str__(self):
        return f"{self.payment_out_number} - {self.vendor_invoice.vendor.party_name}"