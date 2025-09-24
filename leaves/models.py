from django.db import models
from datetime import timedelta

from authentication.models import Ar, Employee, Hr, Manager,User



class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    leave_proof = models.FileField(upload_to='media/leave_proof/',blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name='leave_requests')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')# Adjust as per your user model
    email = models.EmailField()
    notification_sent = models.BooleanField(default=False)
    calendar_link = models.URLField(blank=True, null=True)
    is_auto_leave = models.BooleanField(default=False, help_text="Indicates if the leave was auto-applied due to no check-in.")#added_tosay
   # Add this line for storing total days

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
        sundays = sum(
            1 for i in range(total_days)
            if (self.start_date + timedelta(days=i)).weekday() == 6
        )
        return total_days - sundays

    
class Notification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
    
class ApplyNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
        

class LeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='leave_balance')  # ✅ Corrected
    medical_leave = models.PositiveIntegerField(default=0)
    vacation_leave = models.PositiveIntegerField(default=0)
    personal_leave = models.PositiveIntegerField(default=0)
    total_leave_days = models.PositiveIntegerField(default=0)
    total_absent_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    def recalculate_total_leave_days(self):
        self.total_leave_days = (
            self.medical_leave + self.vacation_leave + self.personal_leave
        )
        self.save()


class ManagerLeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user =models.CharField(max_length=20,default=None)
    user_id =models.CharField(max_length=20)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=30, null=False)    
    manager_notification_sent = models.BooleanField(default=False)  # New field for notification status
    is_auto_leave = models.BooleanField(default=False, help_text="Indicates if the leave was auto-applied due to no check-in.")
    
    def __str__(self):
        return f"{self.user} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
    # Count the number of Sundays in the leave period
        sundays = sum(1 for i in range(total_days) if (self.start_date + timedelta(days=i)).weekday() == 6)
        return total_days - sundays
# Model for leave requests
    
class ManagerNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
    
class ManagerApplyNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"    

from authentication.models import Supervisor 

# Optional: Model to track leave balance (if required)
class ManagerLeaveBalance(models.Model):
    user = models.CharField(max_length=20, unique=True)
    medical_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    vacation_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    personal_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_leave_days = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_absent_days = models.PositiveIntegerField(default=0)  # Total absent days

    def __str__(self):
        return f"{self.user} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    # Add method to update total absent days
    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    # Method to recalculate total leave days
    def recalculate_total_leave_days(self):
        self.total_leave_days = self.medical_leave + self.vacation_leave + self.personal_leave
        self.save()



class SupervisorLeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name='supervisor_leave_requests')
    email = models.EmailField(max_length=30, null=False)    
    supervisor_notification_sent = models.BooleanField(default=False)  # New field for notification status
    is_auto_leave = models.BooleanField(default=False, help_text="Indicates if the leave was auto-applied due to no check-in.")#added_tosay
		 

    def __str__(self):
        return f"{self.user} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
    # Count the number of Sundays in the leave period
        sundays = sum(1 for i in range(total_days) if (self.start_date + timedelta(days=i)).weekday() == 6)
        return total_days - sundays
# Model for leave requests
    
    
class SupervisorNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
    
class SupervisorApplyNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"     

# Optional: Model to track leave balance (if required)
class SupervisorLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_leave_balance')  # ✅ Corrected
    medical_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    vacation_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    personal_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_leave_days = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_absent_days = models.PositiveIntegerField(default=0)  # Total absent days

    def __str__(self):
        return f"{self.user} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    # Add method to update total absent days
    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    # Method to recalculate total leave days
    def recalculate_total_leave_days(self):
        self.total_leave_days = self.medical_leave + self.vacation_leave + self.personal_leave
        self.save()


class HrLeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True, null=True, related_name='hr_leave_requests')
    email = models.EmailField(max_length=30, null=False)    
    manager_notification_sent = models.BooleanField(default=False)  # New field for notification status
    is_auto_leave = models.BooleanField(default=False, help_text="Indicates if the leave was auto-applied due to no check-in.")
    
    def __str__(self):
        return f"{self.user} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
    # Count the number of Sundays in the leave period
        sundays = sum(1 for i in range(total_days) if (self.start_date + timedelta(days=i)).weekday() == 6)
        return total_days - sundays
# Model for leave requests
    
class HrNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
    
class HrApplyNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"    

from authentication.models import Supervisor 

# Optional: Model to track leave balance (if required)
class HrLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hr_leave_balance')  # ✅ Corrected
    medical_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    vacation_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    personal_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_leave_days = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_absent_days = models.PositiveIntegerField(default=0)  # Total absent days

    def __str__(self):
        return f"{self.user} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    # Add method to update total absent days
    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    # Method to recalculate total leave days
    def recalculate_total_leave_days(self):
        self.total_leave_days = self.medical_leave + self.vacation_leave + self.personal_leave
        self.save()
        
class ArLeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user =models.CharField(max_length=20,default=None)
    user_id =models.CharField(max_length=20)
    ar = models.ForeignKey(Ar, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=30, null=False)    
    manager_notification_sent = models.BooleanField(default=False)  # New field for notification status
    
    def __str__(self):
        return f"{self.user} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
    # Count the number of Sundays in the leave period
        sundays = sum(1 for i in range(total_days) if (self.start_date + timedelta(days=i)).weekday() == 6)
        return total_days - sundays
# Model for leave requests
    
class ArNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"
    
class ArApplyNotification(models.Model):
    user = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)
    
    
    def __str__(self):
        return f"Notification for {self.user} on {self.date} at {self.time}"    

from authentication.models import Supervisor 

# Optional: Model to track leave balance (if required)
class ArLeaveBalance(models.Model):
    user = models.CharField(max_length=20, unique=True)
    medical_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    vacation_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    personal_leave = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_leave_days = models.PositiveIntegerField(default=0)  # Remaining leave balance
    total_absent_days = models.PositiveIntegerField(default=0)  # Total absent days

    def __str__(self):
        return f"{self.user} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    # Add method to update total absent days
    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    # Method to recalculate total leave days
    def recalculate_total_leave_days(self):
        self.total_leave_days = self.medical_leave + self.vacation_leave + self.personal_leave
        self.save()        
        
################################  For Supervisor   ################################
class LateloginReason(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    leave_request = models.ForeignKey(SupervisorLeaveRequest, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    supervisor_name = models.CharField(max_length=100, blank=True)  # New field to store supervisor name

    def __str__(self):
        return f"Late login reason for {self.supervisor_name} on {self.date}"

    def save(self, *args, **kwargs):
        # Automatically populate supervisor_name from the related Supervisor model
        if self.supervisor and not self.supervisor_name:
            self.supervisor_name = self.supervisor.supervisor_name
        super().save(*args, **kwargs)
        


################################july7################################
class HrLateLoginReason(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    hr = models.ForeignKey(Hr, on_delete=models.CASCADE)
    leave_request = models.ForeignKey(HrLeaveRequest, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    hr_name = models.CharField(max_length=100, blank=True)  # Field to store HR's name

    def __str__(self):
        return f"Late login reason for {self.hr_name} on {self.date}"

    def save(self, *args, **kwargs):
        # Automatically populate hr_name from the related Hr model
        if self.hr and not self.hr_name:
            self.hr_name = self.hr.hr_name
        super().save(*args, **kwargs)



class ManagerLateLoginReason(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    leave_request = models.ForeignKey(ManagerLeaveRequest, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    manager_name = models.CharField(max_length=100, blank=True)  # Field to store manager's name

    def __str__(self):
        return f"Late login reason for {self.manager_name} on {self.date}"

    def save(self, *args, **kwargs):
        # Automatically populate manager_name from the related Manager model
        if self.manager and not self.manager_name:
            self.manager_name = self.manager.manager_name
        super().save(*args, **kwargs)


class EmployeeLateLoginReason(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_request = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE)
    date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    employee_name = models.CharField(max_length=100, blank=True)  # New field to store employee name

    def _str_(self):
        return f"Late login reason for {self.employee_name} on {self.date}"

    def save(self, *args, **kwargs):
        # Automatically populate employee_name from the related Employee model
        if self.employee and not self.employee_name:
            self.employee_name = self.employee.employee_name
        super().save(*args, **kwargs)


############################################################# New Changes #############################################################
class UserLeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('medical', 'Medical'),
        ('vacation', 'Vacation'),
        ('personal', 'Personal'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    reason = models.TextField()
    leave_proof = models.FileField(upload_to='media/leave_proof/', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='user_leave_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    email = models.EmailField()
    notification_sent = models.BooleanField(default=False)
    calendar_link = models.URLField(blank=True, null=True)
    is_auto_leave = models.BooleanField(default=False, help_text="Indicates if the leave was auto-applied due to no check-in.")

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} from {self.start_date} to {self.end_date}"

    @property
    def total_days(self):
        total_days = (self.end_date - self.start_date).days + 1
        sundays = sum(
            1 for i in range(total_days)
            if (self.start_date + timedelta(days=i)).weekday() == 6
        )
        return total_days - sundays
    
    
class UserLateLoginReason(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_late_login_reasons')
    leave_request = models.ForeignKey(UserLeaveRequest, on_delete=models.SET_NULL, blank=True, null=True, related_name='user_late_login_reasons')
    date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Late login - {self.user.username} on {self.date}"


class UserLeaveBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_leave_balance')
    medical_leave = models.PositiveIntegerField(default=0)
    vacation_leave = models.PositiveIntegerField(default=0)
    personal_leave = models.PositiveIntegerField(default=0)
    total_leave_days = models.PositiveIntegerField(default=0)
    total_absent_days = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.user_name} - Balance: {self.total_leave_days} days, Absent: {self.total_absent_days} days"

    def update_total_absent_days(self, days):
        self.total_absent_days += days
        self.save()

    def recalculate_total_leave_days(self):
        self.total_leave_days = (
            self.medical_leave + self.vacation_leave + self.personal_leave
        )
        self.save()
        

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)

    def __str__(self):
        return f"Notification for {self.user.user_name} on {self.date} at {self.time}"


class UserApplyNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="apply_notifications")
    date = models.DateField()
    time = models.TimeField()
    message = models.TextField(max_length=300)

    def __str__(self):
        return f"Apply Notification for {self.user.user_name} on {self.date} at {self.time}"