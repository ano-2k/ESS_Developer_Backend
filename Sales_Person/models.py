from django.db import models

from authentication.models import Employee

# Create your models here.
# class SalesPerson(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=15)
#     employee_code = models.CharField(max_length=50, unique=True)
#     date_joined = models.DateField(auto_now_add=True)
#     region = models.CharField(max_length=100, blank=True, null=True)
#     target = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
#     commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
#     total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
#     deals_closed = models.PositiveIntegerField(default=0)
#     clients_handled = models.PositiveIntegerField(default=0)
#     is_active = models.BooleanField(default=True)
#     profile_picture = models.ImageField(upload_to="sales_profiles/", null=True, blank=True)
#     notes = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.name

class SalesPerson(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name="salesperson_profile")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    employee_code = models.CharField(max_length=50, unique=True)
    date_joined = models.DateField(auto_now_add=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    target = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deals_closed = models.PositiveIntegerField(default=0)
    clients_handled = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to="sales_profiles/", null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.employee.employee_name if self.employee else "No Employee"
