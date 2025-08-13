import random
from django.db import models
from cloudinary.models import CloudinaryField

from django.contrib.auth.hashers import make_password, check_password

class SuperAdmin(models.Model):
    username = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save(update_fields=['password'])

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

    
    
class Admin(models.Model):
    username = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100,unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)
    features = models.JSONField(default=list, blank=True)


    def __str__(self):
        return self.email
    
class ManagingDirector(models.Model):
    username = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=255)
    reset_token = models.CharField(max_length=255, null=True, blank=True)
    token_expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email

class Department(models.Model):
    department_id = models.CharField(max_length=50, unique=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class Shift(models.Model):
    shift_number = models.CharField(max_length=50, unique=True)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()

    def __str__(self):
        return self.shift_number
    
class Location(models.Model):
    location_id = models.CharField(max_length=50, unique=True)
    location_name = models.CharField(max_length=100)

    def __str__(self):
        return self.location_name


class Manager(models.Model):
    manager_id = models.CharField(max_length=50, unique=True, blank=True)  # Allow blank, will be auto-filled
    manager_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    # manager_image = CloudinaryField('image',folder='ess/', blank=True, null=True)
    manager_image = models.ImageField(upload_to='manager_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='manager')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward =models.IntegerField(default=0,blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE ,blank=True, null=True)
    streams = models.JSONField(null=True, blank=True)





    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.manager_id:  # Generate employee_id only if it's not already set
            last_manager = Manager.objects.order_by('-id').first()
            if last_manager and last_manager.manager_id.startswith("MAN"):
                last_number = int(last_manager.manager_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1  # If no employee exists, start with EMP001

            self.manager_id = f"MAN{new_number:03}"  # Generates EMP001, EMP002, etc.
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.manager_name 
    
class Hr(models.Model):
    hr_id = models.CharField(max_length=50, unique=True, blank=True)  # Allow blank, will be auto-filled
    hr_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    hr_image = models.ImageField(upload_to='hr_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='hr')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward =models.IntegerField(default=0,blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE ,blank=True, null=True)
    streams = models.JSONField(null=True, blank=True)


    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.hr_id:  # Generate hr_id only if it's not already set
            last_hr = Hr.objects.order_by('-id').first()
            if last_hr and last_hr.hr_id.startswith("HR"):
                last_number = int(last_hr.hr_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1  # If no hr exists, start with HR001

            self.hr_id = f"HR{new_number:03}"  # Generates HR001, EMP002, etc.
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.hr_name
    
        
    
class Employee(models.Model):
    employee_id = models.CharField(max_length=50, unique=True, blank=True)  # Allow blank, will be auto-filled
    employee_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    employee_image = models.ImageField(upload_to='employee_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='employee')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward =models.IntegerField(default=0,blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE ,blank=True, null=True)
    streams = models.JSONField(null=True, blank=True)


    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.employee_id:  # Generate employee_id only if it's not already set
            last_employee = Employee.objects.order_by('-id').first()
            if last_employee and last_employee.employee_id.startswith("EMP"):
                last_number = int(last_employee.employee_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1  # If no employee exists, start with EMP001

            self.employee_id = f"EMP{new_number:03}"  # Generates EMP001, EMP002, etc.
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.employee_name

    
class Supervisor(models.Model):
    supervisor_id = models.CharField(max_length=50, unique=True, blank=True)  # Allow blank, will be auto-filled
    supervisor_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    supervisor_image = models.ImageField(upload_to='supervisor_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='supervisor')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward =models.IntegerField(default=0,blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,blank=True, null=True)
    streams = models.JSONField(null=True, blank=True)


    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.supervisor_id:  # Generate employee_id only if it's not already set
            last_supervisor = Supervisor.objects.order_by('-id').first()
            if last_supervisor and last_supervisor.supervisor_id.startswith("SUP"):
                last_number = int(last_supervisor.supervisor_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1  # If no employee exists, start with EMP001

            self.supervisor_id = f"SUP{new_number:03}"  # Generates EMP001, EMP002, etc.
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.supervisor_name 
    


    
class Todo(models.Model):
    title=models.CharField(max_length=255)
    completed=models.BooleanField(default=False)
    created_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # Use TextField instead of CharField for larger content
    # date = models.DateField()  # Date when the news was created
    created_date = models.DateTimeField(auto_now_add=True)  # Automatically set on news creation

    def str(self):
        return self.title

#helpdesk 

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('In Progress', 'In Progress'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="created_tickets" , null=True)
    Reciver= models.TextField()
    assigned_to = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    proof = models.FileField(upload_to='ticket_proofs/', null=True, blank=True)

    def __str__(self):
        return self.title
    
class Req(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
    

class Requests(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.SET_NULL, null=True, blank=True)
    admin = models.ForeignKey('Admin', on_delete=models.SET_NULL, null=True, blank=True) 
    hr = models.ForeignKey('Hr', on_delete=models.SET_NULL, null=True, blank=True)# Add admin field
    title = models.CharField(max_length=255)
    request_ticket_id = models.CharField(max_length=4, unique=True, null=False)

    def save(self, *args, **kwargs):
        if not self.request_ticket_id:
            # Generate a random 4-digit unique ticket ID
            while True:
                ticket_id = f"{random.randint(1000, 9999)}"
                if not Requests.objects.filter(request_ticket_id=ticket_id).exists():
                    self.request_ticket_id = ticket_id
                    break
        super().save(*args, **kwargs)

    description = models.TextField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Forwarded', 'Forwarded'),
        ],
        default='Pending'
    )

    admin_status = models.CharField (
        max_length=50,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
        ],
        default='Pending'
    )

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.status}"

class Skill(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.CharField(max_length=20, choices=[
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced')
    ])

    def _str_(self):
        return f"{self.skill_name} ({self.proficiency_level}) - {self.employee.employee_name}" 


class Hiring(models.Model):
    project = models.ForeignKey("projectmanagement.Project", on_delete=models.CASCADE)  # ✅ Use a string reference
    no_requirement = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    skills = models.CharField(max_length=255)
    
    # ✅ Add Experience Field
    EXPERIENCE_CHOICES = [
        ("fresher", "Fresher"),
        ("1+", "1+ Years"),
        ("3+", "3+ Years"),
        ("5+", "5+ Years"),
        ("10+", "10+ Years"),
    ]
    experience = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, default="fresher")
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending") 
    created_date = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.project} - {self.title}" 
    


class Ar(models.Model):
    ar_id = models.CharField(max_length=50, unique=True, blank=True)  # Allow blank, will be auto-filled
    ar_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField()
    gender = models.CharField(max_length=10)
    ar_image = models.ImageField(upload_to='ar_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='ar')
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward =models.IntegerField(default=0,blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE,blank=True, null=True)


    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.ar_id:  # Generate employee_id only if it's not already set
            last_ar = Ar.objects.order_by('-id').first()
            if last_ar and last_ar.ar_id.startswith("AR"):
                last_number = int(last_ar.ar_id[3:])
                new_number = last_number + 1
            else:
                new_number = 1  # If no employee exists, start with EMP001

            self.ar_id = f"AR{new_number:03}"  # Generates EMP001, EMP002, etc.
        
        super().save(*args, **kwargs)

    def _str_(self):
        return self.ar_name
    

#Job Alert Hr Flow 
class JobAlert(models.Model):
    TYPE_CHOICES = [
        ("Full-time", "Full-time"),
        ("Contract", "Contract"),
        ("Internship-full-time", "Internship (Full-time)"),
        ("Internship-part-time", "Internship (Part-time)"),
    ]

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Paused", "Paused"),
        ("Closed", "Closed"),
    ]

    job_id = models.CharField(max_length=50, unique=True, editable=False)
    hr = models.ForeignKey('Hr', on_delete=models.CASCADE, related_name='job_alerts')
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)  # Increased max_length for longer values
    posted = models.DateField()
    applications = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if not self.job_id:
            last_job = JobAlert.objects.order_by('-id').first()
            if last_job and last_job.job_id:
                last_num = int(last_job.job_id.split('_')[1])
            else:
                last_num = 0
            self.job_id = f"JOB_{last_num + 1:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

from django.core.validators import FileExtensionValidator  
class Candidate(models.Model):
    STATUS_CHOICES = [
        ("Resume In Review", "Resume In Review"),
        ("Shortlisted", "Shortlisted" ),
        ("Interview - L1", "Interview - L1"),
        ("Interview - L2", "Interview - L2"),
        ("Interview - L3", "Interview - L3"),
        ("Welcome Letter", "Welcome Letter"),
        ("Document Collection", "Document Collection"),
        ("Offer Letter", "Offer Letter"),
        ("Onboarding", "Onboarding"),
    ]

    JOB_TITLE_CHOICES = [
        ("Frontend Developer", "Frontend Developer"),
        ("Backend Developer", "Backend Developer"),
        ("UI/UX Designer", "UI/UX Designer"),
    ]

    c_id = models.CharField(max_length=50, unique=True, editable=False)
    hr = models.ForeignKey('Hr', on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    jobTitle = models.CharField(max_length=50, choices=JOB_TITLE_CHOICES)
    resume = models.FileField(
        upload_to='resumes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def save(self, *args, **kwargs):
        if not self.c_id:
            last_candidate = Candidate.objects.order_by('-id').first()
            last_num = int(last_candidate.c_id.split('CAN')[1]) if last_candidate else 0
            self.c_id = f"CAN{last_num + 1:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name




######################## New User Model After the  change flow ###########################################

class User(models.Model):
    user_id = models.CharField(max_length=50, unique=True, blank=True)
    user_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=10)
    user_image = models.ImageField(upload_to='user_images/', null=True, blank=True)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    dob = models.DateField()
    hired_date = models.DateField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    designation = models.CharField(max_length=50, choices=[
        ('Employee', 'Employee'),
        ('Supervisor', 'Supervisor'),
        ('Human Resources', 'Human Resources')
    ])
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    linkedin_profile_link = models.URLField(null=True, blank=True)
    reset_token = models.CharField(max_length=64, blank=True, null=True)
    token_expiration = models.DateTimeField(blank=True, null=True)
    reward = models.IntegerField(default=0, blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    streams = models.JSONField(null=True, blank=True)

    @property
    def department_name(self):
        return self.department.department_name

    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = User.objects.order_by('-id').first()
            if last_user and last_user.user_id.startswith("USER"):
                last_number = int(last_user.user_id[4:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.user_id = f"USER{new_number:03}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_name