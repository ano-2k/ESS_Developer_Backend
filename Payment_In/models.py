from django.db import models
from django.utils import timezone
from Pincode.models import AddParty
from Sales_Invoice.models import SalesInvoice
from decimal import Decimal

class RecordPayment(models.Model):
    PAYMENT_MODES = [
        ("Cash", "Cash"),
        ("Bank Transfer", "Bank Transfer"),
        ("UPI", "UPI"),
        ("Cheque", "Cheque"),
        ("Other", "Other"),
    ]

    party = models.ForeignKey(AddParty, on_delete=models.CASCADE, related_name="payments")
    sales_invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    payment_date = models.DateField(default=timezone.localdate)
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODES, default="Cash")
    payment_in_number = models.CharField(max_length=20, unique=True, blank=True)  # Auto-generated
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if not self.payment_in_number:
            last_payment = RecordPayment.objects.order_by('-id').first()
            next_number = 1 if not last_payment else int(last_payment.payment_in_number.split('-')[1]) + 1
            self.payment_in_number = f"PAYIN-{next_number:05d}"

        super().save(*args, **kwargs)

        # 🔄 Update the SalesInvoice totals if this is a new payment or modified
        if self.sales_invoice:
            # ✅ Recalculate total paid amount
            total_paid = self.sales_invoice.payments.aggregate(
                total=models.Sum('payment_amount')
            )['total'] or Decimal("0.00")

            self.sales_invoice.total_paid_amount = total_paid
            self.sales_invoice.update_payment_status()

    def __str__(self):
        return f"Payment {self.payment_in_number} - {self.party.party_name}"
