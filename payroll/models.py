from pprint import isrecursive
from django.db import models
# payroll/models.py
from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from django.db.models import Sum
from authentication.models import User
class PayrollManagement(models.Model):
    user = models.CharField(max_length=20, default=None)
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(default=True, blank=True)
    base_salary = models.CharField(max_length=20)  # Keeping as CharField
    net_salary = models.CharField(max_length=20, default='0')  # Changed to CharField
    total_working_hours = models.CharField(max_length=20, default='0')  # New field for total hours
    overtime_hours = models.CharField(max_length=20, default='0')
    overtime_pay = models.CharField(max_length=30,default='0')
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_id', 'month')
        
class ManagerPayrollManagement(models.Model):
    user = models.CharField(max_length=20, default=None)
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(default=True, blank=True)
    base_salary = models.CharField(max_length=20)  # Keeping as CharField
    net_salary = models.CharField(max_length=20, default='0')  # Changed to CharField
    total_working_hours = models.CharField(max_length=20, default='0')  # New field for total hours
    overtime_hours = models.CharField(max_length=20, default='0')
    overtime_pay = models.CharField(max_length=30,default='0')
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_id', 'month')        # This enforces that the same user can have multiple payslips, one for each month# New field for overtime

class SupervisorPayrollManagement(models.Model):
    user = models.CharField(max_length=20, default=None)
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(default=True, blank=True)
    base_salary = models.CharField(max_length=20)  # Keeping as CharField
    net_salary = models.CharField(max_length=20, default='0')  # Changed to CharField
    total_working_hours = models.CharField(max_length=20, default='0')  # New field for total hours
    overtime_hours = models.CharField(max_length=20, default='0')
    overtime_pay = models.CharField(max_length=30,default='0')
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_id', 'month')        
        
class PayrollNotification(models.Model):
    user = models.CharField(max_length=40,default=None)
    user_id = models.CharField(max_length=30)
    date = models.DateField(default=True)
    time = models.TimeField()
    message = models.TextField(default=True)
           
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"   

class ManagerPayrollNotification(models.Model):
    user = models.CharField(max_length=40,default=None)
    user_id = models.CharField(max_length=30)
    date = models.DateField(default=True)
    time = models.TimeField()
    message = models.TextField(default=True)
           
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"  

class SupervisorPayrollNotification(models.Model):
    user = models.CharField(max_length=40,default=None)
    user_id = models.CharField(max_length=30)
    date = models.DateField(default=True)
    time = models.TimeField()
    message = models.TextField(default=True)
           
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}" 
    
from django.db import models
from django.utils.timezone import now

class Salary(models.Model):
    user_id = models.CharField(max_length=20)
    annual_salary = models.CharField(max_length=20)
    bonus = models.CharField(max_length=20)
    total_salary = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.CharField(max_length=20, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert CharField values to float for calculations
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0

        # Perform calculations
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12

        # Convert results back to strings for storage
        self.total_salary = f"{total_salary:.2f}"
        self.monthly_salary = f"{monthly_salary:.2f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user_id} - Monthly: {self.monthly_salary}"
    
class ManagerSalary(models.Model):
    user_id = models.CharField(max_length=20)
    annual_salary = models.CharField(max_length=20)
    bonus = models.CharField(max_length=20)
    total_salary = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.CharField(max_length=20, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert CharField values to float for calculations
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0

        # Perform calculations
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12

        # Convert results back to strings for storage
        self.total_salary = f"{total_salary:.2f}"
        self.monthly_salary = f"{monthly_salary:.2f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user_id} - Monthly: {self.monthly_salary}"    

class SupervisorSalary(models.Model):
    user_id = models.CharField(max_length=20)
    annual_salary = models.CharField(max_length=20)
    bonus = models.CharField(max_length=20)
    total_salary = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.CharField(max_length=20, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert CharField values to float for calculations
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0

        # Perform calculations
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12

        # Convert results back to strings for storage
        self.total_salary = f"{total_salary:.2f}"
        self.monthly_salary = f"{monthly_salary:.2f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user_id} - Monthly: {self.monthly_salary}" 
    
class BonusType(models.Model):
    user_id = models.CharField(max_length=20)
    bonus_type = models.CharField(max_length=100)
    amount = models.CharField(max_length=20)
    due_date = models.DateField(default=now)
    paid_status = models.CharField(max_length=20, blank=True, null=True)
    total_paid = models.CharField(max_length=20, blank=True, null=True)
                          

class HrPayrollManagement(models.Model):
    user = models.CharField(max_length=20, default=None)
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(default=True, blank=True)
    base_salary = models.CharField(max_length=20)  # Keeping as CharField
    net_salary = models.CharField(max_length=20, default='0')  # Changed to CharField
    total_working_hours = models.CharField(max_length=20, default='0')  # New field for total hours
    overtime_hours = models.CharField(max_length=20, default='0')
    overtime_pay = models.CharField(max_length=30,default='0')
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_id', 'month')                           

class HrPayrollNotification(models.Model):
    user = models.CharField(max_length=40,default=None)
    user_id = models.CharField(max_length=30)
    date = models.DateField(default=True)
    time = models.TimeField()
    message = models.TextField(default=True)
           
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"          
    
class HrSalary(models.Model):
    user_id = models.CharField(max_length=20)
    annual_salary = models.CharField(max_length=20)
    bonus = models.CharField(max_length=20)
    total_salary = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.CharField(max_length=20, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert CharField values to float for calculations
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0

        # Perform calculations
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12

        # Convert results back to strings for storage
        self.total_salary = f"{total_salary:.2f}"
        self.monthly_salary = f"{monthly_salary:.2f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user_id} - Monthly: {self.monthly_salary}"                              
    
class ArPayrollManagement(models.Model):
    user = models.CharField(max_length=20, default=None)
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(default=True, blank=True)
    base_salary = models.CharField(max_length=20)  # Keeping as CharField
    net_salary = models.CharField(max_length=20, default='0')  # Changed to CharField
    total_working_hours = models.CharField(max_length=20, default='0')  # New field for total hours
    overtime_hours = models.CharField(max_length=20, default='0')
    overtime_pay = models.CharField(max_length=30,default='0')
    pdf_path = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ('user_id', 'month')                           

class ArPayrollNotification(models.Model):
    user = models.CharField(max_length=40,default=None)
    user_id = models.CharField(max_length=30)
    date = models.DateField(default=True)
    time = models.TimeField()
    message = models.TextField(default=True)
           
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"          
    
class ArSalary(models.Model):
    user_id = models.CharField(max_length=20)
    annual_salary = models.CharField(max_length=20)
    bonus = models.CharField(max_length=20)
    total_salary = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.CharField(max_length=20, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        # Convert CharField values to float for calculations
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0

        # Perform calculations
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12

        # Convert results back to strings for storage
        self.total_salary = f"{total_salary:.2f}"
        self.monthly_salary = f"{monthly_salary:.2f}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user_id} - Monthly: {self.monthly_salary}"                                  
    
    
    
############################# NEW CHANGES AFTER USER MODEL AND CONCEPT IMPEMENTED ####################################   

class UserSalary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="salaries")
    annual_salary = models.DecimalField(max_digits=12, decimal_places=2)
    bonus = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField(default=now)
    updated_date = models.DateField(auto_now=True)

    def save(self, *args, **kwargs):
        annual_salary = float(self.annual_salary) if self.annual_salary else 0
        bonus = float(self.bonus) if self.bonus else 0
        total_salary = annual_salary + bonus
        monthly_salary = total_salary / 12
        self.total_salary = total_salary
        self.monthly_salary = monthly_salary
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Salary for {self.user.user_id} - Monthly: {self.monthly_salary}"
    
    
class UserPayrollManagement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payrolls")
    user_id = models.CharField(max_length=20)
    month = models.DateField()
    email = models.EmailField(blank=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_working_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pdf_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('user_id', 'month')

    def __str__(self):
        return f"Payroll for {self.user.user_name} - {self.month.strftime('%B %Y')}"
    


class UserPayrollNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payroll_notifications")
    date = models.DateField(default=now)
    time = models.TimeField(auto_now_add=True)
    message = models.TextField(default="")

    class Meta:
        ordering = ['-date', '-time']  # default ordering by latest

    def __str__(self):
        return f"Notification for {self.user.user_name} on {self.date} at {self.time}"