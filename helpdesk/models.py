from django.db import models

from authentication.models import Hr, Supervisor, Admin, Manager,Employee
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


class AdministrativeTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('password_change', 'Password Change'),
        ('username_change', 'Username Change'),
        ('location_change', 'Location Change'),
        ('shift_change', 'Shift Change'),
        ('team_related', 'Team Related'),
        ('task_related', 'Task Related'),
        ('project_related', 'Project Related'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/administrative/', null=True, blank=True)
    raise_to = models.ForeignKey(Admin, on_delete=models.PROTECT, null=True, blank=False, related_name='admin_tickets')
    user_id = models.CharField(max_length=100 ,null=True, blank=True)  # Stores user_id from API
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE,null=True, blank=True, related_name='administrative_tickets')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor_administrative_tickets')
    hr = models.ForeignKey(Hr,on_delete=models.CASCADE, null=True, blank=True, related_name='hr_administrative_tickets')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_administrative_tickets')
    
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    replies = GenericRelation('TicketReply', related_query_name='administrative_tickets')
    
    
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = AdministrativeTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-ADM-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

class HRTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('leave_policy', 'Leave Policy'),
        ('leave_request_related', 'Leave Request Related'),
        ('login_issue', 'Login Issue'),
        ('salary_related', 'Salary Related'),
        ('attendance_related', 'Attendance Related'),
        ('training_conflicts', 'Training Conflicts'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/hr/', null=True, blank=True)
    raise_to = models.ForeignKey(Hr, on_delete=models.PROTECT, null=True, blank=False, related_name='hr_tickets')
    hr_id = models.CharField(max_length=100 ,null=True, blank=True)  # Stores hr_id from API
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE,null=True, blank=True, related_name='hr_related_tickets')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor_hr_tickets')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_hr_tickets')
    replies = GenericRelation('TicketReply', related_query_name='hr_tickets')
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = HRTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-HR-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

class SupervisorTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('reports_of_project', 'Reports of Project'),
        ('reports_of_tasks', 'Reports of Tasks'),
        ('team_conflicts', 'Team Conflicts'),
        ('communication_issue', 'Communication Issue'),
        ('performance_related', 'Performance Related'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/supervisor/', null=True, blank=True)
    raise_to = models.ForeignKey(Supervisor, on_delete=models.PROTECT, null=True, blank=False, related_name='supervisor_tickets')
    supervisor_id = models.CharField(max_length=100,null=True, blank=True) # Stores supervisor_id from API
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE,null=True, blank=True, related_name='supervisor_related_tickets')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_supervisor_tickets')
    replies = GenericRelation('TicketReply', related_query_name='supervisor_tickets')
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = SupervisorTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-SUP-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

class SystemTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('slow_network', 'Slow Network'),
        ('system_performance', 'System Performance'),
        ('cyber_hacks', 'Cyber Hacks'),
        ('data_loss', 'Data Loss'),
        ('software_issue', 'Software Compatibility Issues'),
        ('trouble_shoot', 'Trouble Shoot'),
        ('hardware_issue', 'Hardware Issue'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/system/', null=True, blank=True)
    raise_to = models.ForeignKey(Admin, on_delete=models.PROTECT, null=True, blank=False, related_name='system_tickets')  # Assuming system tickets go to IT HR
    user_id = models.CharField(max_length=100 ,null=True, blank=True)  # Stores user_id from API
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE,null=True, blank=True, related_name='system_related_tickets')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor_system_tickets')
    
    hr = models.ForeignKey(Hr,on_delete=models.CASCADE, null=True, blank=True, related_name='hr_system_tickets')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_system_tickets')
    
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = SystemTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-SYS-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

class OtherTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, blank=True)  # No predefined options
    attachment = models.FileField(upload_to='tickets/other/', null=True, blank=True)
    raise_to = models.ForeignKey(Admin, on_delete=models.PROTECT, null=True, blank=False, related_name='other_tickets')  # Assuming other tickets go to HR
    user_id = models.CharField(max_length=100 ,null=True, blank=True)  # Stores user_id from API
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE,null=True, blank=True, related_name='other_related_tickets')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='supervisor_other_tickets')
    hr = models.ForeignKey(Hr,on_delete=models.CASCADE, null=True, blank=True, related_name='hr_other_tickets')
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_other_tickets')
    replies = GenericRelation('TicketReply', related_query_name='other_tickets')
    
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = OtherTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-OTH-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"
    

class TicketReply(models.Model):
     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
     object_id = models.PositiveIntegerField()
     ticket = GenericForeignKey('content_type', 'object_id')
     reply_text = models.TextField()

     def __str__(self):
        return f"Reply to {self.ticket.ticket_id}"
    
    

class ManagerTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('task_late_submission', 'Task Late Submission'),
        ('project_materials', 'Project Materials'),
        ('team_conflicts', 'Team Conflicts'),
        ('risk_management', 'Risk Management'),
        ('project_deadline', 'Project Deadline'),
        ('project_plan', 'Project Plan'),
        ('resource_allocation', 'Resource Allocation'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/manager/', null=True, blank=True)
    raise_to = models.ForeignKey(Manager, on_delete=models.PROTECT, null=True, blank=False, related_name='manager_tickets')
    manager_id = models.CharField(max_length=100 ,null=True, blank=True) 
    employee = models.ForeignKey(Employee,on_delete=models.CASCADE, null=True, blank=True, related_name='employee_manager_tickets')
    
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    replies = GenericRelation('TicketReply', related_query_name='manager_tickets')
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = ManagerTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-MGR-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"
    
    
#--------------------------------rough model for employee need to be changee after the system and other implementation ----------
    
class EmployeeTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    service_type = models.CharField(max_length=100, choices=[
        ('task_late_submission', 'Task Late Submission'),
        ('project_materials', 'Project Materials'),
        ('team_conflicts', 'Team Conflicts'),
        ('risk_management', 'Risk Management'),
        ('project_deadline', 'Project Deadline'),
        ('project_plan', 'Project Plan'),
        ('resource_allocation', 'Resource Allocation'),
        ('others', 'Others'),
    ])
    attachment = models.FileField(upload_to='tickets/employee/', null=True, blank=True)
    raise_to = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True, blank=False, related_name='employee_tickets')
    employee_id = models.CharField(max_length=100 ,null=True, blank=True) 
    
    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')
    
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    replies = GenericRelation('TicketReply', related_query_name='employee_tickets')
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = EmployeeTicket.objects.order_by('-id').first()
            self.ticket_id = f'TKT-EMP-{last_ticket.id + 1 if last_ticket else 1}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"
    

################################################# New Changes Sep 8 ###############################################################################


from authentication.models import User

class UserTicket(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True, blank=True)
    subject = models.CharField(max_length=200)
    description = models.TextField()

    # Merge ALL service types from HR, Supervisor, and Employee tickets
    service_type = models.CharField(max_length=100, choices=[
        # HR service types
        ('leave_policy', 'Leave Policy'),
        ('leave_request_related', 'Leave Request Related'),
        ('login_issue', 'Login Issue'),
        ('salary_related', 'Salary Related'),
        ('attendance_related', 'Attendance Related'),
        ('training_conflicts', 'Training Conflicts'),

        # Supervisor service types
        ('reports_of_project', 'Reports of Project'),
        ('reports_of_tasks', 'Reports of Tasks'),
        ('team_conflicts', 'Team Conflicts'),
        ('communication_issue', 'Communication Issue'),
        ('performance_related', 'Performance Related'),

        # Employee service types
        ('task_late_submission', 'Task Late Submission'),
        ('project_materials', 'Project Materials'),
        ('risk_management', 'Risk Management'),
        ('project_deadline', 'Project Deadline'),
        ('project_plan', 'Project Plan'),
        ('resource_allocation', 'Resource Allocation'),

        # Common
        ('others', 'Others'),
    ])

    attachment = models.FileField(upload_to='tickets/user/', null=True, blank=True)

    # Unified user relations
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets_created')
    raise_to = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='tickets_received')

    status = models.CharField(max_length=20, choices=[
        ('Request', 'Request'),
        ('Review', 'Review'),
        ('Approved', 'Approved'),
    ], default='Request')

    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    replies = GenericRelation('TicketReply', related_query_name='user_tickets')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = UserTicket.objects.order_by('-id').first()
            self.ticket_id = f"TKT-USER-{last_ticket.id + 1 if last_ticket else 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"