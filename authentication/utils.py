import secrets
import datetime
from django.utils import timezone
from .models import Admin, Ar, Manager, Employee, ManagingDirector, Supervisor,Hr

def generate_reset_token_for_hr(email):
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Set the token expiration time (1 hour from now)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    # Update the Hr object with the reset token and expiration time
    try:
        hr = Hr.objects.get(email=email)
        hr.reset_token = token
        hr.token_expiration = expiration
        hr.save()
    except Hr.DoesNotExist:
        return None
    
    return token

def validate_reset_token_for_hr(token):
    try:
        # Find the user by token and check if it's still valid
        hr = Hr.objects.get(reset_token=token)
        if hr.token_expiration and hr.token_expiration > timezone.now():
            return True
        return False
    except Hr.DoesNotExist:
        return False

def get_email_from_token_for_hr(token):
    try:
        # Find the user by token
        hr = Hr.objects.get(reset_token=token)
        return hr.email
    except Hr.DoesNotExist:
        return None


def generate_reset_token_for_ar(email):
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Set the token expiration time (1 hour from now)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    # Update the Hr object with the reset token and expiration time
    try:
        ar = Ar.objects.get(email=email)
        ar.reset_token = token
        ar.token_expiration = expiration
        ar.save()
    except Ar.DoesNotExist:
        return None
    
    return token

def validate_reset_token_for_ar(token):
    try:
        # Find the user by token and check if it's still valid
        ar = Ar.objects.get(reset_token=token)
        if ar.token_expiration and ar.token_expiration > timezone.now():
            return True
        return False
    except Ar.DoesNotExist:
        return False

def get_email_from_token_for_ar(token):
    try:
        # Find the user by token
        ar = Ar.objects.get(reset_token=token)
        return ar.email
    except Ar.DoesNotExist:
        return None

def generate_reset_token(email):
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    # Set the token expiration time (1 hour from now)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    # Update the Admin object with the reset token and expiration time
    try:
        user = Admin.objects.get(email=email)
        user.reset_token = token
        user.token_expiration = expiration
        user.save()
    except Admin.DoesNotExist:
        return None
    
    return token

def validate_reset_token(token):
    try:
        # Find the user by token and check if it's still valid
        user = Admin.objects.get(reset_token=token)
        if user.token_expiration and user.token_expiration > timezone.now():
            return True
        return False
    except Admin.DoesNotExist:
        return False

def get_email_from_token(token):
    try:
        # Find the user by token
        user = Admin.objects.get(reset_token=token)
        return user.email
    except Admin.DoesNotExist:
        return None
    
def generate_reset_token_for_manager(email):
    token = secrets.token_urlsafe(32)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    try:
        manager = Manager.objects.get(email=email)
        manager.reset_token = token
        manager.token_expiration = expiration
        manager.save()
        return token
    except Manager.DoesNotExist:
        return None

# Validate reset token for manager
def validate_reset_token_for_manager(token):
    try:
        manager = Manager.objects.get(reset_token=token)
        if manager.token_expiration and manager.token_expiration > timezone.now():
            return True
        return False
    except Manager.DoesNotExist:
        return False

# Get email from reset token for manager
def get_email_from_token_for_manager(token):
    try:
        manager = Manager.objects.get(reset_token=token)
        return manager.email
    except Manager.DoesNotExist:
        return None

def generate_reset_token_for_supervisor(email):
    token = secrets.token_urlsafe(32)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    try:
        supervisor = Supervisor.objects.get(email=email)
        supervisor.reset_token = token
        supervisor.token_expiration = expiration
        supervisor.save()
        return token
    except Supervisor.DoesNotExist:
        return None

# Validate reset token for supervisor
def validate_reset_token_for_supervisor(token):
    try:
        supervisor = Supervisor.objects.get(reset_token=token)
        if supervisor.token_expiration and supervisor.token_expiration > timezone.now():
            return True
        return False
    except Supervisor.DoesNotExist:
        return False

# Get email from reset token for supervisor
def get_email_from_token_for_supervisor(token):
    try:
        supervisor = Supervisor.objects.get(reset_token=token)
        return supervisor.email
    except Supervisor.DoesNotExist:
        return None    

# Generate reset token for employee
def generate_reset_token_for_employee(email):
    token = secrets.token_urlsafe(32)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    try:
        employee = Employee.objects.get(email=email)
        employee.reset_token = token
        employee.token_expiration = expiration
        employee.save()
        return token
    except Employee.DoesNotExist:
        return None

# Validate reset token for employee
def validate_reset_token_for_employee(token):
    try:
        employee = Employee.objects.get(reset_token=token)
        if employee.token_expiration and employee.token_expiration > timezone.now():
            return True
        return False
    except Employee.DoesNotExist:
        return False

# Get email from reset token for employee
def get_email_from_token_for_employee(token):
    try:
        employee = Employee.objects.get(reset_token=token)
        return employee.email
    except Employee.DoesNotExist:
        return None
    
# Generate reset token for md
def generate_reset_token_for_md(email):
    token = secrets.token_urlsafe(32)
    expiration = timezone.now() + datetime.timedelta(hours=1)
    
    try:
        md = ManagingDirector.objects.get(email=email)
        md.reset_token = token
        md.token_expiration = expiration
        md.save()
        return token
    except ManagingDirector.DoesNotExist:
        return None

# Validate reset token for md
def validate_reset_token_for_md(token):
    try:
        md = ManagingDirector.objects.get(reset_token=token)
        if md.token_expiration and md.token_expiration > timezone.now():
            return True
        return False
    except ManagingDirector.DoesNotExist:
        return False

# Get email from reset token for md
def get_email_from_token_for_md(token):
    try:
        md = ManagingDirector.objects.get(reset_token=token)
        return md.email
    except ManagingDirector.DoesNotExist:
        return None
  
  
############################################# September 08 ##################################################  
import secrets
from django.utils import timezone
from datetime import timedelta
from .models import User


# 1. Generate reset token for User
def generate_reset_token_for_user(email):
    token = secrets.token_urlsafe(32)
    expiration = timezone.now() + timedelta(hours=1)

    try:
        user = User.objects.get(email=email)
        user.reset_token = token
        user.token_expiration = expiration
        user.save()
        return token
    except User.DoesNotExist:
        return None


# 2. Validate reset token for User
def validate_reset_token_for_user(token):
    try:
        user = User.objects.get(reset_token=token)
        if user.token_expiration and user.token_expiration > timezone.now():
            return True
        return False
    except User.DoesNotExist:
        return False


# 3. Get email from reset token for User
def get_email_from_token_for_user(token):
    try:
        user = User.objects.get(reset_token=token)
        return user.email
    except User.DoesNotExist:
        return None