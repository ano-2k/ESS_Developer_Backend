from django.db import models
from Pincode.models import AddParty
from Create_New_Item.models import *
from Sales_Person.models import *
from ClientPurchaseOrder.models import *
from django.utils import timezone
from datetime import date


class ClientSalesOrder(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("sent", "Sent"),
        ("converted", "Converted to Invoice"),
    ]

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="created")
    # purchase_order = models.OneToOneField(ClientPurchaseOrder, on_delete=models.CASCADE, related_name="sales_order")
    customer = models.ForeignKey(AddParty, on_delete=models.CASCADE, limit_choices_to={'party_type': 'customer'})
    sales_person = models.ForeignKey(SalesPerson, on_delete=models.SET_NULL, null=True, blank=True)
    so_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    po_number = models.CharField(max_length=30, unique=True, blank=True, null=True)
    so_date = models.DateField(default=timezone.localdate)
    delivery_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_total_amount(self):
        total = sum(item.total_amount or 0 for item in self.items.all())
        ClientSalesOrderTotalAmount.objects.update_or_create(
            sales_order=self,
            defaults={"total": total}
        )

    def save(self, *args, **kwargs):
        if not self.so_number:
            last_so = ClientSalesOrder.objects.exclude(so_number__isnull=True).exclude(so_number='').aggregate(last=models.Max("so_number"))
            self.so_number = self.generate_number(last_so["last"], prefix="SO")

        if not self.po_number:
            last_po = ClientSalesOrder.objects.exclude(po_number__isnull=True).exclude(po_number='').aggregate(last=models.Max("po_number"))
            self.po_number = self.generate_number(last_po["last"], prefix="PO")

        super().save(*args, **kwargs)

    def generate_number(self, last_number, prefix):
        """
        Generate new number like SO-0001 or PO-0001.
        """
        if last_number:
            try:
                last_int = int(last_number.split("-")[1])
                return f"{prefix}-{last_int + 1:04d}"
            except:
                return f"{prefix}-0001"
        else:
            return f"{prefix}-0001"

    def __str__(self):
        return f"Sales Order {self.so_number} for PO {self.po_number}"



class ClientSalesOrderItem(models.Model):
    sales_order = models.ForeignKey(ClientSalesOrder, on_delete=models.CASCADE, related_name="items")
    product_item = models.ForeignKey(ProductItem, on_delete=models.SET_NULL, null=True, blank=True)
    service_item = models.ForeignKey(ServiceItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    hsn_sac_code = models.CharField(max_length=20, blank=True, null=True)
    measuring_unit = models.CharField(max_length=10, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.ForeignKey(GSTTax, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.product_item:
            self.item_name = self.product_item.item_name
            self.description = self.product_item.description
            self.hsn_sac_code = self.product_item.hsn_code
            self.measuring_unit = self.product_item.measuring_unit

            self.price_per_item = (
                self.product_item.sales_price_without_tax
                or self.product_item.sales_price_with_tax
            )

            if not self.tax and self.product_item.gst_tax:
                self.tax = self.product_item.gst_tax

        elif self.service_item:
            self.item_name = self.service_item.service_name
            self.description = self.service_item.service_description
            self.hsn_sac_code = self.service_item.sac_code
            self.measuring_unit = self.service_item.measuring_unit

            self.price_per_item = (
                self.service_item.sales_price_without_tax
                or self.service_item.sales_price_with_tax
            )

            if not self.tax and self.service_item.gst_tax_rate and self.service_item.gst_tax_rate != "exempted":
                try:
                    self.tax = GSTTax.objects.get(gst_rate=self.service_item.gst_tax_rate)
                except GSTTax.DoesNotExist:
                    self.tax = None

        if self.price_per_item and self.quantity:
            subtotal = self.quantity * self.price_per_item
            self.total_amount = subtotal - self.discount

        super().save(*args, **kwargs)

        # ✅ Trigger total update after saving item
        if self.sales_order:
            self.sales_order.update_total_amount()

    def __str__(self):
        return self.item_name


class ClientSalesOrderTotalAmount(models.Model):
    sales_order = models.OneToOneField(ClientSalesOrder, on_delete=models.CASCADE, related_name="total_amount")
    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Total for {self.sales_order.so_number}: {self.total}"

class ClientSalesOrderEmailLog(models.Model):
    sales_order = models.ForeignKey(ClientSalesOrder, on_delete=models.CASCADE, related_name="email_logs")
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[("sent", "Sent"), ("failed", "Failed")],
        default="sent"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Email to {self.email} - {self.sales_order.so_number}"