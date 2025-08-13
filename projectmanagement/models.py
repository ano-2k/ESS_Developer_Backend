from datetime import datetime,date
import mimetypes
from django.db import models
from authentication.models import User 
from authentication.models import Manager,Employee, Hr, Location
from ess import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone

class Project(models.Model):
    project_id = models.CharField(max_length=50, unique=True, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    deadline = models.DateField()
    project_manager=models.CharField(max_length=100)
    project_status=models.CharField(max_length=50,default='not_started')
    completion_date = models.DateTimeField(null=True, blank=True)# Date when the task is marked as completed
    completion_reason = models.TextField(null=True, blank=True)
    

    def __str__(self):
        return self.name

    def is_late(self):
        if self.completion_date:
            # Convert the deadline to a timezone-aware datetime
            deadline_datetime = timezone.make_aware(datetime.combine(self.deadline, datetime.min.time()))
            return self.completion_date > deadline_datetime
        return False 
    
    def save(self, *args, **kwargs):
        if not self.project_id:
            last_project = Project.objects.order_by('-id').first()
            if last_project and last_project.project_id:
                last_num = int(last_project.project_id.split('_')[1])
            else:
                last_num = 0
            self.project_id = f"PRO_{last_num + 1:03d}"
        super().save(*args, **kwargs)
    
    


class Task(models.Model):
    STATUS_CHOICES = [
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
        ('in review', 'In Review'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    task_id = models.CharField(max_length=50, unique=True, editable=False)
    task_name = models.CharField(max_length=100)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    start_date = models.DateField()
    deadline = models.DateField()
    project_name =models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not started')
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='tasks')
    completion_date = models.DateTimeField(null=True, blank=True)  # Date when the task is marked as completed
    completion_reason = models.TextField(null=True, blank=True)  # Reason for late completion

    def __str__(self):
        return self.task_name

    def is_late(self):
        """
        Check if the task was completed after its deadline.
        """
        if self.completion_date:
            # Convert deadline to timezone-aware datetime
            deadline_datetime = timezone.make_aware(datetime.combine(self.deadline, datetime.min.time()))
            return self.completion_date > deadline_datetime
        return False

    @staticmethod
    def calculate_manager_performance(manager):
        """
        Calculate the performance of a manager based on completed tasks.
        """
        total_tasks = Task.objects.filter(manager=manager).count()
        completed_tasks = Task.objects.filter(manager=manager, status='completed').count()
        if total_tasks > 0:
            return (completed_tasks / total_tasks) * 100
        return 0
    
    def save(self, *args, **kwargs):
        if not self.task_id:
            last_task = Task.objects.order_by('-id').first()
            if last_task and last_task.task_id:
                last_num = int(last_task.task_id.split('_')[1])
            else:
                last_num = 0
            self.task_id = f"TASK_{last_num + 1:03d}"
        super().save(*args, **kwargs)

   
    


class Role(models.Model):
    role_id = models.CharField(max_length=50, unique=True, editable=False)
    role_name = models.CharField(max_length=100)

    def __str__(self):
        return self.role_name

    def save(self, *args, **kwargs):
        if not self.role_id:
            last_role = Role.objects.order_by('-id').first()
            if last_role and last_role.role_id:
                last_num = int(last_role.role_id.split('_')[1])
            else:
                last_num = 0
            self.role_id = f"ROLE_{last_num + 1:03d}"
        super().save(*args, **kwargs)



class Team(models.Model):
    team_id = models.CharField(max_length=50, unique=True, editable=False)
    team_name = models.CharField(max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='teams')
    team_task = models.CharField(max_length=100)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='teams')
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leader_teams')
    members = models.ManyToManyField(User, related_name="team_members")

    def save(self, *args, **kwargs):
        if not self.team_id:
            last_team = Team.objects.order_by('-id').first()
            if last_team and last_team.team_id:
                last_num = int(last_team.team_id.split('_')[1])
            else:
                last_num = 0
            self.team_id = f"TEAM_{last_num + 1:03d}"
        super().save(*args, **kwargs)
    
# class employee_task(models.Model):
#     STATUS_CHOICES = [
#         ('not started', 'Not Started'),
#         ('in progress', 'In Progress'),
#         ('in review', 'In Review'),
#         ('completed', 'Completed'),  # Optional: Add a 'completed' status if needed
#     ]
#     manager = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True, blank=True)
#     team_name = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
#     project_name = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)
#     emptask_id = models.CharField(max_length=50, blank=True, null=True)  # Task ID
#     task_name = models.CharField(max_length=50)
#     task_description = models.CharField(max_length=100)
#     assigned_to = models.CharField(max_length=50)
#     deadline = models.DateField()
#     emp_taskstatus = models.CharField(max_length=100, choices=STATUS_CHOICES, default='not started')
#     completion_date = models.DateTimeField(null=True, blank=True)  # Date when the task is completed
#     completion_reason = models.TextField(null=True, blank=True)  # Reason for task delays
    


#     def __str__(self):
#         return self.task_name

#     def is_late(self):
#         if self.completion_date:
#             # Convert the deadline to a timezone-aware datetime
#             deadline_datetime = timezone.make_aware(datetime.combine(self.deadline, datetime.min.time()))
#             return self.completion_date > deadline_datetime
#         return False
    
    
#     @staticmethod
#     def calculate_employee_performance(employee_name):
#         total_tasks = employee_task.objects.filter(assigned_to=employee_name).count()
#         completed_tasks = employee_task.objects.filter(assigned_to=employee_name, emp_taskstatus='completed').count()
#         if total_tasks > 0:
#             return (completed_tasks / total_tasks) * 100
#         return 0

class employee_task(models.Model):

    STATUS_CHOICES = [
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
        ('in review', 'In Review'),
        ('completed', 'Completed'),
    ]


    team_id=models.ForeignKey(Team, on_delete=models.CASCADE,null=True)
    emptask_id = models.CharField(max_length=50, unique=True, editable=False)
    task_name=models.CharField(max_length=50)
    task_description=models.CharField(max_length=100)
    assigned_to=models.CharField(max_length=50)
    deadline=models.DateField(max_length=50)
    team_name=models.CharField(max_length=50,null=True)
    team_project_name=models.CharField(max_length=50)
    emp_taskstatus=models.CharField(max_length=50, choices=STATUS_CHOICES, default='not started')
    completion_date = models.DateTimeField(null=True, blank=True) # Date when the task is marked as completed
    completion_reason = models.TextField(null=True, blank=True)  # Reason for late completion
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='emptask', null=True, blank=True)
    
    def is_late(self):
        if self.completion_date:
            # Convert the deadline to a timezone-aware datetime
            deadline_datetime = timezone.make_aware(datetime.combine(self.deadline, datetime.min.time()))
            return self.completion_date > deadline_datetime
        return False
    
    
    @staticmethod
    def calculate_employee_performance(employee_name):
        total_tasks = employee_task.objects.filter(assigned_to=employee_name).count()
        completed_tasks = employee_task.objects.filter(assigned_to=employee_name, emp_taskstatus='completed').count()
        if total_tasks > 0:
            return (completed_tasks / total_tasks) * 100
        return 0
    
    def save(self, *args, **kwargs):
        if not self.emptask_id:
            last_task = employee_task.objects.order_by('-id').first()
            if last_task and last_task.emptask_id:
                last_num = int(last_task.emptask_id.split('_')[1])
            else:
                last_num = 0
            self.emptask_id = f"EMPTASK_{last_num + 1:03d}"
        super().save(*args, **kwargs)


class TaskLog(models.Model):
    task=models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_logs', null=True, blank=True)
    employeetask=models.ForeignKey(employee_task, on_delete=models.CASCADE, related_name='task_logs', null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='task_logs', null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name='task_logs', null=True, blank=True)
    check_in_time = models.DateTimeField()
    check_out_time = models.DateTimeField(null=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def calculate_hours_worked(self):
        if self.check_in_time and self.check_out_time:
            delta = self.check_out_time - self.check_in_time
            # Calculate hours as a decimal (e.g., 1 hour 30 minutes = 1.5 hours)
            self.hours_worked = delta.total_seconds() / 3600
            self.save()


class TaskDocument(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.CharField(max_length=50)
    document = models.FileField(upload_to='task_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class TaskEmpDocument(models.Model):
    employee_task = models.ForeignKey(employee_task, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.CharField(max_length=50)
    document = models.FileField(upload_to='task_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
   
# training models
class TrainingProgram(models.Model):
    program_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    for_managers = models.BooleanField(default=False)  # True if this program is for managers
    for_employees = models.BooleanField(default=True)  # True if this program is for employees
    training_incharge = models.ForeignKey(Manager, on_delete=models.CASCADE)

    def _str_(self):
        return self.name

class TrainingParticipation(models.Model):
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True, blank=True)
    completion_status = models.CharField(max_length=20, choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='not_started')
    completion_date = models.DateField(null=True, blank=True)

    def _str_(self):
        return f"{self.program.name} - {self.employee or self.manager}"


class Certification(models.Model):
    participation = models.OneToOneField('TrainingParticipation', on_delete=models.CASCADE)
    certification_name = models.CharField(max_length=255)
    certification_date = models.DateField()
    certification_file = models.FileField(upload_to='certificates/')

    def _str_(self):
        return f"Certification for {self.participation.employee or self.participation.manager}"

    def send_certificate_email(self):
        email = EmailMessage(
            subject=f'Certification Received: {self.certification_name}',
            body=f'Dear {self.participation.employee.employee_name if self.participation.employee else self.participation.manager.manager_name},\n\n'
                 f'You have received the {self.certification_name} certification for completing the training program on {self.certification_date}.',
            from_email=settings.EMAIL_HOST_USER,
            to=[self.participation.employee.email if self.participation.employee else self.participation.manager.email],
        )
        
        # Attach the certification file
        content_type = mimetypes.guess_type(self.certification_file.name)[0] or 'application/octet-stream'
        email.attach(self.certification_file.name, self.certification_file.read(), content_type)
        email.send()
        
        


# New Models Created For Manpower Plannning 


class PositionRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('hr_review', 'HR Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    request_id = models.CharField(max_length=50, unique=True, editable=False)
    title = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='position_requests')
    experience_level = models.CharField(max_length=50)
    job_types = models.CharField(max_length=50)
    opening_roles = models.PositiveIntegerField()
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    requested_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='position_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    hr_reviewer = models.ForeignKey(Hr, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_position_requests')
    manager_approver = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_position_requests')
    approval_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.request_id:
            while True:
                last_request = PositionRequest.objects.order_by('-id').first()
                if last_request and last_request.request_id.startswith("REQ"):
                    last_number = int(last_request.request_id[3:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                request_id = f"REQ{new_number:03}"
                if not PositionRequest.objects.filter(request_id=request_id).exists():
                    self.request_id = request_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.request_id}"

class Vacancy(models.Model):
    vacancy_id = models.CharField(max_length=50, unique=True, editable=False)
    position_request = models.OneToOneField(PositionRequest, on_delete=models.CASCADE, related_name='vacancy')
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50)
    job_types = models.CharField(max_length=50)
    opening_roles = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')

    def __str__(self):
        return f"{self.title} - {self.vacancy_id}"

    def save(self, *args, **kwargs):
        if not self.vacancy_id:
            last_vacancy = Vacancy.objects.order_by('-id').first()
            if last_vacancy and last_vacancy.vacancy_id:
                last_num = int(last_vacancy.vacancy_id.split('_')[1])
            else:
                last_num = 0
            self.vacancy_id = f"VAC_{last_num + 1:03d}"
        super().save(*args, **kwargs)
	
 
 
#  from authentication.models import User this import not the default import mindit