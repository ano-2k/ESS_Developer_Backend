from django.http import HttpRequest
# from calendar import monthrange
# import datetime
# from mailbox import Message
from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from attendance.views import calculate_total_present_days
# from attendance.models import PermissionHour
# from attendance.views import calculate_total_present_days
from authentication.utils import generate_reset_token, generate_reset_token_for_ar, generate_reset_token_for_employee, generate_reset_token_for_hr, generate_reset_token_for_manager, generate_reset_token_for_md, generate_reset_token_for_supervisor, get_email_from_token, get_email_from_token_for_ar, get_email_from_token_for_employee, get_email_from_token_for_hr, get_email_from_token_for_manager, get_email_from_token_for_md, get_email_from_token_for_supervisor, validate_reset_token, validate_reset_token_for_ar, validate_reset_token_for_employee, validate_reset_token_for_hr, validate_reset_token_for_manager, validate_reset_token_for_md, validate_reset_token_for_supervisor
from chat.models import Message
from leaves.models import ArLeaveRequest, HrLeaveRequest, LeaveBalance, ManagerLeaveRequest, SupervisorLeaveRequest,ManagerLeaveBalance,HrLeaveBalance,SupervisorLeaveBalance
from leaves.serializers import LeaveBalanceSerializer,HrLeaveBalanceSerializer,SupervisorLeaveBalanceSerializer

# from projectmanagement.models import Project, Role, Task, Team
from .models import Admin, Ar, Hr,Manager, Employee, ManagingDirector, Supervisor,SuperAdmin
# from attendance.models import Attendance, ResetRequest
from django.contrib.auth import authenticate, login
# from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password

# from .utils import generate_reset_token, generate_reset_token_for_md, get_email_from_token_for_md, validate_reset_token, get_email_from_token, generate_reset_token_for_manager, validate_reset_token_for_manager, get_email_from_token_for_manager, generate_reset_token_for_employee, validate_reset_token_for_employee, get_email_from_token_for_employee, validate_reset_token_for_md 
# # from .forms import LoginForm
# from datetime import datetime, timedelta
# from django.utils.dateparse import parse_date
# from django.utils import timezone
# from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
import bcrypt

def index(request):
    return render(request, 'authentication/index.html')

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manager, Employee, Admin, ManagingDirector,SuperAdmin
from .serializers import ArSerializer, HrSerializer, LoginSerializer, SupervisorSerializer  # Import your serializer
import bcrypt
from authentication.serializers import AdminSerializer, ManagingDirectorSerializer, ManagerSerializer, EmployeeSerializer, SupervisorSerializer,SuperAdminSerializer

@api_view(['GET'])
def view_manager_by_id(request, id):
    try:
        # Attempt to get the Manager instance by ID
        manager = Manager.objects.get(manager_id=id)
    except Manager.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = ManagerSerializer(manager)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_supervisor_by_id(request, id):
    try:
        # Attempt to get the Manager instance by ID
        supervisor = Supervisor.objects.get(supervisor_id=id)
    except Supervisor.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "supervisor not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = SupervisorSerializer(supervisor)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_hr_by_id(request, id):
    try:
        # Attempt to get the Manager instance by ID
        hr = Hr.objects.get(hr_id=id)
    except Hr.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "Hr not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = HrSerializer(hr)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def view_employee_by_id(request, id):
    try:
        # Retrieve the specific employee profile using get_object_or_404
        employee = get_object_or_404(Employee, employee_id=id)

        # Serialize the employee data
        serializer = EmployeeSerializer(employee)

        # Return the serialized data as the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle any potential errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_department(request, id):
    try:
        department = Department.objects.get(id=id)
        serializer = DepartmentSerializer(department)  # No need for request.data here
        return Response({
            "message": "Department fetched successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

# @api_view(['POST'])
# def common_user_login(request):
#     if request.method == 'POST':
#         serializer = LoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             user_id = serializer.validated_data['user_id']
#             password = serializer.validated_data['password'].encode('utf-8')

#             # User models and their respective roles
#             user_roles = [
#                 {'model': Manager, 'role': 'manager', 'id_field': 'manager_id'},
#                 {'model': Supervisor, 'role': 'supervisor', 'id_field': 'supervisor_id'},
#                 {'model': Employee, 'role': 'employee', 'id_field': 'employee_id'},
#                 {'model': Admin, 'role': 'admin', 'id_field': 'user_id'},
#                 {'model': Hr, 'role': 'hr', 'id_field': 'hr_id'},
#             ]

#             def authenticate_user(user_model, user_id_field, role, user_id):
#                 try:
#                     user = user_model.objects.get(username=username, **{user_id_field: user_id})
#                     if bcrypt.checkpw(password, user.password.encode('utf-8')):
#                         set_session(request, user, role, user_id)  # Pass user_id here
#                         Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)
#                         return Response({"message": f"Login successful", "role": role, "user_id": user_id}, status=status.HTTP_200_OK)
#                 except user_model.DoesNotExist:
#                     return None

#             def set_session(request, user, role, user_id):
#                 request.session['user'] = user.username
#                 request.session['user_id'] = user_id
#                 request.session['role'] = role
#                 request.session['is_authenticated'] = True  # Marking user as authenticated
#                 if hasattr(user, 'email'):
#                     request.session['email'] = user.email
#                 request.session.set_expiry(3600)  # Session expires after 1 hour

#             # Attempt to authenticate against each role
#             for role_info in user_roles:
#                 response = authenticate_user(role_info['model'], role_info['id_field'], role_info['role'], user_id)
#                 if response:
#                     return response

#             # If all authentication attempts fail
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.utils.timezone import now
from datetime import datetime, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import bcrypt
from .models import Employee, Shift
from .serializers import LoginSerializer

from django.utils import timezone
import logging
from datetime import datetime, timedelta
from leaves.models import LeaveRequest

########################## Commented becoz new version is replaced this is old version July 22 #########################

# # Setup logging
 
logger = logging.getLogger(__name__)
@api_view(['POST'])
def common_user_login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user_id = serializer.validated_data['user_id']
            password = serializer.validated_data['password'].encode('utf-8')

            # User models and their respective roles
            user_roles = [
                {'model': Employee, 'role': 'employee', 'id_field': 'employee_id'},
                {'model': Manager, 'role': 'manager', 'id_field': 'manager_id'},
                {'model': Supervisor, 'role': 'supervisor', 'id_field': 'supervisor_id'},
                {'model': Admin, 'role': 'admin', 'id_field': 'user_id'},
                {'model': Hr, 'role': 'hr', 'id_field': 'hr_id'},
                {'model': Ar, 'role': 'ar', 'id_field': 'ar_id'},
            ]

            def authenticate_user(user_model, user_id_field, role, user_id):
                try:
                    user = user_model.objects.get(username=username, **{user_id_field: user_id})
                    if bcrypt.checkpw(password, user.password.encode('utf-8')):
                        auto_leave_created = employee_check_and_auto_leave(user)
                        manager_auto_leave_created = manager_check_and_auto_leave(user)
                        hr_auto_leave_created = hr_check_and_auto_leave(user)
                        ar_auto_leave_created = ar_check_and_auto_leave(user)
                        supervisor_auto_leave_created = supervisor_check_and_auto_leave(user)# Check and create auto leave
                        set_session(request, user, role, user_id)
                        Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)
                        return Response({
                            "message": "Login successful",
                            "role": role,
                            "user_id": user_id,
                            "auto_leave_created": auto_leave_created,
                            "manager_auto_leave_created": manager_auto_leave_created,
                            "supervisor_auto_leave_created": supervisor_auto_leave_created,
                            "hr_auto_leave_created": hr_auto_leave_created,
                            "ar_auto_leave_created": ar_auto_leave_created
                        }, status=status.HTTP_200_OK)
                except user_model.DoesNotExist:
                    return None

            def set_session(request, user, role, user_id):
                request.session['user'] = user.username
                request.session['user_id'] = user_id
                request.session['role'] = role
                request.session['is_authenticated'] = True  # Marking user as authenticated
                if hasattr(user, 'email'):
                    request.session['email'] = user.email
                request.session.set_expiry(3600)  # Session expires after 1 hour

            # Attempt to authenticate against each role
            for role_info in user_roles:
                response = authenticate_user(role_info['model'], role_info['id_field'], role_info['role'], user_id)
                if response:
                    return response

            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
def employee_check_and_auto_leave(user):
    """Check if user has logged in late and auto-create leave request if needed."""
    try:
        if isinstance(user, Employee) and user.shift:
            shift = user.shift  # Get assigned shift
            today = timezone.localdate()  # Get current date
            shift_start_datetime = datetime.combine(today, shift.shift_start_time)

            # Convert shift_start_datetime to timezone-aware
            shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())

            shift_max_login_datetime = shift_start_datetime + timedelta(hours=1)  # 1-hour grace period
            current_datetime = timezone.now()  # Always timezone-aware

            if current_datetime > shift_max_login_datetime:
                # Check if leave already exists for today
                leave_exists = LeaveRequest.objects.filter(user=user.username, start_date=today).exists()
                if not leave_exists:
                    logger.info(f"Auto leave being created for {user.username} on {today}")

                    # Fetch or create leave balance
                    leave_balance, _ = LeaveBalance.objects.get_or_create(
                        user=user.username,
                        defaults={
                            'medical_leave': 0,
                            'vacation_leave': 0,
                            'personal_leave': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                        }
                    )

                    # Determine leave type based on available balance
                    leave_type = None
                    if leave_balance.personal_leave > 0:
                        leave_type = "personal"
                        leave_balance.personal_leave -= 1
                    elif leave_balance.vacation_leave > 0:
                        leave_type = "vacation"
                        leave_balance.vacation_leave -= 1
                    elif leave_balance.medical_leave > 0:
                        leave_type = "medical"
                        leave_balance.medical_leave -= 1
                    else:
                        # If no leave balance is available, still create the leave as personal
                        leave_type = "personal"
                        leave_balance.total_absent_days += 1  # Increment absent days if no leave is available

                    # Update total leave days
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

                    # Create the auto leave request
                    LeaveRequest.objects.create(
                        user=user.username,
                        user_id=user.employee_id,
                        start_date=today,
                        end_date=today,
                        leave_type=leave_type,
                        reason="Auto Leave: Late or No Login",
                        status="approved",
                        email=user.email if hasattr(user, 'email') else "",
                        employee=user,  # Foreign key reference
                        is_auto_leave=True  # Mark as auto leave
                    )

                    logger.info(f"Auto leave created for {user.username} with leave type {leave_type}")

                    # Return a message to be displayed
                    return f"Today you are absent for not logging in on time."
                
        return None  # No message if login is on time or no leave is created
    except Exception as e:
        logger.error(f"Auto leave creation error for {user.username}: {str(e)}")
        return None  # Fail silently if an error occurs
   
def manager_check_and_auto_leave(user):
    """Check if user has logged in late and auto-create leave request if needed."""
    try:
        if isinstance(user, Manager) and user.shift:
            shift = user.shift  # Get assigned shift
            today = timezone.localdate()  # Get current date
            shift_start_datetime = datetime.combine(today, shift.shift_start_time)

            # Convert shift_start_datetime to timezone-aware
            shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())

            shift_max_login_datetime = shift_start_datetime + timedelta(hours=1)  # 1-hour grace period
            current_datetime = timezone.now()  # Always timezone-aware

            if current_datetime > shift_max_login_datetime:
                # Check if leave already exists for today
                leave_exists = ManagerLeaveRequest.objects.filter(user=user.username, start_date=today).exists()
                if not leave_exists:
                    logger.info(f"Auto leave being created for {user.username} on {today}")

                    # Fetch or create leave balance
                    leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(
                        user=user.username,
                        defaults={
                            'medical_leave': 0,
                            'vacation_leave': 0,
                            'personal_leave': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                        }
                    )

                    # Determine leave type based on available balance
                    leave_type = None
                    if leave_balance.personal_leave > 0:
                        leave_type = "personal"
                        leave_balance.personal_leave -= 1
                    elif leave_balance.vacation_leave > 0:
                        leave_type = "vacation"
                        leave_balance.vacation_leave -= 1
                    elif leave_balance.medical_leave > 0:
                        leave_type = "medical"
                        leave_balance.medical_leave -= 1
                    else:
                        # If no leave balance is available, still create the leave as personal (as a fallback)
                        leave_type = "personal"
                        leave_balance.total_absent_days += 1  # Increment absent days if no leave is available

                    # Update total leave days
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

                    # Create the auto leave request
                    ManagerLeaveRequest.objects.create(
                        user=user.username,
                        user_id=user.manager_id,
                        start_date=today,
                        end_date=today,
                        leave_type=leave_type,
                        reason="Auto Leave: Late or No Login",
                        status="approved",
                        email=user.email if hasattr(user, 'email') else "",
                        manager=user,  # Foreign key reference
                        is_auto_leave=True  # Mark as auto leave
                    )

                    logger.info(f"Auto leave created for {user.username} with leave type {leave_type}")

                    # Return a message to be displayed
                    return f"Today you are absent for not logging in on time."
                
        return None  # No message if login is on time or no leave is created
    except Exception as e:
        logger.error(f"Auto leave creation error for {user.username}: {str(e)}")
        return None  # Fail silently if an error occurs 
    

def supervisor_check_and_auto_leave(user):
    """Check if user has logged in late and auto-create leave request if needed."""
    try:
        if isinstance(user, Supervisor) and user.shift:
            shift = user.shift  # Get assigned shift
            today = timezone.localdate()  # Get current date
            shift_start_datetime = datetime.combine(today, shift.shift_start_time)

            # Convert shift_start_datetime to timezone-aware
            shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())

            shift_max_login_datetime = shift_start_datetime + timedelta(hours=1)  # 1-hour grace period
            current_datetime = timezone.now()  # Always timezone-aware

            if current_datetime > shift_max_login_datetime:
                # Check if leave already exists for today
                leave_exists = SupervisorLeaveRequest.objects.filter(user=user.username, start_date=today).exists()
                if not leave_exists:
                    logger.info(f"Auto leave being created for {user.username} on {today}")

                    # Fetch or create leave balance
                    leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(
                        user=user.username,
                        defaults={
                            'medical_leave': 0,
                            'vacation_leave': 0,
                            'personal_leave': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                        }
                    )

                    # Determine leave type based on available balance
                    leave_type = None
                    if leave_balance.personal_leave > 0:
                        leave_type = "personal"
                        leave_balance.personal_leave -= 1
                    elif leave_balance.vacation_leave > 0:
                        leave_type = "vacation"
                        leave_balance.vacation_leave -= 1
                    elif leave_balance.medical_leave > 0:
                        leave_type = "medical"
                        leave_balance.medical_leave -= 1
                    else:
                        # If no leave balance is available, still create the leave as personal (as a fallback)
                        leave_type = "personal"
                        leave_balance.total_absent_days += 1  # Increment absent days if no leave is available

                    # Update total leave days
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

                    # Create the auto leave request
                    SupervisorLeaveRequest.objects.create(
                        user=user.username,
                        user_id=user.supervisor_id,
                        start_date=today,
                        end_date=today,
                        leave_type=leave_type,
                        reason="Auto Leave: Late or No Login",
                        status="approved",
                        email=user.email if hasattr(user, 'email') else "",
                        supervisor=user,  # Foreign key reference
                        is_auto_leave=True  # Mark as auto leave
                    )

                    logger.info(f"Auto leave created for {user.username} with leave type {leave_type}")

                    # Return a message to be displayed
                    return f"Today you are absent for not logging in on time."
                
        return None  # No message if login is on time or no leave is created
    except Exception as e:
        logger.error(f"Auto leave creation error for {user.username}: {str(e)}")
        return None  # Fail silently if an error occurs  


def hr_check_and_auto_leave(user):
    """Check if HR user has logged in late and auto-create leave request if needed."""
    try:
        if isinstance(user, Hr) and user.shift:
            shift = user.shift  # Get assigned shift
            today = timezone.localdate()  # Get current date
            shift_start_datetime = datetime.combine(today, shift.shift_start_time)

            # Convert shift_start_datetime to timezone-aware
            shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())

            shift_max_login_datetime = shift_start_datetime + timedelta(hours=1)  # 1-hour grace period
            current_datetime = timezone.now()  # Always timezone-aware

            if current_datetime > shift_max_login_datetime:
                # Check if leave already exists for today
                leave_exists = HrLeaveRequest.objects.filter(user=user.username, start_date=today).exists()
                if not leave_exists:
                    logger.info(f"Auto leave being created for {user.username} on {today}")

                    # Fetch or create leave balance
                    leave_balance, _ = HrLeaveBalance.objects.get_or_create(
                        user=user.username,
                        defaults={
                            'medical_leave': 0,
                            'vacation_leave': 0,
                            'personal_leave': 0,
                            'total_leave_days': 0,
                            'total_absent_days': 0,
                        }
                    )

                    # Determine leave type based on available balance
                    leave_type = None
                    if leave_balance.personal_leave > 0:
                        leave_type = "personal"
                        leave_balance.personal_leave -= 1
                    elif leave_balance.vacation_leave > 0:
                        leave_type = "vacation"
                        leave_balance.vacation_leave -= 1
                    elif leave_balance.medical_leave > 0:
                        leave_type = "medical"
                        leave_balance.medical_leave -= 1
                    else:
                        # If no leave balance is available, still create the leave as personal (as a fallback)
                        leave_type = "personal"
                        leave_balance.total_absent_days += 1  # Increment absent days if no leave is available

                    # Update total leave days
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

                    # Create the auto leave request
                    HrLeaveRequest.objects.create(
                        user=user.username,
                        user_id=user.hr_id,
                        start_date=today,
                        end_date=today,
                        leave_type=leave_type,
                        reason="Auto Leave: Late or No Login",
                        status="approved",
                        email=user.email if hasattr(user, 'email') else "",
                        hr=user,  # Foreign key reference
                        is_auto_leave=True  # Mark as auto leave
                    )

                    logger.info(f"Auto leave created for {user.username} with leave type {leave_type}")

                    # Return a message to be displayed
                    return f"Today you are absent for not logging in on time."
                
        return None  # No message if login is on time or no leave is created
    except Exception as e:
        logger.error(f"Auto leave creation error for {user.username}: {str(e)}")
        return None  # Fail silently if an error occurs

def ar_check_and_auto_leave(user):
    """Check if user has logged in late and auto-create leave request if needed."""
    try:
        if isinstance(user, Ar) and user.shift:
            shift = user.shift  # Get assigned shift
            today = timezone.localdate()  # Get current date
            shift_start_datetime = datetime.combine(today, shift.shift_start_time)

            # Convert shift_start_datetime to timezone-aware
            shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())

            shift_max_login_datetime = shift_start_datetime + timedelta(hours=1)  # 1-hour grace period
            current_datetime = timezone.now()  # Always timezone-aware

            if current_datetime > shift_max_login_datetime:
                # Check if leave already exists for today
                leave_exists = ArLeaveRequest.objects.filter(user=user.username, start_date=today).exists()
                if not leave_exists:
                    logger.info(f"Auto leave being created for {user.username} on {today}")

                    ArLeaveRequest.objects.create(
                        user=user.username,
                        user_id=user.ar_id,
                        start_date=today,
                        end_date=today,
                        leave_type="personal",  # Default leave type
                        reason="Auto Leave: Late or No Login",
                        status="approved",
                        email=user.email if hasattr(user, 'email') else "",
                        ar=user  # Foreign key reference
                    )

                    logger.info(f"Auto leave created for {user.username}")

                    # Return a message to be displayed
                    return f"Today you are absent for not logging in on time."
                
        return None  # No message if login is on time or no leave is created
    except Exception as e:
        logger.error(f"Auto leave creation error for {user.username}: {str(e)}")
        return None  # Fail silently if an error occurs    
   

@api_view(['GET'])
def admin_list(request):
    try:
        admin = Admin.objects.all()  # Get all Manager instances
        serializer = AdminSerializer(admin, many=True)  # Serialize multiple managers
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # If any exception occurs, return an internal server error with the exception message
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @api_view(['POST'])
# def common_user_login(request):
#     """
#     Handles login for multiple user roles, setting appropriate session data upon successful authentication.
#     """
#     if request.method == 'POST':
#         serializer = LoginSerializer(data=request.data)
        
#         if serializer.is_valid():
#             username = serializer.validated_data['username']
#             user_id = serializer.validated_data['user_id']
#             password = serializer.validated_data['password'].encode('utf-8')

#             # Define user roles and corresponding models
#             user_roles = [
#                 {'model': Manager, 'role': 'manager', 'id_field': 'manager_id'},
#                 {'model': Supervisor, 'role': 'supervisor', 'id_field': 'supervisor_id'},
#                 {'model': Employee, 'role': 'employee', 'id_field': 'employee_id'},
#                 {'model': Admin, 'role': 'admin', 'id_field': 'user_id'},
#                 {'model': ManagingDirector, 'role': 'md', 'id_field': 'user_id'},
#             ]

#             def authenticate_user(user_model, user_id_field, role):
#                 """
#                 Authenticates a user against the provided user model and role.
#                 """
#                 try:
#                     # Fetch user by username and specific ID field
#                     user = user_model.objects.get(username=username, **{user_id_field: user_id})
#                     # Verify password
#                     if bcrypt.checkpw(password, user.password.encode('utf-8')):
#                         set_session(request, user, role)
#                         # Mark undelivered messages as delivered
#                         Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)
#                         return Response(
#                             {"message": f"Login successful", "role": role, "user_id": user_id},
#                             status=status.HTTP_200_OK
#                         )
#                 except user_model.DoesNotExist:
#                     return None

#             def set_session(request, user, role):
#                 """
#                 Sets session data for the authenticated user.
#                 """
#                 session = request.session
#                 session['user'] = username
#                 session['user_id'] = user_id
#                 session['role'] = role
#                 if hasattr(user, 'email'):
#                     session['email'] = user.email
#                 session.save()

#             # Attempt authentication for each role
#             for role_info in user_roles:
#                 response = authenticate_user(role_info['model'], role_info['id_field'], role_info['role'])
#                 if response:
#                     return response

#             # If all authentication attempts fail
#             return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#         # If the serializer is invalid
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# import secrets

# def set_session(request, user, role):
#     """
#     Sets session data for the authenticated user and generates a session token.
#     """
#     session = request.session
#     session['user'] = user.username
#     session['user_id'] = user.id
#     session['role'] = role
#     if hasattr(user, 'email'):
#         session['email'] = user.email

#     # Generate a session token (e.g., using secrets)
#     session_token = secrets.token_hex(32)
#     session['session_token'] = session_token
#     session.save()

#     return session_token

# @api_view(['POST'])
# def common_user_login(request):
#     """
#     Handles login for multiple user roles, setting appropriate session data and returning a session token.
#     """
#     serializer = LoginSerializer(data=request.data)
#     if serializer.is_valid():
#         username = serializer.validated_data['username']
#         user_id = serializer.validated_data['user_id']
#         password = serializer.validated_data['password'].encode('utf-8')

#         user_roles = [
#             {'model': Manager, 'role': 'manager', 'id_field': 'manager_id'},
#             {'model': Supervisor, 'role': 'supervisor', 'id_field': 'supervisor_id'},
#             {'model': Employee, 'role': 'employee', 'id_field': 'employee_id'},
#             {'model': Admin, 'role': 'admin', 'id_field': 'user_id'},
#             {'model': ManagingDirector, 'role': 'md', 'id_field': 'user_id'},
#         ]

#         def authenticate_user(user_model, user_id_field, role):
#             """
#             Authenticates a user against the provided user model and role.
#             """
#             try:
#                 user = user_model.objects.get(username=username, **{user_id_field: user_id})
#                 if bcrypt.checkpw(password, user.password.encode('utf-8')):
#                     # session_token = set_session(request, user, role)
#                     Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)
#                     login(user,role)
#                     return {
#                         "message": "Login successful",
#                         "role": role,
#                         "user_id": user_id,
#                         # "session_token": session_token
#                     }
#             except user_model.DoesNotExist:
#                 return None

#         for role_info in user_roles:
#             response = authenticate_user(role_info['model'], role_info['id_field'], role_info['role'])
#             if response:
#                 return Response(response, status=status.HTTP_200_OK)

#         return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




########################## Commented becoz new version is replaced this is old version July 22 #########################

@api_view(['GET'])
def details(request):
    try:
        # Fetch all users data
        admins = Admin.objects.all()
        hrs = Hr.objects.all()
        ars = Ar.objects.all()
        managers = Manager.objects.all()
        employees = Employee.objects.all()
        supervisors = Supervisor.objects.all()

        # Serialize data
        data = {
            'admins': AdminSerializer(admins, many=True).data,
            'hrs': HrSerializer(hrs, many=True).data,
            'ars': ArSerializer(ars, many=True).data,
            'managers': ManagerSerializer(managers, many=True).data,
            'employees': EmployeeSerializer(employees, many=True).data,
            'supervisors': SupervisorSerializer(supervisors, many=True).data,
        }

        # Return success response with serialized data
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle exceptions and return error response
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import LoginSerializer, ResetPasswordSerializer
from django.contrib.auth.models import User  # Adjust based on your user model
import bcrypt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

@api_view(['POST'])
def user_logout(request):
    request.session.flush()
    return Response({"message": "You have been logged out successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')

    try:
        user = Admin.objects.get(email=email)
        token = generate_reset_token(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/admin/reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.,',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
    except Admin.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request, token):
    """
    Reset the user's password using a reset token sent via email.
    """
    # Validate the reset token
    if not validate_reset_token(token):
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed to reset the password after token is validated
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        password = serializer.validated_data['password']

        # Get the email associated with the reset token
        email = get_email_from_token(token)
        if not email:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user by email
            user = Admin.objects.get(email=email)

            # Hash the new password before saving
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password and reset the token fields
            user.password = hashed_password
            user.reset_token = None  # Clear the reset token
            user.token_expiration = None  # Clear the token expiration
            user.save()

            # Return a success response
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Admin.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def custom_admin_home(request):
    if 'user' not in request.session:
        return Response({"error": "Unauthorized."}, status=status.HTTP_401_UNAUTHORIZED)

    managers = Manager.objects.all()
    employees = Employee.objects.all()
    # Collect other models as needed...

    context = {
        'managers': managers,
        'employees': employees,
        # Add other context variables as needed...
    }

    return Response(context, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Manager, Supervisor, Employee
from .serializers import ManagerSerializer, SupervisorSerializer, EmployeeSerializer
from django.db.models import Sum
from datetime import timedelta

@api_view(['GET'])
def manager_dashboard(request):
    if request.user.is_authenticated and request.session.get('role') == 'manager':
        manager_id = request.session.get('user_id')
        try:
            manager = Manager.objects.get(manager_id=manager_id)
            serializer = ManagerSerializer(manager)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

# @api_view(['GET'])
# def supervisor_dashboard(request):
#     # if request.user.is_authenticated and request.session.get('role') == 'supervisor':
#         supervisor_id = request.session.get('user_id')
#         try:
#             supervisor = Supervisor.objects.get(supervisor_id=supervisor_id)
#             serializer = SupervisorSerializer(supervisor)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Supervisor.DoesNotExist:
#             return Response({'error': 'Supervisor not found'}, status=status.HTTP_404_NOT_FOUND)
#     # return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

from leaves .models import SupervisorLeaveBalance
from leaves .serializers import SupervisorLeaveBalanceSerializer
from attendance .views import supervisor_calculate_total_present_days

@api_view(['GET'])
def supervisor_dashboard(request):
    """
    Retrieves employee dashboard data, including employee details, leave balance, total permission hours, and total present days.
    """
    supervisor_id = request.session.get('user_id')
    user = request.session.get('user')

    if not supervisor_id or not user:
        return Response({'error': 'Session data missing or corrupted'}, status=status.HTTP_400_BAD_REQUEST)

    try:
            
            supervisor = Supervisor.objects.get(supervisor_id=supervisor_id)
            leave_balance = SupervisorLeaveBalance.objects.filter(user=user).first()
            total_present_days = supervisor_calculate_total_present_days(supervisor.id)

            response_data = {
                'supervisor': SupervisorSerializer(supervisor).data,
                'leave_balance': SupervisorLeaveBalanceSerializer(leave_balance).data if leave_balance else None,
                'total_present_days': total_present_days,
            }
            return Response(response_data, status=status.HTTP_200_OK)

    except Supervisor.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)



# @api_view(['GET'])
# def employee_dashboard(request):
#     # if request.user.is_authenticated and request.session.get('role') == 'employee':
#         employee_id = request.session.get('user_id')
#         user = request.session.get('user')
#         try:
#             employee = Employee.objects.get(employee_id=employee_id)
#             leave_balance = LeaveBalance.objects.filter(user=user).first()
            
#             # # Calculate total approved permission hours
#             total_permission_hours = PermissionHour.objects.filter(
#                 employee=employee, status='Approved'
#             ).aggregate(total=Sum('duration'))['total'] or timedelta()

#             # Assume calculate_total_present_days is a utility function
#             total_present_days = calculate_total_present_days(employee.id)

#             response_data = {
#                 'employee': EmployeeSerializer(employee).data,
#                 'leave_balance': LeaveBalanceSerializer(leave_balance).data if leave_balance else None,
#                 # 'total_permission_hours': total_permission_hours.total_seconds() / 3600,  # Convert to hours
#                 'total_present_days': total_present_days,
#             }
#             return Response(response_data, status=status.HTTP_200_OK)
#         except Employee.DoesNotExist:
#             return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
#     # return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)


########################## Commented becoz new version is replaced this is old version July 22 #########################

@api_view(['GET'])
def employee_dashboard(request):
    """
    Retrieves employee dashboard data, including employee details, leave balance, total permission hours, and total present days.
    """
    
    employee_id = request.session.get('user_id')
    user = request.session.get('user')

    if not employee_id or not user:
        return Response({'error': 'Session data missing or corrupted'}, status=status.HTTP_400_BAD_REQUEST)

    try:
            
            employee = Employee.objects.get(employee_id=employee_id)
            leave_balance = LeaveBalance.objects.filter(user=user).first()

          

            response_data = {
                'employee': EmployeeSerializer(employee).data,
                'leave_balance': LeaveBalanceSerializer(leave_balance).data if leave_balance else None,
               
            }
            return Response(response_data, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)



from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manager, Employee
from django.core.mail import send_mail
from django.conf import settings
import bcrypt

@api_view(['POST'])
def forgot_password_manager(request):
    email = request.data.get('email')

    try:
        user = Manager.objects.get(email=email)
        token = generate_reset_token_for_manager(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/manager/reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.,',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
    except Manager.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password_manager(request, token):
    """
    Reset the user's password using a reset token sent via email.
    """
    # Validate the reset token
    if not validate_reset_token_for_manager(token):
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed to reset the password after token is validated
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        password = serializer.validated_data['password']

        # Get the email associated with the reset token
        email = get_email_from_token_for_manager(token)
        if not email:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user by email
            user = Manager.objects.get(email=email)

            # Hash the new password before saving
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password and reset the token fields
            user.password = hashed_password
            user.reset_token = None  # Clear the reset token
            user.token_expiration = None  # Clear the token expiration
            user.save()

            # Return a success response
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Manager.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password_employee(request):
    email = request.data.get('email')

    try:
        user = Employee.objects.get(email=email)
        token = generate_reset_token_for_employee(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/employee/reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Employee.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password_employee(request, token):
    password = request.data.get('password')

    if validate_reset_token_for_employee(token):  # Check if the token is valid
        email = get_email_from_token_for_employee(token)  # Get email from token
        if email:
            try:
                user = Employee.objects.get(email=email)
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update the password and clear the reset token and expiration
                user.password = hashed_password
                user.reset_token = None
                user.token_expiration = None
                user.save()

                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            except Employee.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manager, Employee, Department, Shift, Location
from .serializers import ManagerSerializer, EmployeeSerializer, DepartmentSerializer, ShiftSerializer, LocationSerializer
import bcrypt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Add Manager
# @api_view(['POST'])
# def add_manager(request):
#     serializer = ManagerSerializer(data=request.data)

#     if serializer.is_valid():
#         try:
#             raw_password = request.data.get('password')
#             validate_password(raw_password)  # Ensure password meets security standards
#         except ValidationError as e:
#             return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

#         manager = serializer.save()  # This triggers auto-generation of employee_id

#         return Response({
#             "message": "Manager added successfully!",
#             "manager_id": manager.manager_id  # Return generated employee_id in response
#         }, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_manager(request):
    print("Raw request.POST:", dict(request.POST))  # Debug
    print("Raw request.FILES:", dict(request.FILES))  # Debug

    # Copy form data (not files)
    data = request.POST.dict()

    # Handle 'streams' JSON parsing
    try:
        data['streams'] = json.loads(request.POST.get('streams', '{}'))
        print("Parsed streams:", data['streams'])
    except json.JSONDecodeError as e:
        print("Streams parsing error:", str(e))
        return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Add image from request.FILES if it exists
    files = {'manager_image': request.FILES.get('manager_image')} if request.FILES.get('manager_image') else {}

    # Combine and pass to serializer
    serializer = ManagerSerializer(data={**data, **files})

    if serializer.is_valid():
        try:
            raw_password = data.get('password')
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        manager = serializer.save()
        return Response({
            "message": "Manager added successfully!",
            "manager_id": manager.manager_id
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# # Update Manager
# @api_view(['PUT'])
# def update_manager(request, id):
#     try:
#         manager = Manager.objects.get(manager_id=id)
#     except Manager.DoesNotExist:
#         return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = ManagerSerializer(manager, data=request.data, partial=True)
#     if serializer.is_valid():
#         if 'password' in request.data:
#             raw_password = request.data.get('password')

#             # Validate the password
#             try:
#                 validate_password(raw_password)
#             except ValidationError as e:
#                 return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            

#         serializer.save()
#         return Response(
#             {"message": "Manager updated successfully!", "manager": serializer.data},
#             status=status.HTTP_200_OK
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_manager(request, id):
    try:
        manager = Manager.objects.get(manager_id=id)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create mutable copy of request data
    data = request.POST.dict() if request.POST else {}
    files = request.FILES

    # Handle streams separately
    streams_data = request.POST.get('streams')
    if streams_data:
        try:
            data['streams'] = json.loads(streams_data)
        except json.JSONDecodeError as e:
            return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Handle password validation if it's being updated
    if 'password' in data and data['password']:
        try:
            validate_password(data['password'])
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Create serializer data combining all fields
    serializer_data = {**data, **files}
    
    # Use partial=True to allow partial updates
    serializer = ManagerSerializer(manager, data=serializer_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Manager updated successfully!", "manager": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Manager
@api_view(['DELETE'])
def delete_manager(request, id):
    try:
        manager = Manager.objects.get(manager_id=id)
        manager.delete()
        return Response({"message": "Manager deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)
    
# # Add supervisor
# @api_view(['POST'])
# def add_supervisor(request):
#     serializer = SupervisorSerializer(data=request.data)

#     if serializer.is_valid():
#         try:
#             raw_password = request.data.get('password')
#             validate_password(raw_password)  # Ensure password meets security standards
#         except ValidationError as e:
#             return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

#         supervisor = serializer.save()  # This triggers auto-generation of employee_id

#         return Response({
#             "message": "Supervisor added successfully!",
#             "supervisor_id": supervisor.supervisor_id  # Return generated employee_id in response
#         }, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # Update Manager
# @api_view(['PUT'])
# def update_supervisor(request, id):
#     try:
#         supervisor = Supervisor.objects.get(supervisor_id=id)
#     except Supervisor.DoesNotExist:
#         return Response({"error": "supervisor not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = SupervisorSerializer(supervisor, data=request.data, partial=True)
#     if serializer.is_valid():
#         if 'password' in request.data:
#             raw_password = request.data.get('password')

#             # Validate the password
#             try:
#                 validate_password(raw_password)
#             except ValidationError as e:
#                 return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            

#         serializer.save()
#         return Response(
#             {"message": "Supervisor updated successfully!", "manager": serializer.data},
#             status=status.HTTP_200_OK
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Add supervisor
@api_view(['POST'])
def add_supervisor(request):
    print("Raw request.POST:", dict(request.POST))  # Debug
    print("Raw request.FILES:", dict(request.FILES))  # Debug

    # Copy form data (not files)
    data = request.POST.dict()

    # Handle 'streams' JSON parsing
    try:
        data['streams'] = json.loads(request.POST.get('streams', '{}'))
        print("Parsed streams:", data['streams'])
    except json.JSONDecodeError as e:
        print("Streams parsing error:", str(e))
        return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Add image from request.FILES if it exists
    files = {'supervisor_image': request.FILES.get('supervisor_image')} if request.FILES.get('supervisor_image') else {}

    # Combine and pass to serializer
    serializer = SupervisorSerializer(data={**data, **files})

    if serializer.is_valid():
        try:
            raw_password = data.get('password')
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        supervisor = serializer.save()
        return Response({
            "message": "Supervisor added successfully!",
            "supervisor_id": supervisor.supervisor_id
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update Supervisor
@api_view(['PUT'])
def update_supervisor(request, id):
    try:
        supervisor = Supervisor.objects.get(supervisor_id=id)
    except Supervisor.DoesNotExist:
        return Response({"error": "Supervisor not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create mutable copy of request data
    data = request.POST.dict() if request.POST else {}
    files = request.FILES

    # Handle streams separately
    streams_data = request.POST.get('streams')
    if streams_data:
        try:
            data['streams'] = json.loads(streams_data)
        except json.JSONDecodeError as e:
            return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Handle password validation if it's being updated
    if 'password' in data and data['password']:
        try:
            validate_password(data['password'])
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Create serializer data combining all fields
    serializer_data = {**data, **files}
    
    # Use partial=True to allow partial updates
    serializer = SupervisorSerializer(supervisor, data=serializer_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Supervisor updated successfully!", "supervisor": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Manager
@api_view(['DELETE'])
def delete_supervisor(request, id):
    try:
        supervisor = Supervisor.objects.get(supervisor_id=id)
        supervisor.delete()
        return Response({"message": "Supervisor deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Manager.DoesNotExist:
        return Response({"error": "Superviosr not found."}, status=status.HTTP_404_NOT_FOUND) 
    


@api_view(['POST'])
def forgot_password_supervisor(request):
    email = request.data.get('email')

    try:
        user = Supervisor.objects.get(email=email)
        token = generate_reset_token_for_supervisor(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/supervisor/reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Manager.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password_supervisor(request, token):
    password = request.data.get('password')

    if validate_reset_token_for_supervisor(token):  # Check if the token is valid
        email = get_email_from_token_for_supervisor(token)  # Get email from token
        if email:
            try:
                user = Supervisor.objects.get(email=email)
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Update the password and clear the reset token and expiration
                user.password = hashed_password
                user.reset_token = None
                user.token_expiration = None
                user.save()

                return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
            except Manager.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)     

# View all Employee Profiles
@api_view(['GET'])
def employee_list(request):
    try:
        # Retrieve all employees from the database
        employees = Employee.objects.all()

        # Serialize the data (many=True because we're passing a queryset)
        serializer = EmployeeSerializer(employees, many=True)

        # Return the serialized employee data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    



# Update Supervisor Profile
@api_view(['PUT'])
def update_supervisor_profile(request, id):
    supervisor = get_object_or_404(Supervisor, supervisor_id=id)  # Fix: Use Supervisor instead of Manager
    serializer = SupervisorSerializer(supervisor, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Supervisor profile updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 




# @api_view(['POST'])
# def add_employee(request):
#     serializer = EmployeeSerializer(data=request.data)

#     if serializer.is_valid():
#         try:
#             raw_password = request.data.get('password')
#             validate_password(raw_password)
#         except ValidationError as e:
#             return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

#         employee = serializer.save()

#         return Response({
#             "message": "Employee added successfully!",
#             "employee_id": employee.employee_id
#         }, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# @api_view(['PUT'])
# def update_employee(request, id):
#     try:
#         employee = Employee.objects.get(employee_id=id)
#     except Employee.DoesNotExist:
#         return Response({"error": "employee not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = EmployeeSerializer(employee, data=request.data, partial=True)
#     if serializer.is_valid():
#         if 'password' in request.data:
#             raw_password = request.data.get('password')

#             # Validate the password
#             try:
#                 validate_password(raw_password)
#             except ValidationError as e:
#                 return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            

#         serializer.save()
#         return Response(
#             {"message": "Employee updated successfully!", "employee": serializer.data},
#             status=status.HTTP_200_OK
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def add_employee(request):
    print("Raw request.POST:", dict(request.POST))  # Debug
    print("Raw request.FILES:", dict(request.FILES))  # Debug

    # Copy form data (not files)
    data = request.POST.dict()

    # Handle 'streams' JSON parsing
    try:
        data['streams'] = json.loads(request.POST.get('streams', '{}'))
        print("Parsed streams:", data['streams'])
    except json.JSONDecodeError as e:
        print("Streams parsing error:", str(e))
        return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Add image from request.FILES if it exists
    files = {'employee_image': request.FILES.get('employee_image')} if request.FILES.get('employee_image') else {}

    # Combine and pass to serializer
    serializer = EmployeeSerializer(data={**data, **files})

    if serializer.is_valid():
        try:
            raw_password = data.get('password')
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        employee = serializer.save()
        return Response({
            "message": "Employee added successfully!",
            "employee_id": employee.employee_id
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_employee(request, id):
    try:
        employee = Employee.objects.get(employee_id=id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create mutable copy of request data
    data = request.POST.dict() if request.POST else {}
    files = request.FILES

    # Handle streams separately
    streams_data = request.POST.get('streams')
    if streams_data:
        try:
            data['streams'] = json.loads(streams_data)
        except json.JSONDecodeError as e:
            return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Handle password validation if it's being updated
    if 'password' in data and data['password']:
        try:
            validate_password(data['password'])
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Create serializer data combining all fields
    serializer_data = {**data, **files}
    
    # Use partial=True to allow partial updates
    serializer = EmployeeSerializer(employee, data=serializer_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Employee updated successfully!", "employee": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






@api_view(['DELETE'])
def delete_employee(request, id):
    try:
        # Attempt to get the employee with the given ID
        employee = Employee.objects.get(employee_id=id)
        employee.delete()
        return Response({"message": "Employee deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Employee.DoesNotExist:
        # If the employee does not exist, return an error response
        return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

# Repeat for Department
@api_view(['POST'])
def add_department(request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Department added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_department(request, id):
    department = Department.objects.get(id=id)
    serializer = DepartmentSerializer(department, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Department updated successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_department(request, id):
    try:
        department = Department.objects.get(id=id)
        department.delete()
        return Response({"message": "Department deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Department.DoesNotExist:
        return Response({"error": "Department not found."}, status=status.HTTP_404_NOT_FOUND)

# Repeat for Shift
@api_view(['POST'])
def add_shift(request):
    serializer = ShiftSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Shift added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_shift(request, id):
    shift = Shift.objects.get(id=id)
    serializer = ShiftSerializer(shift, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Shift updated successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_shift(request, id):
    try:
        shift = Shift.objects.get(id=id)
        shift.delete()
        return Response({"message": "Shift deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Shift.DoesNotExist:
        return Response({"error": "Shift not found."}, status=status.HTTP_404_NOT_FOUND)

# Repeat for Location
@api_view(['POST'])
def add_location(request):
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Location added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_location(request, id):
    location = Location.objects.get(id=id)
    serializer = LocationSerializer(location, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Location updated successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_location(request, id):
    try:
        location = Location.objects.get(id=id)
        location.delete()
        return Response({"message": "Location deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Location.DoesNotExist:
        return Response({"error": "Location not found."}, status=status.HTTP_404_NOT_FOUND)






from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manager, Employee, Department, Shift, Location
from .serializers import ManagerSerializer, EmployeeSerializer, DepartmentSerializer, ShiftSerializer, LocationSerializer
import bcrypt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@api_view(['GET'])
def md_home(request):
    if 'user' not in request.session:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    managers = Manager.objects.all()
    employees = Employee.objects.all()
    departments = Department.objects.all()
    shifts = Shift.objects.all()
    locations = Location.objects.all()

    context = {
        'managers': ManagerSerializer(managers, many=True).data,
        'employees': EmployeeSerializer(employees, many=True).data,
        'departments': DepartmentSerializer(departments, many=True).data,
        'shifts': ShiftSerializer(shifts, many=True).data,
        'locations': LocationSerializer(locations, many=True).data,
    }

    return Response(context, status=status.HTTP_200_OK)

@api_view(['POST'])
def md_add_manager(request):
    serializer = ManagerSerializer(data=request.data)
    if serializer.is_valid():
        raw_password = request.data.get('password')

        try:
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        serializer.validated_data['password'] = hashed_password

        serializer.save()
        return Response({"message": "Manager added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def md_add_supervisor(request):
    serializer = SupervisorSerializer(data=request.data)
    if serializer.is_valid():
        raw_password = request.data.get('password')

        try:
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        serializer.validated_data['password'] = hashed_password

        serializer.save()
        return Response({"message": "supervisor added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def md_add_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        raw_password = request.data.get('password')

        try:
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        serializer.validated_data['password'] = hashed_password

        serializer.save()
        return Response({"message": "Employee added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def md_add_department(request):
    serializer = DepartmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Department added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def md_add_shift(request):
    serializer = ShiftSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Shift added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def md_add_location(request):
    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Location added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #Delete functionality perform by mdfrom rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Manager, Employee, Department, Shift, Location
from .serializers import ManagerSerializer, EmployeeSerializer, DepartmentSerializer, ShiftSerializer, LocationSerializer

# Delete Functions
@api_view(['DELETE'])
def md_delete_manager(request, manager_id):
    manager = get_object_or_404(Manager, manager_id=manager_id)
    manager.delete()
    return Response({'message': 'Manager deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

# Delete Functions
@api_view(['DELETE'])
def md_delete_supervisor(request, supervisor_id):
    supervisor = get_object_or_404(Supervisor, supervisor_id=supervisor_id)
    supervisor.delete()
    return Response({'message': 'supervisor deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def md_delete_employee(request, employee_id):
    employee = get_object_or_404(Employee, employee_id=employee_id)
    employee.delete()
    return Response({'message': 'Employee deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def md_delete_department(request, department_id):
    department = get_object_or_404(Department, department_id=department_id)
    department.delete()
    return Response({'message': 'Department deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def md_delete_shift(request, shift_number):
    shift = get_object_or_404(Shift, shift_number=shift_number)
    shift.delete()
    return Response({'message': 'Shift deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def md_delete_location(request, location_id):
    location = get_object_or_404(Location, location_id=location_id)
    location.delete()
    return Response({'message': 'Location deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

# Update Functions
@api_view(['PUT'])
def md_update_manager(request, id):
    manager = get_object_or_404(Manager, id=id)
    serializer = ManagerSerializer(manager, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update Functions
@api_view(['PUT'])
def md_update_supervisor(request, id):
    supervisor = get_object_or_404(Supervisor, id=id)
    serializer = SupervisorSerializer(supervisor, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def md_update_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    serializer = EmployeeSerializer(employee, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def md_update_department(request, id):
    department = get_object_or_404(Department, id=id)
    serializer = DepartmentSerializer(department, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def md_update_shift(request, id):
    shift = get_object_or_404(Shift, id=id)
    serializer = ShiftSerializer(shift, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def md_update_location(request, id):
    location = get_object_or_404(Location, id=id)
    serializer = LocationSerializer(location, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Functions
@api_view(['POST'])
def forgot_password_md(request):
    email = request.data.get('email')
    try:
        user = ManagingDirector.objects.get(email=email)
        token = generate_reset_token_for_md(email)  # Replace with your token generation logic
        reset_link = f"http://127.0.0.1:8000/md/reset_password_md/{token}/"
        
        # Send email logic here...

        return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
    except ManagingDirector.DoesNotExist:
        return Response({'error': 'Email not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password_md(request, token):
    password = request.data.get('password')
    if validate_reset_token_for_md(token):  # Check if the token is valid
        email = get_email_from_token_for_md(token)  # Get email from token
        if email:
            try:
                user = ManagingDirector.objects.get(email=email)
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                user.password = hashed_password
                user.save()
                return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
            except ManagingDirector.DoesNotExist:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Employee, Manager
from .serializers import EmployeeSerializer, ManagerSerializer



# Update Employee Profile
@api_view(['PUT'])
def update_employee_profile(request, id):
    try:
        # Retrieve the employee object from the database
        employee = get_object_or_404(Employee, employee_id=id)

        # Log the incoming request data for debugging purposes
        print("Incoming request data:", request.data)

        # Serialize the data with the existing employee data
        serializer = EmployeeSerializer(employee, data=request.data, partial=True)

        # Check if the serializer is valid and log errors if any
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        else:
            # Log the validation errors for debugging
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# Update Manager Profile
@api_view(['PUT'])
def update_manager_profile(request, id):
    manager = get_object_or_404(Manager, manager_id=id)
    serializer = ManagerSerializer(manager, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Manager profile updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Update Manager Profile
@api_view(['PUT'])
def update_supervisor_profile(request, id):
    supervisor = get_object_or_404(Supervisor, supervisor_id=id)
    serializer = SupervisorSerializer(supervisor, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "supervisor profile updated successfully."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def manager_view_employee_profile(request):
    employee_id = request.data.get('employee_id')

    if not employee_id:
        return Response({"error": "Employee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = get_object_or_404(Employee, employee_id=employee_id)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({"error": f"No employee found with ID {employee_id}."}, status=status.HTTP_404_NOT_FOUND)
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Requests, Employee, Supervisor, Admin
from .serializers import RequestsSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_request(request):
    if request.method == 'POST':
        data = request.data
        employee_username = request.user.username  # Assume request.user is authenticated
        try:
            employee = Employee.objects.get(username=employee_username)
            supervisor = Supervisor.objects.get(id=data.get('supervisor_id'))

            new_request = Requests.objects.create(
                employee=employee,
                supervisor=supervisor,
                title=data.get('title'),
                request_ticket_id=data.get('request_ticket_id'),
                description=data.get('description'),
                status='onprocess',
            )
            serializer = RequestsSerializer(new_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found. Please log in again.'}, status=status.HTTP_400_BAD_REQUEST)
        except Supervisor.DoesNotExist:
            return Response({'error': 'Supervisor not found.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def supervisor_view_allrequest(request):
    if request.method == 'GET':
        supervisor_id = request.user.id  # Assume the user is authenticated and represents a supervisor
        try:
            supervisor = Supervisor.objects.get(supervisor_id=supervisor_id)
            requests = Requests.objects.filter(supervisor=supervisor)
            serializer = RequestsSerializer(requests, many=True)
            return Response(serializer.data)
        except Supervisor.DoesNotExist:
            return Response({'error': 'Supervisor not found.'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        try:
            request_obj = Requests.objects.get(id=request_id)
            if action == 'Approve':
                request_obj.status = 'Approved'
            elif action == 'Reject':
                request_obj.status = 'Rejected'
            elif action == 'Forward':
                admin = Admin.objects.first()
                if admin:
                    request_obj.supervisor = None
                    request_obj.admin = admin
                    request_obj.status = 'Forwarded'
                else:
                    return Response({'error': 'No admin available to forward the request.'}, status=status.HTTP_400_BAD_REQUEST)
            request_obj.save()
            return Response({'message': f'Request {action} successfully.'}, status=status.HTTP_200_OK)
        except Requests.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_view_request(request):
    if request.method == 'GET':
        forwarded_requests = Requests.objects.filter(status='Forwarded')
        serializer = RequestsSerializer(forwarded_requests, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        try:
            request_obj = Requests.objects.get(id=request_id)
            if action == 'Approve':
                supervisor = Supervisor.objects.first()
                if supervisor:
                    request_obj.admin = None
                    request_obj.supervisor = supervisor
                    request_obj.admin_status = 'Approved'
            elif action == 'Reject':
                supervisor = Supervisor.objects.first()
                if supervisor:
                    request_obj.admin = None
                    request_obj.supervisor = supervisor
                    request_obj.admin_status = 'Rejected'
            request_obj.save()
            return Response({'message': f'Request {action} successfully.'}, status=status.HTTP_200_OK)
        except Requests.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import News, Ticket, Requests, Manager
from .serializers import NewsSerializer, TicketSerializer, RequestsSerializer

@api_view(['POST'])
def send_news(request):
    if request.method == "POST":
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(date=timezone.now().date())  # Automatically set the date to today's date
            serializer.save()
            return Response({"message": "News sent successfully!", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer

@api_view(['GET'])
def view_news(request):
    # try:
        if request.method == "GET":
            all_news = News.objects.all()  # Querying all news items
            serializer = NewsSerializer(all_news, many=True)  # Serializing the data
            return Response(serializer.data, status=status.HTTP_200_OK)
    # except News.DoesNotExist:
    #     return Response(
    #         {"error": "No news found."},
    #         status=status.HTTP_404_NOT_FOUND
    #     )
    # except Exception as e:
    #     return Response(
    #         {"error": f"An unexpected error occurred: {str(e)}"},
    #         status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import News
from .serializers import NewsSerializer

@api_view(['PUT'])
def update_news(request, id):
    try:
        # Retrieve the news item by its ID
        news_item = News.objects.get(id=id)

        # Deserialize the request data and validate
        serializer = NewsSerializer(news_item, data=request.data, partial=True)  # Use partial=True to allow updating only specific fields

        if serializer.is_valid():
            # Save the updated data
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except News.DoesNotExist:
        return Response({"detail": "News item not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
def delete_news(request, id):
    try:
        # Retrieve the news item by its ID
        news_item = News.objects.get(id=id)

        # Delete the news item from the database
        news_item.delete()

        return Response({"detail": "News item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    except News.DoesNotExist:
        return Response({"detail": "News item not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def add_ticket(request):
    """
    API endpoint to create a new ticket.
    """
    try:
        data = request.data

        # Extract data from request
        receiver = data.get('receiver')
        admin_name = data.get('admin_name')
        manager_name = data.get('manager_name')
        proof = request.FILES.get('proof')  # Uploaded file, if any

        # Initialize assigned user
        assigned_user = None

        # Determine the user assigned based on the receiver
        if receiver == 'Admin':
            assigned_user = Admin.objects.filter(username=admin_name).first()
        elif receiver == 'Manager':
            assigned_user = Manager.objects.filter(manager_name=manager_name).first()
        else:
            return Response(
                {"error": "Invalid receiver type. Must be 'Admin' or 'Manager'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not assigned_user:
            return Response(
                {"error": f"No {receiver} found for the given details."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare ticket data for the serializer
        ticket_data = {
            "title": data.get('title'),
            "description": data.get('description'),
            "Reciver": receiver,
            "assigned_to": assigned_user.id,  # ForeignKey to either Admin or Manager
            "proof": proof,
        }

        # Validate and save the ticket
        serializer = TicketSerializer(data=ticket_data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Ticket created successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def self_request(request):
    if request.method == "GET":
        all_requests = Requests.objects.all()
        serializer = RequestsSerializer(all_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Todo
from .serializers import TodoSerializer


@api_view(['GET'])
def todo_list(request):
    """
    List all Todo items.
    """
    try:
        # Fetch all Todo items from the database
        todos = Todo.objects.all()
        
        # Serialize the data
        serializer = TodoSerializer(todos, many=True)
        
        # Return the serialized data with a 200 OK status
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle any unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def todo_create(request):
    """
    Create a new Todo item.
    """
    serializer = TodoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Todo item created successfully!", "data": serializer.data}, 
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "Invalid data provided", "details": serializer.errors}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['PATCH'])
def todo_toggle(request, id):
    """
    Toggle the 'completed' status of a Todo item by its ID.
    """
    # Fetch the Todo item or return a 404 error if not found
    todo = get_object_or_404(Todo, id=id)

    # Toggle the 'completed' status
    todo.completed = not todo.completed
    todo.save()

    # Serialize the updated Todo item
    serializer = TodoSerializer(todo)

    # Return a success response with the updated data
    return Response(
        {
            "message": "Todo status toggled successfully!",
            "data": serializer.data
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE'])
def todo_delete(request, id):
    """
    Delete a Todo item.
    """
    try:
        todo = get_object_or_404(Todo, id=id)
        todo.delete()
        return Response({"message": "Todo item deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"Error deleting todo with id {id}: {e}")
        return Response({"error": "Failed to delete todo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# all get functions code

# View Manager Profile

from .serializers import (
    ManagerSerializer, ManagerAttendanceSerializer, ManagerPerformanceReviewSerializer,
    ManagerSkillSerializer, ManagerTaskSerializer, ManagerDocumentSerializer
)
from authentication.models import Manager, Skill
from attendance.models import Attendance
from kpi.models import PerformanceReview
from documents.models import ManagerDocument
from projectmanagement.models import Task

@api_view(['GET'])
def view_manager_profile(request, id):
    try:
        # Attempt to get the Manager instance by ID
        manager = Manager.objects.get(manager_id=id)
    except Manager.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = ManagerSerializer(manager)
    return Response(serializer.data, status=status.HTTP_200_OK)



from .serializers import (
    ManagerSerializer, ManagerAttendanceSerializer, ManagerPerformanceReviewSerializer,
    ManagerSkillSerializer, ManagerTaskSerializer, ManagerDocumentSerializer
)
from authentication.models import Manager, Skill
from attendance.models import Attendance
from kpi.models import PerformanceReview
from documents.models import ManagerDocument
from projectmanagement.models import Task

@api_view(['GET'])
def admin_view_manager_profile(request, manager_id):
    try:
        manager = Manager.objects.get(manager_id=manager_id)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)

    # Attendance Data
    attendance_records = Attendance.objects.filter(manager__manager_id=manager.manager_id)
    attendance_reward_points = sum(1 for record in attendance_records if record.status == 'Present')
    attendance_serializer = ManagerAttendanceSerializer(attendance_records, many=True)

    # Performance Reviews
    performance_reviews = PerformanceReview.objects.filter(manager=manager).order_by('-review_date')
    performance_serializer = ManagerPerformanceReviewSerializer(performance_reviews, many=True)

    # Skills
    skills = Skill.objects.filter(manager=manager)
    skill_serializer = ManagerSkillSerializer(skills, many=True)

    # Employee Tasks
    tasks = Task.objects.filter(assigned_to=manager.manager_name, status='completed')
    task_reward_points = sum(1 for task in tasks if task.completion_date and not task.is_late())
    task_serializer = ManagerTaskSerializer(tasks, many=True)

    # Documents (Certificates)
    documents = ManagerDocument.objects.filter(user_id=manager_id)
    document_serializer = ManagerDocumentSerializer(documents, many=True)

    # Calculate Total Reward Points
    total_reward_points = attendance_reward_points + task_reward_points

    response_data = {
        'manager': {
            'manager_id': manager.manager_id,
            'manager_name': manager.manager_name,
            'email': manager.email,
            'department': manager.department,
        },
        'attendance_data': attendance_serializer.data,
        'performance_data': performance_serializer.data,
        'skills': skill_serializer.data,
        'attendance_reward_points': attendance_reward_points,
        'task_reward_points': task_reward_points,
        'total_reward_points': total_reward_points,
        'task_data': task_serializer.data,
        'documents': document_serializer.data,
    }

    return Response(response_data, status=status.HTTP_200_OK)


# List all managers
@api_view(['GET'])
def manager_list(request):
    try:
        managers = Manager.objects.all()  # Get all Manager instances
        serializer = ManagerSerializer(managers, many=True)  # Serialize multiple managers
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # If any exception occurs, return an internal server error with the exception message
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def view_supervisor_profile(request, id):
    try:
        # Attempt to get the Manager instance by ID
        supervisor = Supervisor.objects.get(supervisor_id=id)
    except Supervisor.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "supervisor not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = SupervisorSerializer(supervisor)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def supervisor_list(request):
    try:
        # Query all supervisors
        supervisors = Supervisor.objects.all()

        # If no supervisors found, return an empty list with status 200
        if not supervisors:
            return Response({"message": "No supervisors found."}, status=status.HTTP_200_OK)
        
        # Serialize the supervisor data
        serializer = SupervisorSerializer(supervisors, many=True)

        # Return the serialized data with a 200 OK status
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # If there's any error, return a 500 internal server error
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmployeeSerializer, EmployeeAttendanceSerializer, EmployeePerformanceReviewSerializer,
    EmployeeSkillSerializer, EmployeeTaskSerializer, EmployeeDocumentSerializer
)
from authentication.models import Employee, Skill
from attendance.models import Attendance
from kpi.models import PerformanceReview
from documents.models import Document
from projectmanagement.models import employee_task

@api_view(['GET', 'POST'])
def view_employee_profile(request):
    employee_id = request.session.get('user_id')
    
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Attendance Data
        attendance_records = Attendance.objects.filter(employee_id=employee_id)
        attendance_reward_points = sum(1 for record in attendance_records if record.status == 'Present')
        attendance_serializer = EmployeeAttendanceSerializer(attendance_records, many=True)

        # Performance Reviews
        performance_reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_date')
        performance_serializer = EmployeePerformanceReviewSerializer(performance_reviews, many=True)

        # Skills
        skills = Skill.objects.filter(employee=employee)
        skill_serializer = EmployeeSkillSerializer(skills, many=True)

        # Employee Tasks
        tasks = employee_task.objects.filter(assigned_to=employee.employee_name, emp_taskstatus='completed')
        task_reward_points = sum(1 for task in tasks if task.completion_date and not task.is_late())
        task_serializer = EmployeeTaskSerializer(tasks, many=True)

        # Documents (Certificates)
        documents = Document.objects.filter(user_id=employee_id)
        document_serializer = EmployeeDocumentSerializer(documents, many=True)

        # Calculate Total Reward Points
        total_reward_points = attendance_reward_points + task_reward_points

        response_data = {
            'employee': {
                'employee_id': employee.employee_id,
                'employee_name': employee.employee_name,
                'email': employee.email,
                'department': employee.department,
            },
            'attendance_data': attendance_serializer.data,
            'performance_data': performance_serializer.data,
            'skills': skill_serializer.data,
            'attendance_reward_points': attendance_reward_points,
            'task_reward_points': task_reward_points,
            'total_reward_points': total_reward_points,
            'task_data': task_serializer.data,
            'documents': document_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        if 'skill_submit' in request.data:
            skill_name = request.data.get('skill_name')
            proficiency_level = request.data.get('proficiency_level')

            if skill_name and proficiency_level:
                Skill.objects.create(employee=employee, skill_name=skill_name, proficiency_level=proficiency_level)
                return Response({"message": "Skill added successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Skill name and proficiency level are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'document_submit' in request.data:
            document_serializer = EmployeeDocumentSerializer(data=request.data)
            if document_serializer.is_valid():
                document_serializer.save(user_id=employee_id, email=employee.email)
                return Response({"message": "Document uploaded successfully."}, status=status.HTTP_201_CREATED)
            else:
                return Response(document_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    EmployeeSerializer, EmployeeAttendanceSerializer, EmployeePerformanceReviewSerializer,
    EmployeeSkillSerializer, EmployeeTaskSerializer, EmployeeDocumentSerializer
)
from authentication.models import Employee, Skill
from attendance.models import Attendance
from kpi.models import PerformanceReview
from documents.models import Document
from projectmanagement.models import employee_task

@api_view(['GET'])
def admin_view_employee_profile(request, employee_id):
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Attendance Data
    attendance_records = Attendance.objects.filter(employee__employee_id=employee.employee_id)
    attendance_reward_points = sum(1 for record in attendance_records if record.status == 'Present')
    attendance_serializer = EmployeeAttendanceSerializer(attendance_records, many=True)

    # Performance Reviews
    performance_reviews = PerformanceReview.objects.filter(employee=employee).order_by('-review_date')
    performance_serializer = EmployeePerformanceReviewSerializer(performance_reviews, many=True)

    # Skills
    skills = Skill.objects.filter(employee=employee)
    skill_serializer = EmployeeSkillSerializer(skills, many=True)

    # Employee Tasks
    tasks = employee_task.objects.filter(assigned_to=employee.employee_name, emp_taskstatus='completed')
    task_reward_points = sum(1 for task in tasks if task.completion_date and not task.is_late())
    task_serializer = EmployeeTaskSerializer(tasks, many=True)

    # Documents (Certificates)
    documents = Document.objects.filter(user_id=employee_id)
    document_serializer = EmployeeDocumentSerializer(documents, many=True)

    # Calculate Total Reward Points
    total_reward_points = attendance_reward_points + task_reward_points

    response_data = {
        'employee': {
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'email': employee.email,
            'department': employee.department,
        },
        'attendance_data': attendance_serializer.data,
        'performance_data': performance_serializer.data,
        'skills': skill_serializer.data,
        'attendance_reward_points': attendance_reward_points,
        'task_reward_points': task_reward_points,
        'total_reward_points': total_reward_points,
        'task_data': task_serializer.data,
        'documents': document_serializer.data,
    }

    return Response(response_data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def employee_list(request):
    try:
        # Retrieve all employees from the database
        employees = Employee.objects.all()

        # Serialize the data (many=True because we're passing a queryset)
        serializer = EmployeeSerializer(employees, many=True)

        # Return the serialized employee data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def show_department(request, id):
    try:
        department = Department.objects.get(id=id)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def overall_department(request):
    try:
        # Fetch all department records from the database
        departments = Department.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = DepartmentSerializer(departments, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def show_shift(request, id):
    try:
        shift = Shift.objects.get(id=id)
    except Shift.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ShiftSerializer(shift)
    return Response(serializer.data)

@api_view(['GET'])
def overall_shift(request):
    try:
        # Fetch all department records from the database
        shift = Shift.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = ShiftSerializer(shift, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def show_location(request, id):
    try:
        location = Location.objects.get(id=id)
    except Location.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationSerializer(location)
    return Response(serializer.data)

@api_view(['GET'])
def overall_location(request):
    try:
        # Fetch all department records from the database
        location = Location.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = LocationSerializer(location, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def md_show_shift(request, id):
    try:
        shift = Shift.objects.get(id=id)
    except Shift.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ShiftSerializer(shift)
    return Response(serializer.data)

@api_view(['GET'])
def md_show_overall_shift(request):
    try:
        # Fetch all department records from the database
        shift = Shift.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = ShiftSerializer(shift, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def md_show_location(request, id):
    try:
        location = Location.objects.get(id=id)
    except Location.DoesNotExist:
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = LocationSerializer(location)
    return Response(serializer.data)

@api_view(['GET']) 
def md_show_overall_location(request):
    try:
        # Fetch all department records from the database
        location = Location.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = LocationSerializer(location, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def md_show_department(request, id):
    try:
        department = Department.objects.get(id=id)
        serializer = DepartmentSerializer(department)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Department.DoesNotExist:
        return Response({"error": "Department not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def md_show_overall_department(request):
    try:
        # Fetch all department records from the database
        departments = Department.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = DepartmentSerializer(departments, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Employee, Manager, Supervisor, News, Ticket, Requests, Todo
from .serializers import EmployeeSerializer, ManagerSerializer, SupervisorSerializer, NewsSerializer, TicketSerializer, RequestsSerializer, TodoSerializer

# View all employees
@api_view(['GET'])
def md_employee_list(request):
    try:
        employees = Employee.objects.all()
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View a specific employee's profile
@api_view(['GET'])
def md_view_employee_profile(request, id):
    try:
        employee = get_object_or_404(Employee, employee_id=id)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View all managers
@api_view(['GET'])
def md_manager_list(request):
    try:
        managers = Employee.objects.all()  # Assuming you want to retrieve managers from Employee model
        serializer = EmployeeSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View a specific manager's profile
@api_view(['GET'])
def md_view_manager_profile(request, id):
    try:
        manager = get_object_or_404(Manager, manager_id=id)
        serializer = ManagerSerializer(manager)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View all supervisors
@api_view(['GET'])
def md_supervisor_list(request):
    try:
        supervisors = Supervisor.objects.all()
        serializer = SupervisorSerializer(supervisors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View a specific supervisor's profile
@api_view(['GET'])
def md_view_supervisor_profile(request, id):
    try:
        supervisor = get_object_or_404(Supervisor, supervisor_id=id)
        serializer = SupervisorSerializer(supervisor)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View all news with authentication
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def view_all_news(request):
    # try:
        all_news = News.objects.all().order_by('-date')
        serializer = NewsSerializer(all_news, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View specific news with authentication
# @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# def view_news(request, id):
#     # try:
#         news_item = get_object_or_404(News, id=id)
#         serializer = NewsSerializer(news_item)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View all service tickets with authentication
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def self_all_service(request):
    # try:
        tickets = Ticket.objects.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View specific service ticket with authentication
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def self_service(request, id):
    # try:
        ticket = get_object_or_404(Ticket, id=id)
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View all service requests with authentication
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def self_all_request(request):
    # try:
        all_requests = Requests.objects.all()
        serializer = RequestsSerializer(all_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View specific service request with authentication
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def self_request(request, id):
    # try:
        request_item = get_object_or_404(Requests, id=id)
        serializer = RequestsSerializer(request_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # except Exception as e:
        # return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET', 'POST'])
def supervisor_view_all_request(request,user_id):
    if request.method == 'GET':
        supervisor_id = request.user.id  # Assume the user is authenticated and represents a supervisor
        try:
            supervisor = Supervisor.objects.get(supervisor_id=user_id)
            requests = Requests.objects.filter(supervisor=supervisor)
            serializer = RequestsSerializer(requests, many=True)
            return Response(serializer.data)
        except Supervisor.DoesNotExist:
            return Response({'error': 'Supervisor not found.'}, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        action = request.data.get('action')
        request_id = request.data.get('request_id')
        try:
            request_obj = Requests.objects.get(id=request_id)
            if action == 'Approve':
                request_obj.status = 'Approved'
            elif action == 'Reject':
                request_obj.status = 'Rejected'
            elif action == 'Forward':
                admin = Admin.objects.first()
                if admin:
                    request_obj.supervisor = None
                    request_obj.admin = admin
                    request_obj.status = 'Forwarded'
                else:
                    return Response({'error': 'No admin available to forward the request.'}, status=status.HTTP_400_BAD_REQUEST)
            request_obj.save()
            return Response({'message': f'Request {action} successfully.'}, status=status.HTTP_200_OK)
        except Requests.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

############## HR ALL FUNCTION CODE ####################

@api_view(['GET'])
def hr_dashboard(request):
    if request.user.is_authenticated and request.session.get('role') == 'hr':
        hr_id = request.session.get('user_id')
        try:
            hr = Hr.objects.get(hr_id=hr_id)
            serializer = HrSerializer(hr)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Hr.DoesNotExist:
            return Response({'error': 'hr not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def hr_forgot_password(request):
    email = request.data.get('email')

    try:
        hr = Hr.objects.get(email=email)
        token = generate_reset_token_for_hr(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/admin/hr_reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.,',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
    except Hr.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def hr_reset_password(request, token):
    """
    Reset the user's password using a reset token sent via email.
    """
    # Validate the reset token
    if not validate_reset_token_for_hr(token):
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed to reset the password after token is validated
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        password = serializer.validated_data['password']

        # Get the email associated with the reset token
        email = get_email_from_token_for_hr(token)
        if not email:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user by email
            hr = Hr.objects.get(email=email)

            # Hash the new password before saving
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password and reset the token fields
            hr.password = hashed_password
            hr.reset_token = None  # Clear the reset token
            hr.token_expiration = None  # Clear the token expiration
            hr.save()

            # Return a success response
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Hr.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Add HR
# @api_view(['POST'])
# def add_hr(request):
#     serializer = HrSerializer(data=request.data)

#     if serializer.is_valid():
#         try:
#             raw_password = request.data.get('password')
#             validate_password(raw_password)  # Ensure password meets security standards
#         except ValidationError as e:
#             return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

#         hr = serializer.save()  # This triggers auto-generation of employee_id

#         return Response({
#             "message": "Hr added successfully!",
#             "hr_id": hr.hr_id  # Return generated employee_id in response
#         }, status=status.HTTP_201_CREATED)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# # Update HR
# @api_view(['PUT'])
# def update_hr(request, id):
#     try:
#         hr = Hr.objects.get(hr_id=id)
#     except Hr.DoesNotExist:
#         return Response({"error": "Hr not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = HrSerializer(hr, data=request.data, partial=True)
#     if serializer.is_valid():
#         if 'password' in request.data:
#             raw_password = request.data.get('password')

#             # Validate the password
#             try:
#                 validate_password(raw_password)
#             except ValidationError as e:
#                 return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            

#         serializer.save()
#         return Response(
#             {"message": "Hr updated successfully!", "hr": serializer.data},
#             status=status.HTTP_200_OK
#         )

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def add_hr(request):
    print("Raw request.POST:", dict(request.POST))  # Debug
    print("Raw request.FILES:", dict(request.FILES))  # Debug

    # Copy form data (not files)
    data = request.POST.dict()

    # Handle 'streams' JSON parsing
    try:
        data['streams'] = json.loads(request.POST.get('streams', '{}'))
        print("Parsed streams:", data['streams'])
    except json.JSONDecodeError as e:
        print("Streams parsing error:", str(e))
        return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Add image from request.FILES if it exists
    files = {'hr_image': request.FILES.get('hr_image')} if request.FILES.get('hr_image') else {}

    # Combine and pass to serializer
    serializer = HrSerializer(data={**data, **files})

    if serializer.is_valid():
        try:
            raw_password = data.get('password')
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        hr = serializer.save()
        return Response({
            "message": "HR added successfully!",
            "hr_id": hr.hr_id
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_hr(request, id):
    try:
        hr = Hr.objects.get(hr_id=id)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create mutable copy of request data
    data = request.POST.dict() if request.POST else {}
    files = request.FILES

    # Handle streams separately
    streams_data = request.POST.get('streams')
    if streams_data:
        try:
            data['streams'] = json.loads(streams_data)
        except json.JSONDecodeError as e:
            return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    # Handle password validation if it's being updated
    if 'password' in data and data['password']:
        try:
            validate_password(data['password'])
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

    # Create serializer data combining all fields
    serializer_data = {**data, **files}
    
    # Use partial=True to allow partial updates
    serializer = HrSerializer(hr, data=serializer_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "HR updated successfully!", "hr": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete HR
@api_view(['DELETE'])
def delete_hr(request, id):
    try:
        hr = Hr.objects.get(hr_id=id)
        hr.delete()
        return Response({"message": "Hr deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
# View all Employee Profiles
@api_view(['GET'])
def hr_list(request):
    try:
        # Retrieve all employees from the database
        hr = Hr.objects.all()

        # Serialize the data (many=True because we're passing a queryset)
        serializer = HrSerializer(hr, many=True)

        # Return the serialized employee data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# Update Employee Profile
@api_view(['PUT'])
def update_hr_profile(request, id):
    try:
        # Retrieve the employee object from the database
        hr = get_object_or_404(Hr, hr_id=id)

        # Log the incoming request data for debugging purposes
        print("Incoming request data:", request.data)

        # Serialize the data with the existing employee data
        serializer = HrSerializer(hr, data=request.data, partial=True)

        # Check if the serializer is valid and log errors if any
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        else:
            # Log the validation errors for debugging
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#hrrrrrrrrrr


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Hiring
from .serializers import HiringSerializer

# Get all hiring requests & create a new hiring request
@api_view(['GET', 'POST'])
def hiring_list_create(request):
    if request.method == 'GET':
        hiring = Hiring.objects.all()
        serializer = HiringSerializer(hiring, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        serializer = HiringSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # Simulate sending notification to HR (Replace with actual logic)
            hr_notification = {"message": "New hiring request sent to HR."}
            return Response({"data": serializer.data, "notification": hr_notification}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def update_hiring_status(request, id):
    try:
        hiring = Hiring.objects.get(id=id)
    except Hiring.DoesNotExist:
        return Response({"error": "Hiring request not found"}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get("status")
    
    if new_status not in ["approved", "rejected", "pending"]:
        return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)

    hiring.status = new_status
    hiring.save()

    return Response({"message": f"Hiring status updated to {hiring.get_status_display()}"}, status=status.HTTP_200_OK)


# Get, Update, or Delete a specific hiring request
@api_view(['GET', 'PUT', 'DELETE'])
def hiring_detail(request, id):
    try:
        hiring = Hiring.objects.get(id=id)
    except Hiring.DoesNotExist:
        return Response({"error": "Hiring request not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = HiringSerializer(hiring)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = HiringSerializer(hiring, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        hiring.delete()
        return Response({"message": "Hiring request deleted"}, status=status.HTTP_204_NO_CONTENT)

import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.conf import settings

# Configure Gemini AI API
genai.configure(api_key=settings.GEMINI_API_KEY)

@csrf_exempt
def generate_job_description(request):
    if request.method == "POST":
        data = json.loads(request.body)
        job_title = data.get("job_title", "")
        skills = data.get("skills", "")
        experience = data.get("experience", "")

        prompt = f"Write a professional job description for a {job_title} requiring {experience} years of experience with skills in {skills}."

        try:
            # Use the correct model name
            model = genai.GenerativeModel("gemini-1.5-pro")  # Change this if needed
            response = model.generate_content(prompt)

            if response and hasattr(response, "text"):
                return JsonResponse({"job_description": response.text})
            else:
                return JsonResponse({"error": "No response from Gemini AI"}, status=500)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


# views.py
import google.generativeai as genai
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-pro")

@csrf_exempt
def hr_chatbot(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "")
            response = model.generate_content(message)
            return JsonResponse({"reply": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
    
import os
import tempfile
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.conf import settings
import google.generativeai as genai

# Configure Gemini with your API key
genai.configure(api_key=settings.GEMINI_API_KEY)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def extract_pdf_content(request):
    pdf_file = request.FILES.get("pdf")
    if not pdf_file:
        return Response({"error": "No file uploaded"}, status=400)

    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            for chunk in pdf_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name

        # Upload to Gemini
        uploaded_file = genai.upload_file(temp_path, display_name="Uploaded PDF")

        # Generate content
        model = genai.GenerativeModel("models/gemini-1.5-pro")
        response = model.generate_content(
            [
                "Extract all tables from this PDF and return them as valid HTML table code only (no extra text):",
                uploaded_file
            ],
            stream=False
        )

        # Clean up the temporary file
        os.remove(temp_path)

        return Response({"table": response.text.strip()})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
                        
                        
# View all Employee Profiles
@api_view(['GET'])
def ar_list(request):
    try:
        # Retrieve all employees from the database
        ar = Ar.objects.all()

        # Serialize the data (many=True because we're passing a queryset)
        serializer = ArSerializer(ar, many=True)

        # Return the serialized employee data in the response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def view_ar_by_id(request, id):
    try:
        # Attempt to get the Manager instance by ID
        ar = Ar.objects.get(ar_id=id)
    except Ar.DoesNotExist:
        # Return a 404 response if the Manager with the given ID does not exist
        return Response({"error": "ar not found"}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the Manager instance and return the data in the response
    serializer = ArSerializer(ar)
    return Response(serializer.data, status=status.HTTP_200_OK)    
    
# Update Employee Profile
@api_view(['PUT'])
def update_ar_profile(request, id):
    try:
        # Retrieve the employee object from the database
        ar = get_object_or_404(Ar, ar_id=id)

        # Log the incoming request data for debugging purposes
        print("Incoming request data:", request.data)

        # Serialize the data with the existing employee data
        serializer = ArSerializer(ar, data=request.data, partial=True)

        # Check if the serializer is valid and log errors if any
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        else:
            # Log the validation errors for debugging
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# arrrrrrrrrrrrrrrrrrrr

@api_view(['GET'])
def ar_dashboard(request):
    if request.user.is_authenticated and request.session.get('role') == 'ar':
        ar_id = request.session.get('user_id')
        try:
            ar = Ar.objects.get(ar_id=ar_id)
            serializer = ArSerializer(ar)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ar.DoesNotExist:
            return Response({'error': 'ar not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def ar_forgot_password(request):
    email = request.data.get('email')

    try:
        ar = Hr.objects.get(email=email)
        token = generate_reset_token_for_ar(email)  # Generate a reset token
        if token:
            reset_link = f"http://127.0.0.1:8000/admin/hr_reset_password/{token}/"

            send_mail(
                'Password Reset Request',
                f'Hello,\n\nWe received a request to reset your password. '
                f'Click the link below to reset your password:\n\n{reset_link}\n\n'
                'If you did not request this change, please ignore this email.\n\nBest regards,\nVulturelines Tech Management Private Ltd.,',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return Response({"message": "Password reset link sent to your email."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)
    except Hr.DoesNotExist:
        return Response({"error": "Email not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def ar_reset_password(request, token):
    """
    Reset the user's password using a reset token sent via email.
    """
    # Validate the reset token
    if not validate_reset_token_for_ar(token):
        return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    # Proceed to reset the password after token is validated
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        password = serializer.validated_data['password']

        # Get the email associated with the reset token
        email = get_email_from_token_for_ar(token)
        if not email:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the user by email
            ar = Ar.objects.get(email=email)

            # Hash the new password before saving
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Update the user's password and reset the token fields
            ar.password = hashed_password
            ar.reset_token = None  # Clear the reset token
            ar.token_expiration = None  # Clear the token expiration
            ar.save()

            # Return a success response
            return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        except Ar.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Add HR
@api_view(['POST'])
def add_ar(request):
    serializer = ArSerializer(data=request.data)

    if serializer.is_valid():
        try:
            raw_password = request.data.get('password')
            validate_password(raw_password)  # Ensure password meets security standards
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        ar = serializer.save()  # This triggers auto-generation of employee_id

        return Response({
            "message": "Hr added successfully!",
            "ar_id": ar.ar_id  # Return generated employee_id in response
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Update HR
@api_view(['PUT'])
def update_ar(request, id):
    try:
        ar = Ar.objects.get(ar_id=id)
    except Ar.DoesNotExist:
        return Response({"error": "Ar not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ArSerializer(ar, data=request.data, partial=True)
    if serializer.is_valid():
        if 'password' in request.data:
            raw_password = request.data.get('password')

            # Validate the password
            try:
                validate_password(raw_password)
            except ValidationError as e:
                return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

            

        serializer.save()
        return Response(
            {"message": "Ar updated successfully!", "ar": serializer.data},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Delete HR
@api_view(['DELETE'])
def delete_ar(request, id):
    try:
        ar = Ar.objects.get(ar_id=id)
        ar.delete()
        return Response({"message": "Ar deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Ar.DoesNotExist:
        return Response({"error": "AR not found."}, status=status.HTTP_404_NOT_FOUND)
    
    
#access feature in admin



@api_view(['GET'])
def get_admin_features(request, user_id):
    try:
        admin = get_object_or_404(Admin, user_id=user_id)
        serializer = AdminSerializer(admin)
        return Response({
            'user_id': admin.user_id,
            'features': admin.features
        }, status=status.HTTP_200_OK)
    except Admin.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def update_admin_features(request, user_id):
    try:
        admin = get_object_or_404(Admin, user_id=user_id)
        features = request.data.get('features', [])
        admin.features = features
        admin.save()
        serializer = AdminSerializer(admin)
        return Response({
            'user_id': admin.user_id,
            'features': admin.features
        }, status=status.HTTP_200_OK)
    except Admin.DoesNotExist:
        return Response({'error': 'Admin not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


#check employee is a team leader or not 

from projectmanagement.models import Team

@api_view(['GET'])
def check_team_leader(request):
    try:
        # Retrieve the employee's username from the session
        employee_username = request.session.get('user')
        
        if not employee_username:
            return Response(
                {"success": False, "message": "Employee not found in session."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve the employee object based on their username
        employee = Employee.objects.get(username=employee_username)

        # Check if the employee is a team leader in any team
        is_team_leader = Team.objects.filter(team_leader=employee).exists()

        # Return the result
        return Response(
            {"success": True, "is_team_leader": is_team_leader},
            status=status.HTTP_200_OK
        )

    except Employee.DoesNotExist:
        return Response(
            {"success": False, "message": "Employee not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


#Job Alert Hr Flow 

from .models import JobAlert
from .serializers import JobAlertSerializer

# Create Job Alert
@api_view(['POST'])
def create_job_alert(request, hr_id):  # hr_id from URL

    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = JobAlertSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(hr=hr)  # Assign HR instance
        return Response(
            {"message": "Job Alert created successfully", "data": serializer.data},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Update Job Alert

@api_view(['PUT'])
def update_job_alert(request, job_id):
    try:
        job_alert = JobAlert.objects.get(job_id=job_id)
    except JobAlert.DoesNotExist:
        return Response({"error": "Job Alert not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = JobAlertSerializer(job_alert, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Job Alert updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete Job Alert
@api_view(['DELETE'])
def delete_job_alert(request, job_id):
    try:
        job_alert = JobAlert.objects.get(job_id=job_id)
        job_alert.delete()
        return Response({"message": "Job Alert deleted successfully"}, status=200)
    except JobAlert.DoesNotExist:
        return Response({"error": f"Job Alert with ID '{job_id}' not found."}, status=404)



# Get Job Alerts for a specific HR
@api_view(['GET'])
def get_job_alerts(request, hr_id):
    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found"}, status=status.HTTP_404_NOT_FOUND)

    job_alerts = JobAlert.objects.filter(hr=hr).order_by('-posted')
    serializer = JobAlertSerializer(job_alerts, many=True)
    return Response(serializer.data)



from .models import Candidate
from .serializers import CandidateSerializer

# Create candidate 
@api_view(['POST'])
def create_candidate(request, hr_id):
    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CandidateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(hr=hr)
        return Response({"message": "Candidate created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update candidate
@api_view(['PUT'])
def update_candidate(request, c_id):
    try:
        candidate = Candidate.objects.get(c_id=c_id)
    except Candidate.DoesNotExist:
        return Response({"error": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CandidateSerializer(candidate, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Candidate updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete candidate
@api_view(['DELETE'])
def delete_candidate(request, c_id):
    try:
        candidate = Candidate.objects.get(c_id=c_id)
        candidate.delete()
        return Response({"message": "Candidate deleted successfully"}, status=200)
    except Candidate.DoesNotExist:
        return Response({"error": f"Candidate with ID '{c_id}' not found."}, status=404)


# Get candidate for a specific HR
@api_view(['GET'])
def get_candidates(request, hr_id):
    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({"error": "HR not found"}, status=status.HTTP_404_NOT_FOUND)

    candidates = Candidate.objects.filter(hr=hr).order_by('name')
    serializer = CandidateSerializer(candidates, many=True)
    return Response(serializer.data)

######################## New User VIEWS After the  change flow ###########################################]






from authentication.models import User
from authentication.serializers import UserSerializer,UserDashboardSerializer




logger = logging.getLogger(__name__)
@api_view(['POST'])
def common_users_login(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user_id = serializer.validated_data['user_id']
            password = serializer.validated_data['password'].encode('utf-8')

            # Fallback models and their roles
            user_roles = [
                {'model': SuperAdmin, 'role': 'superadmin', 'id_field': 'user_id'},
                {'model': Manager, 'role': 'manager', 'id_field': 'manager_id'},
                {'model': Admin, 'role': 'admin', 'id_field': 'user_id'},
                {'model': Ar, 'role': 'ar', 'id_field': 'ar_id'},
            ]

            def authenticate_user(user_model, user_id_field, role, user_id):
                try:
                    user = user_model.objects.get(username=username, **{user_id_field: user_id})
                    if bcrypt.checkpw(password, user.password.encode('utf-8')):
                        auto_leave_created = employee_check_and_auto_leave(user)
                        manager_auto_leave_created = manager_check_and_auto_leave(user)
                        hr_auto_leave_created = hr_check_and_auto_leave(user)
                        ar_auto_leave_created = ar_check_and_auto_leave(user)
                        supervisor_auto_leave_created = supervisor_check_and_auto_leave(user)
                        set_session(request, user, role, user_id)
                        Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)
                        return Response({
                            "message": "Login successful",
                            "designation": role,
                            "user_id": user_id,
                            "auto_leave_created": auto_leave_created,
                            "manager_auto_leave_created": manager_auto_leave_created,
                            "supervisor_auto_leave_created": supervisor_auto_leave_created,
                            "hr_auto_leave_created": hr_auto_leave_created,
                            "ar_auto_leave_created": ar_auto_leave_created
                        }, status=status.HTTP_200_OK)
                except user_model.DoesNotExist:
                    return None

            def set_session(request, user, designation, user_id):
                request.session['user'] = user.username
                request.session['user_id'] = user_id
                request.session['designation'] = designation
                request.session['is_authenticated'] = True
                if hasattr(user, 'email'):
                    request.session['email'] = user.email
                request.session.set_expiry(3600)  # 1 hour

            # First check in the main User model
            try:
                user = User.objects.get(username=username, user_id=user_id)
                if bcrypt.checkpw(password, user.password.encode('utf-8')):
                    designation = user.designation  # Use original casing: 'Employee', 'Supervisor', etc.

                    auto_leave_created = employee_check_and_auto_leave(user) if designation == 'Employee' else False
                    manager_auto_leave_created = manager_check_and_auto_leave(user) if designation == 'Manager' else False
                    hr_auto_leave_created = hr_check_and_auto_leave(user) if designation == 'Human Resources' else False
                    ar_auto_leave_created = ar_check_and_auto_leave(user) if designation == 'AR' else False
                    supervisor_auto_leave_created = supervisor_check_and_auto_leave(user) if designation == 'Supervisor' else False

                    set_session(request, user, designation, user_id)
                    Message.objects.filter(receiver_id=user_id, is_delivered=False).update(is_delivered=True)

                    return Response({
                        "message": "Login successful",
                        "designation": designation,
                        "user_id": user_id,
                        "auto_leave_created": auto_leave_created,
                        "manager_auto_leave_created": manager_auto_leave_created,
                        "supervisor_auto_leave_created": supervisor_auto_leave_created,
                        "hr_auto_leave_created": hr_auto_leave_created,
                        "ar_auto_leave_created": ar_auto_leave_created
                    }, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                pass  # fallback to secondary models

            # If not found in User, try other models
            for role_info in user_roles:
                response = authenticate_user(role_info['model'], role_info['id_field'], role_info['role'], user_id)
                if response:
                    return response

            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
def user_details(request):
    try:
        superadmins = SuperAdmin.objects.all()
        admins = Admin.objects.all()
        managers = Manager.objects.all()
        ars = Ar.objects.all()
        
        # Fetch users filtered by designation
        employees = User.objects.filter(designation='Employee')
        supervisors = User.objects.filter(designation='Supervisor')
        hrs = User.objects.filter(designation='Human Resources')

        data = {
            'superadmins' : SuperAdminSerializer(superadmins, many=True).data,
            'admins': AdminSerializer(admins, many=True).data,
            'managers': ManagerSerializer(managers, many=True).data,
            'ars': ArSerializer(ars, many=True).data,
            'employees': UserSerializer(employees, many=True).data,
            'supervisors': UserSerializer(supervisors, many=True).data,
            'hrs': UserSerializer(hrs, many=True).data,
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from projectmanagement.models import Team

@api_view(['GET'])
def verify_team_leader(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)

        if user.designation != 'Employee':
            return Response(
                {"success": False, "message": "User is not an employee."},
                status=status.HTTP_403_FORBIDDEN
            )

        is_team_leader = Team.objects.filter(team_leader=user).exists()

        return Response(
            {"success": True, "is_team_leader": is_team_leader},
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        return Response(
            {"success": False, "message": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"success": False, "error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )



@api_view(['GET'])
def user_list(request):
    try:
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def add_user(request):
    print("Raw request.POST:", dict(request.POST))
    print("Raw request.FILES:", dict(request.FILES))

    data = request.POST.dict()
    try:
        data['streams'] = json.loads(request.POST.get('streams', '{}'))
        print("Parsed streams:", data['streams'])
    except json.JSONDecodeError as e:
        print("Streams parsing error:", str(e))
        return Response({"streams": ["Value must be valid JSON."]}, status=status.HTTP_400_BAD_REQUEST)

    files = {'user_image': request.FILES.get('user_image')} if request.FILES.get('user_image') else {}
    serializer = UserSerializer(data={**data, **files})

    if serializer.is_valid():
        try:
            raw_password = data.get('password')
            validate_password(raw_password)
        except ValidationError as e:
            return Response({"errors": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        return Response({
            "message": "User added successfully!",
            "user_id": user.user_id
        }, status=status.HTTP_201_CREATED)

    print("Serializer errors:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET'])
# def user_employee_dashboard(request, user_id):
#     """
#     Retrieves dashboard data for a user with 'Employee' designation.
#     Uses session-based data, not DRF authentication.
#     """

#     session_user_id = request.session.get('user_id')
#     session_designation = request.session.get('designation')

#     # Validate session
#     if not session_user_id or not session_designation:
#         return Response({'error': 'Session data missing or corrupted'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Validate user ID from session matches requested ID
#         if session_user_id != user_id:
#             return Response({'error': 'You are not authorized to view this user’s dashboard.'}, status=status.HTTP_403_FORBIDDEN)

#         # Get user with "Employee" designation
#         user_obj = User.objects.get(user_id=user_id, designation='Employee')

#         # Get leave balance
#         leave_balance = LeaveBalance.objects.filter(user=user_obj).first()

#         response_data = {
#             'employee': UserSerializer(user_obj).data,
#             'leave_balance': LeaveBalanceSerializer(leave_balance).data if leave_balance else None,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except User.DoesNotExist:
#         return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def user_dashboard(request, user_id):
    """
    Unified dashboard API for Employee, Supervisor, and HR based on user designation.
    Uses session-based auth and returns data accordingly.
    """

    session_user_id = request.session.get('user_id')
    session_designation = request.session.get('designation')

    if not session_user_id or not session_designation:
        return Response({'error': 'Session data missing or corrupted'}, status=status.HTTP_400_BAD_REQUEST)

    if session_user_id != user_id:
        return Response({'error': 'You are not authorized to view this user’s dashboard.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        user_obj = User.objects.get(user_id=user_id)

        if session_designation == 'Employee':
            if user_obj.designation != 'Employee':
                return Response({'error': 'User designation mismatch.'}, status=status.HTTP_400_BAD_REQUEST)

            leave_balance = LeaveBalance.objects.filter(user=user_obj).first()

            response_data = {
                'role': 'Employee',
                'employee': UserDashboardSerializer(user_obj).data,
                'leave_balance': LeaveBalanceSerializer(leave_balance).data if leave_balance else None,
            }

        elif session_designation == 'Supervisor':
            if user_obj.designation != 'Supervisor':
                return Response({'error': 'User designation mismatch.'}, status=status.HTTP_400_BAD_REQUEST)

            # Use SupervisorLeaveBalance model and serializer here
            leave_balance = SupervisorLeaveBalance.objects.filter(user=user_obj).first()

            # Replace with your actual supervisor present days calculation if available
            total_present_days = supervisor_calculate_total_present_days(user_obj.id)  

            response_data = {
                'role': 'Supervisor',
                'supervisor': UserDashboardSerializer(user_obj).data,
                'leave_balance': SupervisorLeaveBalanceSerializer(leave_balance).data if leave_balance else None,
                'total_present_days': total_present_days,
            }

        elif session_designation == 'HR':
            if user_obj.designation != 'HR':
                return Response({'error': 'User designation mismatch.'}, status=status.HTTP_400_BAD_REQUEST)

            # Use HrLeaveBalance model and serializer here
            leave_balance = HrLeaveBalance.objects.filter(user=user_obj).first()

            response_data = {
                'role': 'HR',
                'hr': UserDashboardSerializer(user_obj).data,
                'leave_balance': HrLeaveBalanceSerializer(leave_balance).data if leave_balance else None,
                # Add HR-specific fields if any
            }

        else:
            return Response({'error': 'Invalid designation.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
#Aug 14

@api_view(['GET'])
def get_superadmin_features(request, user_id):
    try:
        superadmin = get_object_or_404(SuperAdmin, user_id=user_id)
        return Response({
            'user_id': superadmin.user_id,
            'features': superadmin.features
        }, status=status.HTTP_200_OK)
    except SuperAdmin.DoesNotExist:
        return Response({'error': 'SuperAdmin not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
def update_superadmin_features(request, user_id):
    try:
        superadmin = get_object_or_404(SuperAdmin, user_id=user_id)
        features = request.data.get('features', [])
        superadmin.features = features
        superadmin.save()
        return Response({
            'user_id': superadmin.user_id,
            'features': superadmin.features
        }, status=status.HTTP_200_OK)
    except SuperAdmin.DoesNotExist:
        return Response({'error': 'SuperAdmin not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)