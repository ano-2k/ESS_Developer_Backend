from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth import get_user_model
from Pincode.models import AddParty
from Create_New_Item.models import ProductItem, ServiceItem, GSTTax


class ClientPurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ("received", "Received"),
        ("converted", "Converted into Sales Order"),
    ]

    customer = models.ForeignKey(
        AddParty,
        on_delete=models.CASCADE,
        limit_choices_to={'party_type': 'customer'},
        related_name="client_purchase_orders"
    )
    po_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    po_date = models.DateField(default=timezone.localdate)
    delivery_date = models.DateField(blank=True, null=True)
    sales_person = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_mobile_number = models.CharField(max_length=15, blank=True)
    shipping_address = models.TextField(blank=True, null=True)

    # payment_terms = models.CharField(max_length=5, choices=[
    #     ("0", "Due on Receipt"),
    #     ("15", "Net 15"),
    #     ("30", "Net 30"),
    #     ("45", "Net 45"),
    #     ("60", "Net 60"),
    # ], default="30", blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)
    po_file_upload = models.FileField(upload_to='client_purchase_orders/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="received")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.po_number:
            last_po = ClientPurchaseOrder.objects.exclude(po_number__isnull=True).exclude(po_number='').order_by('-id').first()
            next_number = 1
            if last_po and last_po.po_number and '-' in last_po.po_number:
                try:
                    next_number = int(last_po.po_number.split('-')[1]) + 1
                except ValueError:
                    pass
            self.po_number = f"CPO-{next_number:05d}"

        if self.customer:
            self.customer_name = self.customer.party_name
            self.customer_mobile_number = self.customer.mobile_number
            try:
                shipping_address = self.customer.shipping_address
                self.shipping_address = f"{shipping_address.street}, {shipping_address.city}, {shipping_address.state}, {shipping_address.pincode}"
            except Exception:
                self.shipping_address = "No Shipping Address"

        super().save(*args, **kwargs)

    def update_totals(self):
        items = self.items.all()
        subtotal = sum(item.total_before_tax for item in items)
        tax_total = sum(item.tax_amount for item in items)
        total = subtotal + tax_total

        # Ensure the total amount object exists and update it
        total_obj, created = ClientPurchaseOrderTotalAmount.objects.get_or_create(
            purchase_order=self,
            defaults={
                'total_before_tax': subtotal,
                'total_tax': tax_total,
                'total': total
            }
        )
        if not created:
            total_obj.total_before_tax = subtotal
            total_obj.total_tax = tax_total
            total_obj.total = total
            total_obj.save()

    def __str__(self):
        return f"{self.po_number} - {self.customer_name}"


class ClientPurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(ClientPurchaseOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey(ServiceItem, on_delete=models.SET_NULL, null=True, blank=True)

    item_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    gst = models.ForeignKey(GSTTax, on_delete=models.SET_NULL, null=True, blank=True)

    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_after_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if self.product:
            self.item_name = self.product.item_name
            self.rate = self.product.sales_price_without_tax or self.product.sales_price_with_tax
            if not self.gst and self.product.gst_tax:
                self.gst = self.product.gst_tax
        elif self.service:
            self.item_name = self.service.service_name
            self.rate = self.service.sales_price_without_tax or self.service.sales_price_with_tax
            if not self.gst and self.service.gst_tax_rate:
                self.gst = GSTTax.objects.filter(gst_rate=self.service.gst_tax_rate).first()

        self.total_before_tax = (self.quantity * self.rate) - self.discount
        gst_rate = self.gst.gst_rate if self.gst else Decimal('0.00')
        self.tax_amount = (self.total_before_tax * gst_rate) / Decimal('100.00')
        self.total_after_tax = self.total_before_tax + self.tax_amount

        super().save(*args, **kwargs)
        self.purchase_order.update_totals()

    def __str__(self):
        return f"{self.item_name} - Qty: {self.quantity}"


class ClientPurchaseOrderTotalAmount(models.Model):
    purchase_order = models.OneToOneField(ClientPurchaseOrder, on_delete=models.CASCADE, related_name="total_amount")
    total_before_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.purchase_order.po_number} - ₹{self.total}"
