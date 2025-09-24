from django.conf import settings
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ArApplyNotification, ArLeaveBalance, ArLeaveRequest, ArNotification, HrApplyNotification, HrLeaveBalance, HrLeaveRequest, HrNotification, LeaveRequest, LeaveBalance, Notification, ApplyNotification,UserApplyNotification,UserLateLoginReason,UserLeaveBalance,UserNotification,UserLeaveRequest
from authentication.models import Ar, Employee, Hr,User
from django.shortcuts import get_list_or_404
from .serializers import ArLeaveRequestSerializer, HrLeaveRequestSerializer, LeaveRequestSerializer, LeaveBalanceSerializer, ManagerLeaveRequestSerializer, ManagerLeaveBalanceSerializer, SupervisorLeaveRequestSerializer,UserApplyNotificationSerializer,UserLateLoginReasonSerializer,UserNotificationSerializer,UserLeaveBalanceSerializer,UserLeaveRequestSerializer

# for employee 

@api_view(['POST'])
def apply_leave(request):
    """
    API endpoint to apply for leave for employees.
    """
    try:
        # Extract request data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_type = request.data.get('leave_type')
        leave_proof = request.FILES.get('leave_proof')
        reason = request.data.get('reason')
        user = request.data.get('user')
        user_id = request.data.get('user_id')
        email = request.data.get('email')

        # Validate required fields
        if not (start_date and end_date and leave_type and user_id and user and email):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate leave type
        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response({'error': 'Invalid leave type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the employee
        try:
            employee = Employee.objects.get(employee_id=user_id)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date strings
        start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()

        if start_date_obj > end_date_obj:
            return Response({'error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total leave days (excluding Sundays)
        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        # Fetch or create leave balance for the user
        leave_balance, _ = LeaveBalance.objects.get_or_create(user=user)

        # Check if leave balance is sufficient for the specific leave type
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the leave request without deducting balance
        leave_request = LeaveRequest.objects.create(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            leave_proof=leave_proof,
            user=user,
            user_id=user_id,
            email=email,
            employee=employee,
            status='pending'
        )

        # Create a notification for the leave request
        ApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date_obj} to {end_date_obj} for {leave_type}."
        )

        return Response({
            'message': 'Leave request submitted successfully!',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def leave_history(request):
    user = request.query_params.get('user')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')

    filter_args = {}
    if from_date:
        filter_args['start_date__gte'] = from_date
    if to_date:
        filter_args['end_date__lte'] = to_date
    if status_filter:
        filter_args['status'] = status_filter
    if user:
        filter_args['user'] = user

    leave_requests = LeaveRequest.objects.filter(**filter_args).order_by('-start_date')
    serializer = LeaveRequestSerializer(leave_requests, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

################################################################################################
@api_view(['GET'])
def leave_history_by_id(request, id):
    """
    Retrieve leave request history by user ID.
    """
    try:
        # Fetch leave requests for the given user ID
        leave_requests = get_list_or_404(LeaveRequest, user_id=id)
        
        # Serialize the list of leave requests
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        
        # Return serialized data with HTTP 200 response
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)   


@api_view(['GET'])
def leave_history_list(request):
    try:
        leave_requests = LeaveRequest.objects.all()
        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
###################################################################################################

from django.utils.timezone import now
from datetime import timedelta
from .models import LeaveRequest, LeaveBalance, Notification
from .serializers import LeaveRequestSerializer
  # Assuming this function is defined for email notifications

####################################july 7 ########################################
@api_view(['POST', 'GET'])
def employee_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = LeaveRequest.objects.get(id=leave_id)
        except LeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If the status is already the same, no need to process
        if leave_request.status == status_update:
            return Response({'message': f'Leave request is already {status_update}.'}, status=status.HTTP_200_OK)

        # Calculate leave days only if approving
        leave_days_used = 0
        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            # Fetch or create leave balance
            leave_balance, _ = LeaveBalance.objects.get_or_create(user=leave_request.user)

            # Check and deduct leave balance for the specific leave type
            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave < leave_days_used:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.medical_leave -= leave_days_used
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave < leave_days_used:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.vacation_leave -= leave_days_used
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave < leave_days_used:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.personal_leave -= leave_days_used

            # Update total leave days
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()

        # Update the leave request status
        leave_request.status = status_update
        leave_request.save()

        # Send email notification
        ApplyNotification(
            leave_request.email,
            status_update,
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date,
        )

        # Create a notification
        Notification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request for {leave_request.leave_type} from {leave_request.start_date} to {leave_request.end_date} has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        search_leave_type = request.query_params.get('search_leave_type', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = LeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if search_leave_type:
            leave_requests = leave_requests.filter(leave_type=search_leave_type)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = LeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
@api_view(['DELETE'])
def delete_employee_leave(request, id):
    """
    Delete an employee leave request by ID, with validation for status and user permissions.
    """
    try:
        leave = LeaveRequest.objects.get(id=id)
        
        user_id = request.session.get('user_id')
        role = request.session.get('role')

        if not user_id or not role:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if role == 'employee':
            if leave.user_id != user_id:
                return Response(
                    {"detail": "You can only delete your own leave requests."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if leave.status != 'pending':
                return Response(
                    {"detail": "Only pending leave requests can be deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role != 'admin':
            return Response(
                {"detail": "Only employees or admins can delete leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        leave.delete()

        if role == 'employee':
            Notification.objects.create(
                user='admin',
                date=timezone.now().date(),
                time=timezone.now().time(),
                message=f"Employee {leave.user} deleted their leave request (ID: {id})."
            )

        return Response(
            {"detail": "Employee leave deleted successfully."},
            status=status.HTTP_200_OK
        )
    except LeaveRequest.DoesNotExist:
        return Response(
            {"detail": "Leave request record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
 


@api_view(['POST', 'GET'])
def supervisor_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = SupervisorLeaveRequest.objects.get(id=leave_id)
        except SupervisorLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If the status is already the same, no need to process
        if leave_request.status == status_update:
            return Response({'message': f'Leave request is already {status_update}.'}, status=status.HTTP_200_OK)

        # Calculate leave days only if approving
        leave_days_used = 0
        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            # Fetch or create leave balance
            leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=leave_request.user)

            # Check and deduct leave balance for the specific leave type
            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave < leave_days_used:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.medical_leave -= leave_days_used
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave < leave_days_used:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.vacation_leave -= leave_days_used
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave < leave_days_used:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.personal_leave -= leave_days_used

            # Update total leave days
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()

        # Update the leave request status
        leave_request.status = status_update
        leave_request.save()

        # Send email notification
        send_supervisor_leave_notification(
            leave_request.email,
            status_update,
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date,
        )

        # Create a notification
        SupervisorNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request for {leave_request.leave_type} from {leave_request.start_date} to {leave_request.end_date} has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        search_leave_type = request.query_params.get('search_leave_type', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = SupervisorLeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if search_leave_type:
            leave_requests = leave_requests.filter(leave_type=search_leave_type)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = SupervisorLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_supervisor_leave(request, id):
    """
    Delete a supervisor leave request by ID, with validation for status and user permissions.
    """
    try:
        leave = SupervisorLeaveRequest.objects.get(id=id)
        
        user_id = request.session.get('user_id')
        role = request.session.get('role')

        if not user_id or not role:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if role == 'supervisor':
            if leave.user_id != user_id:
                return Response(
                    {"detail": "You can only delete your own leave requests."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if leave.status != 'pending':
                return Response(
                    {"detail": "Only pending leave requests can be deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role != 'admin':
            return Response(
                {"detail": "Only supervisors or admins can delete leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        leave.delete()

        if role == 'supervisor':
            SupervisorNotification.objects.create(
                user='admin',
                date=timezone.now().date(),
                time=timezone.now().time(),
                message=f"Supervisor {leave.user} deleted their leave request (ID: {id})."
            )

        return Response(
            {"detail": "Supervisor leave deleted successfully."},
            status=status.HTTP_200_OK
        )
    except SupervisorLeaveRequest.DoesNotExist:
        return Response(
            {"detail": "Supervisor leave record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
   


######################################july 7
@api_view(['DELETE'])
def delete_manager_leave(request, id):
    """
    Delete a manager leave request by ID, with validation for status and user permissions.
    """
    try:
        leave = ManagerLeaveRequest.objects.get(id=id)
        
        user_id = request.session.get('user_id')
        role = request.session.get('role')

        if not user_id or not role:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if role == 'manager':
            if leave.user_id != user_id:
                return Response(
                    {"detail": "You can only delete your own leave requests."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if leave.status != 'pending':
                return Response(
                    {"detail": "Only pending leave requests can be deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role != 'admin':
            return Response(
                {"detail": "Only managers or admins can delete leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        leave.delete()

        if role == 'manager':
            ManagerNotification.objects.create(
                user='admin',
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"Manager {leave.user} deleted their leave request (ID: {id})."
            )

        return Response(
            {"detail": "Manager leave deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ManagerLeaveRequest.DoesNotExist:
        return Response(
            {"detail": "Manager leave record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#############################july 7 ##################################
@api_view(['POST', 'GET'])
def manager_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = ManagerLeaveRequest.objects.get(id=leave_id)
        except ManagerLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If the status is already the same, no need to process
        if leave_request.status == status_update:
            return Response({'message': f'Leave request is already {status_update}.'}, status=status.HTTP_200_OK)

        # Calculate leave days only if approving
        leave_days_used = 0
        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            # Fetch or create leave balance
            leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(user=leave_request.user)

            # Check and deduct leave balance for the specific leave type
            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave < leave_days_used:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.medical_leave -= leave_days_used
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave < leave_days_used:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.vacation_leave -= leave_days_used
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave < leave_days_used:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.personal_leave -= leave_days_used

            # Update total leave days
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()

        # Update the leave request status
        leave_request.status = status_update
        leave_request.save()

        # Send email notification
        try:
            send_manager_leave_notification(
                leave_request.email,
                status_update,
                leave_request.leave_type,
                leave_request.start_date,
                leave_request.end_date,
            )
        except Exception as e:
            return Response({'error': f'Failed to send email notification: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create a notification
        ManagerNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request for {leave_request.leave_type} from {leave_request.start_date} to {leave_request.end_date} has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        search_leave_type = request.query_params.get('search_leave_type', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = ManagerLeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if search_leave_type:
            leave_requests = leave_requests.filter(leave_type=search_leave_type)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = ManagerLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['GET'])
def leave_policies(request):
    leave_balances = LeaveBalance.objects.all()
    leave_data = []

    for leave in leave_balances:
        try:
            employee = Employee.objects.get(username=leave.user)
            leave_data.append({
                'id':leave.id,
                'user': employee.employee_name,
                'department': employee.department_name,
                'role': employee.role,
                'leave_balance': {
                    'medical_leave': leave.medical_leave,
                    'vacation_leave': leave.vacation_leave,
                    'personal_leave': leave.personal_leave,
                    'total_leave_days': leave.total_leave_days
                }
            })
        except Employee.DoesNotExist:
            continue

    return Response(leave_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def update_leave_balance(request, user):
    try:
        # Fetch the LeaveBalance object, or create a new one if it doesn't exist
        leave_balance, created = LeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )
        if created:
            message = f"Leave balance for {user} created successfully."
        else:
            message = f"Leave balance for {user} updated successfully."

        # Update leave fields
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        leave_balance.medical_leave = int(medical_leave)
        leave_balance.vacation_leave = int(vacation_leave)
        leave_balance.personal_leave = int(personal_leave)
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance for {user}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def supervisor_leave_policies(request):
    try:
        leave_balances = SupervisorLeaveBalance.objects.all()
        leave_data = []

        for leave in leave_balances:
            try:
                supervisor = Supervisor.objects.get(username=leave.user)
                leave_data.append({
                    'id': leave.id,
                    'user': supervisor.supervisor_name,
                    'department': supervisor.department_name,
                    'role': supervisor.role,
                    'leave_balance': {
                        'medical_leave': leave.medical_leave,
                        'vacation_leave': leave.vacation_leave,
                        'personal_leave': leave.personal_leave,
                        'total_leave_days': leave.total_leave_days
                    }
                })
            except Supervisor.DoesNotExist:
                continue

        return Response(leave_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error fetching leave policies: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
		

@api_view(['POST'])
def update_supervisor_leave_balance(request, user):
    try:
        # Fetch the LeaveBalance object, or create a new one if it doesn't exist
        leave_balance, created = SupervisorLeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )
        if created:
            message = f"Leave balance for {user} created successfully."
        else:
            message = f"Leave balance for {user} updated successfully."

        # Update leave fields
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        leave_balance.medical_leave = int(medical_leave)
        leave_balance.vacation_leave = int(vacation_leave)
        leave_balance.personal_leave = int(personal_leave)
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance for {user}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

################july 7##########################
@api_view(['GET'])
def manager_leave_policies(request):
    """
    Fetch leave balance policies for all managers.
    """
    try:
        leave_balances = ManagerLeaveBalance.objects.all()
        leave_data = []

        for leave in leave_balances:
            try:
                manager = Manager.objects.get(username=leave.user)
                leave_data.append({
                    'id': leave.id,
                    'user': manager.manager_name,
                    'department': manager.department_name,
                    'role': manager.role,
                    'leave_balance': {
                        'medical_leave': leave.medical_leave,
                        'vacation_leave': leave.vacation_leave,
                        'personal_leave': leave.personal_leave,
                        'total_leave_days': leave.total_leave_days
                    }
                })
            except Manager.DoesNotExist:
                continue

        return Response(leave_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error fetching leave policies: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_manager_leave_balance(request, user):
    try:
        # Fetch the LeaveBalance object, or create a new one if it doesn't exist
        leave_balance, created = ManagerLeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )
        if created:
            message = f"Leave balance for {user} created successfully."
        else:
            message = f"Leave balance for {user} updated successfully."

        # Update leave fields
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        leave_balance.medical_leave = int(medical_leave)
        leave_balance.vacation_leave = int(vacation_leave)
        leave_balance.personal_leave = int(personal_leave)
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance for {user}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
###############################################################################################################################
@api_view(['POST', 'GET'])
def employee_leave_status_by_id(request, id):
    try:
        leave_request = LeaveRequest.objects.get(id=id)
    except LeaveRequest.DoesNotExist:
        return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            leave_balance, _ = LeaveBalance.objects.get_or_create(user=leave_request.user)

            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave >= leave_days_used:
                    leave_balance.medical_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave >= leave_days_used:
                    leave_balance.vacation_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave >= leave_days_used:
                    leave_balance.personal_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

            leave_balance.total_leave_days = max(0, leave_balance.total_leave_days - leave_days_used)
            leave_balance.update_total_absent_days(leave_days_used)
            leave_balance.save()

        leave_request.status = status_update
        leave_request.save()
        
        # Send notification email
        send_leave_notification(
            leave_request.email,
            status_update.lower(),
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date,
        )
        leave_request.notification_sent = True
        leave_request.save()

        Notification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data, status=status.HTTP_200_OK)
##########################################################################################################################


from django.core.mail import BadHeaderError
from django.core.mail import send_mail

def send_leave_notification(email, status, leave_type, start_date, end_date):
    subject = f"Leave Request {status.capitalize()}"
    message = (
        f"Dear User,\n\n"
        f"Your leave request for {leave_type} from {start_date} to {end_date} has been {status.lower()}.\n\n"
        f"Thank you for your patience.\n\n"
        f"Best regards,\n"
        f"Your Company"
    )
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Use the DEFAULT_FROM_EMAIL from settings
            [email],
            fail_silently=False,
        )
    except BadHeaderError:
        # Handle bad header errors (e.g., invalid header values)
        print("Invalid header found.")
    except Exception as e:
        # Handle other exceptions (e.g., network issues, server problems)
        print(f"An error occurred: {e}")
        
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from .models import (
    LeaveRequest,
    Manager,
    ManagerLeaveBalance,
    ManagerLeaveRequest,
    ManagerNotification,
    ManagerApplyNotification
)
from django.core.mail import send_mail
from django.conf import settings


@api_view(['GET'])
def employee_leave_calendar(request):
    # Dummy leave events data
    leave_events = {
        "events": [
            {"title": "Medical Leave", "start": "2025-01-01", "end": "2025-01-03"},
            {"title": "Vacation Leave", "start": "2025-01-10", "end": "2025-01-15"},
        ]
    }
    return Response(leave_events, status=status.HTTP_200_OK)

###################################################################################################################
@api_view(['GET'])
def employee_leave_calendar_view_by_id(request, id):
    try:
        # Retrieve the specific approved leave request by ID
        leave_request = LeaveRequest.objects.get(id=id, status='approved')
    except LeaveRequest.DoesNotExist:
        # Return a 404 response if the leave request is not found
        return Response({'error': 'Approved leave request not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Prepare event data
    event_data = {
        'id': leave_request.id,
        'title': str(leave_request.user),  # Adjust if `user` has a specific string representation
        'start': leave_request.start_date.isoformat(),
        'end': leave_request.end_date.isoformat(),
        'description': leave_request.reason,
    }

    # Return the event data
    return Response({'event': event_data}, status=status.HTTP_200_OK)
#####################################################################################################################3



@api_view(['POST'])
def manager_apply_leave(request):
    """
    API endpoint to apply for a manager leave.
    """
    try:
        # Extract request data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_type = request.data.get('leave_type')
        reason = request.data.get('reason')
        user = request.data.get('user')
        user_id = request.data.get('user_id')
        email = request.data.get('email')

        # Validate required fields
        if not (start_date and end_date and leave_type and user_id and user and email):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate leave type
        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response({'error': 'Invalid leave type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the manager
        try:
            manager = Manager.objects.get(manager_id=user_id)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date strings
        try:
            start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use ISO format (e.g., YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date_obj > end_date_obj:
            return Response({'error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total leave days (excluding Sundays)
        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        # Fetch or create leave balance for the user
        leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(user=user)

        # Check if leave balance is sufficient for the specific leave type
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the leave request without deducting balance
        leave_request = ManagerLeaveRequest.objects.create(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            user=user,
            user_id=user_id,
            email=email,
            manager=manager,
            status='pending'
        )

        # Create a notification for the leave request
        ManagerApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date_obj} to {end_date_obj} for {leave_type}."
        )

        return Response({
            'message': 'Leave request submitted successfully!',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def manager_leave_history(request):
    try:
        # Get the authenticated user
        user = request.user
        
        # Extract query parameters
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')
        status_filter = request.query_params.get('status')

        # Build filter arguments
        filter_args = {'user': user}
        if from_date:
            filter_args['start_date__gte'] = from_date
        if to_date:
            filter_args['end_date__lte'] = to_date
        if status_filter:
            filter_args['status'] = status_filter

        # Query the leave requests
        leave_requests = ManagerLeaveRequest.objects.filter(**filter_args).order_by('-start_date')

        # Serialize the leave requests
        serializer = ManagerLeaveRequestSerializer(leave_requests, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#############################################################################################################
@api_view(['GET'])
def manager_leave_history_by_id(request, id):
    """
    Retrieve leave request history by user ID.
    """
    try:
        # Fetch leave requests for the given user ID (without raising 404 error)
        leave_requests = ManagerLeaveRequest.objects.filter(manager__manager_id=id)
        
        # Serialize the list of leave requests
        serializer = ManagerLeaveRequestSerializer(leave_requests, many=True)
        
        # Return serialized data with HTTP 200 response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
		    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_leave_history_list(request):
    try:
        # Retrieve all leave requests for the authenticated user
        leave_requests = ManagerLeaveRequest.objects.filter(user=request.user).order_by('-start_date')
        
        # Serialize the leave requests
        serializer = ManagerLeaveRequestSerializer(leave_requests, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
###############################################################################################################



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_leave_calendar_view(request):
    try:
        # Retrieve all approved leave requests
        local_events = ManagerLeaveRequest.objects.filter(status='approved')

        # Prepare event data for the response
        event_data = [
            {
                'id': event.id,
                'title': str(event.user),  # Adjust if 'user' has a specific string representation
                'start': event.start_date.isoformat(),
                'end': event.end_date.isoformat(),
                'description': event.reason
            }
            for event in local_events
        ]

        # Return the serialized event data
        return Response({'events': event_data}, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors gracefully
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

###############################################################################################################
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_leave_calendar_view_by_id(request, id):
    try:
        # Fetch the specific leave request by ID and ensure it is approved
        leave_request = ManagerLeaveRequest.objects.get(id=id, status='approved')
    except ManagerLeaveRequest.DoesNotExist:
        # Return a 404 response if the leave request is not found
        return Response({'error': 'Approved leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the leave request data
    serializer = ManagerLeaveRequestSerializer(leave_request)

    # Prepare event data for the response
    event_data = {
        'id': leave_request.id,
        'title': str(leave_request.user),  # Customize as needed, e.g., `user.username`
        'start': leave_request.start_date.isoformat(),
        'end': leave_request.end_date.isoformat(),
        'description': leave_request.reason,
    }

    # Return the serialized data along with the event data
    return Response({'event': event_data, 'details': serializer.data}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_leave_calendar_view_list(request):
    try:
        # Retrieve all approved leave requests
        leave_requests = ManagerLeaveRequest.objects.filter(status='approved').order_by('-start_date')
        
        # Prepare event data for calendar view
        event_data = [
            {
                'id': leave.id,
                'title': str(leave.user),  # Adjust as needed, e.g., `user.username`
                'start': leave.start_date.isoformat(),
                'end': leave.end_date.isoformat(),
                'description': leave.reason
            }
            for leave in leave_requests
        ]

        # Return the serialized data and event-specific information
        return Response({'events': event_data}, status=status.HTTP_200_OK)

    except Exception as e:
        # Handle any unexpected errors
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
####################################################################################################################



    
#############################################################################################################
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manager_leave_status_by_id(request, id):
    if request.method == 'GET':
        try:
            leave_request = ManagerLeaveRequest.objects.get(id=id)
        except ManagerLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        leave_data = {
            'id': leave_request.id,
            'start_date': leave_request.start_date,
            'end_date': leave_request.end_date,
            'leave_type': leave_request.leave_type,
            'status': leave_request.status,
            'reason': leave_request.reason,
        }
        return Response(leave_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Extract data from the request
        data = request.data
        status = data.get('status')

        # Validate the provided status
        if status not in ['Approved', 'Rejected']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the leave request object
        try:
            leave_request = ManagerLeaveRequest.objects.get(id=id)
        except ManagerLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Update the leave request status
        leave_request.status = status
        leave_request.save()

        # If the leave is approved, update the leave balance
        if status == 'Approved':
            leave_balance, created = ManagerLeaveBalance.objects.get_or_create(user=leave_request.user)
            leave_balance.total_leave_days -= leave_request.total_days
            leave_balance.save()

        # Send a notification to the manager about the leave status change
        send_manager_leave_notification(
            leave_request.email,
            status.lower(),
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date
        )

        # Create a notification for the user
        ManagerNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request has been {status.lower()}."
        )

        # Serialize and return the leave request data
        serializer = ManagerLeaveRequestSerializer(leave_request)
        return Response({'message': f'Leave request has been {status.lower()}.'}, status=status.HTTP_200_OK)
##########################################################################################################################

# Utility function for sending email
def send_manager_leave_notification(email, status, leave_type, start_date, end_date):
    subject = f"Leave Request {status.capitalize()}"
    message = (
        f"Your leave request for {leave_type} from {start_date} to {end_date} has been {status}.\n"
        "Thank you for your patience.\n\n"
        "Best regards,\n"
        "Your Company"
    )
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import (
    LeaveBalance, ManagerLeaveBalance, Employee, Manager,
    ApplyNotification, ManagerApplyNotification
)



####################################################################################################################
@api_view(['GET'])
def leave_policies_by_id(request, id):
    try:
        # Fetch LeaveBalance using the user's id
        leave_balance = LeaveBalance.objects.get(user__id=id)
        # Fetch the Employee associated with the LeaveBalance
        employee = leave_balance.user  # Assuming LeaveBalance has a ForeignKey to Employee
    except LeaveBalance.DoesNotExist:
        return Response({'error': 'Leave balance not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Generate a link to the employee's details (example: employee detail page)
    employee_detail_url = reverse('employee-detail', args=[employee.id])
    # Prepare leave data for the response
    leave_data = {
        'user': employee.employee_name,
        'department': employee.department_name,
        'role': employee.role,
        'leave_balance': {
            'medical_leave': leave_balance.medical_leave,
            'vacation_leave': leave_balance.vacation_leave,
            'personal_leave': leave_balance.personal_leave,
            'total_leave_days': leave_balance.total_leave_days,
        },
        'employee_detail_link': request.build_absolute_uri(employee_detail_url),
    }

    return Response(leave_data, status=status.HTTP_200_OK)


########################################################################################################################




#########################################################################################################################
@api_view(['GET'])
def manager_leave_policies_by_id(request, id):
    try:
        # Fetch the manager leave balance by user ID
        manager_balance = ManagerLeaveBalance.objects.get(user__id=id)
        # Fetch the corresponding manager details
        manager = Manager.objects.get(username=manager_balance.user)
    except (ManagerLeaveBalance.DoesNotExist, Manager.DoesNotExist):
        return Response({'error': 'Manager or leave balance not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Construct the response data
    leave_data = {
        'user': manager.manager_name,
        'department': manager.department_name,
        'role': manager.role,
        'leave_balance': {
            'total_leave_days': manager_balance.total_leave_days,
        }
    }

    return Response(leave_data, status=status.HTTP_200_OK)
############################################################################################################################





@api_view(['POST'])
def cancel_notification(request, notification_id):
    try:
        notification = get_object_or_404(ApplyNotification, id=notification_id)
        notification.delete()

        return Response({'message': 'Notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def admin_cancel_notification(request, notification_id):
    try:
        notification = get_object_or_404(ApplyNotification, id=notification_id)
        notification.delete()

        return Response({'message': 'Admin notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling admin notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def manager_cancel_notification(request, notification_id):
    try:
        notification = get_object_or_404(ManagerApplyNotification, id=notification_id)
        notification.delete()

        return Response({'message': 'Manager notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling manager notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import (
    Supervisor, SupervisorLeaveBalance, SupervisorLeaveRequest,
    SupervisorApplyNotification, SupervisorNotification
)
from datetime import timedelta

# @api_view(['POST'])
# def supervisor_apply_leave(request):
#     """
#     API to handle supervisor leave application.
#     """
#     start_date = request.data.get('start_date')
#     end_date = request.data.get('end_date')
#     leave_type = request.data.get('leave_type')
#     reason = request.data.get('reason')
#     user = request.data.get('user')
#     user_id = request.data.get('user_id')
#     email = request.data.get('email')

#     supervisor = get_object_or_404(Supervisor, supervisor_id=user_id)

#     start_date_obj = timezone.datetime.fromisoformat(start_date).date()
#     end_date_obj = timezone.datetime.fromisoformat(end_date).date()

#     total_days = (end_date_obj - start_date_obj).days + 1
#     sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
#     leave_days_used = total_days - sundays

#     leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=user)

#     if leave_balance.total_leave_days >= leave_days_used:
#         SupervisorLeaveRequest.objects.create(
#             start_date=start_date_obj,
#             end_date=end_date_obj,
#             leave_type=leave_type,
#             reason=reason,
#             user=user,
#             user_id=user_id,
#             email=email,
#             supervisor=supervisor
#         )
#         leave_balance.total_leave_days -= leave_days_used
#         leave_balance.save()

#         SupervisorApplyNotification.objects.create(
#             user=user,
#             date=timezone.now().date(),
#             time=timezone.localtime(timezone.now()).time(),
#             message=f"Leave requested from {start_date} to {end_date}."
#         )
#         return Response({"message": "Leave request submitted successfully!"}, status=status.HTTP_201_CREATED)
#     else:
#         return Response({"error": "Insufficient leave balance!"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def supervisor_apply_leave(request):
    """
    API endpoint to apply for leave.
    """
    try:
        # Extract request data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_type = request.data.get('leave_type')
        reason = request.data.get('reason')
        user = request.data.get('user')
        user_id = request.data.get('user_id')
        email = request.data.get('email')

        # Validate required fields
        if not (start_date and end_date and leave_type and user_id and user and email):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate leave type
        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response({'error': 'Invalid leave type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the supervisor
        try:
            supervisor = Supervisor.objects.get(supervisor_id=user_id)
        except Supervisor.DoesNotExist:
            return Response({'error': 'Supervisor not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date strings
        start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()

        if start_date_obj > end_date_obj:
            return Response({'error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total leave days (excluding Sundays)
        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        # Fetch or create leave balance for the user
        leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=user)

        # Check if leave balance is sufficient for the specific leave type
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the leave request without deducting balance
        leave_request = SupervisorLeaveRequest.objects.create(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            user=user,
            user_id=user_id,
            email=email,
            supervisor=supervisor,
            status='pending'
        )

        # Create a notification for the leave request
        SupervisorApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date_obj} to {end_date_obj} for {leave_type}."
        )

        return Response({
            'message': 'Leave request submitted successfully!',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def supervisor_leave_history(request):
    """
    API to fetch supervisor leave history with optional filters.
    """
    # Retrieve query parameters
    user = request.query_params.get('user')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')

    # Build filters dynamically
    filters = {}
    if user:
        filters['user__username'] = user  # Assuming 'user' is a ForeignKey field with 'username' lookup
    if from_date:
        filters['start_date__gte'] = from_date
    if to_date:
        filters['end_date__lte'] = to_date
    if status_filter:
        filters['status'] = status_filter

    # Filter and fetch leave requests
    leave_requests = SupervisorLeaveRequest.objects.filter(**filters).order_by('-start_date')

    # Serialize the data
    leave_data = [
        {
            'id': req.id,
            'user': req.user.username if req.user else None,  # Safeguard against missing user
            'start_date': req.start_date.isoformat(),
            'end_date': req.end_date.isoformat(),
            'leave_type': req.leave_type,
            'reason': req.reason,
            'status': req.status,
        }
        for req in leave_requests
    ]

    # Return the response
    return Response(leave_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def supervisor_leave_history_by_id(request, id):
    """
    Retrieve leave request history by user ID.
    """
    try:
        # Fetch leave requests for the given user ID
        leave_requests = get_list_or_404(SupervisorLeaveRequest, supervisor__supervisor_id=id)
        
        # Serialize the list of leave requests
        serializer = SupervisorLeaveRequestSerializer(leave_requests, many=True)
        
        # Return serialized data with HTTP 200 response

    
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

##################################################################################################################
@api_view(['GET'])
def hr_leave_history_by_id(request, id):
    """
    Retrieve leave request history by user ID.
    """
    try:
        # Fetch leave requests for the given user ID
        leave_requests = get_list_or_404(HrLeaveRequest, hr__hr_id=id)
        
        # Serialize the list of leave requests
        serializer = HrLeaveRequestSerializer(leave_requests, many=True)
        
        # Return serialized data with HTTP 200 response

    
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
#############################july7#########################
@api_view(['POST'])
def hr_apply_leave(request):
    """
    API endpoint to apply for leave for HR users.
    """
    try:
        # Extract request data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_type = request.data.get('leave_type')
        reason = request.data.get('reason')
        user = request.data.get('user')
        user_id = request.data.get('user_id')
        email = request.data.get('email')

        # Validate required fields
        if not (start_date and end_date and leave_type and user_id and user and email):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate leave type
        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response({'error': 'Invalid leave type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the HR
        try:
            hr = Hr.objects.get(hr_id=user_id)
        except Hr.DoesNotExist:
            return Response({'error': 'HR not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date strings
        try:
            start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        except ValueError:
            return Response({'error': 'Invalid date format. Use ISO format (e.g., YYYY-MM-DD).'}, status=status.HTTP_400_BAD_REQUEST)

        if start_date_obj > end_date_obj:
            return Response({'error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total leave days (excluding Sundays)
        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        # Fetch or create leave balance for the user
        leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=user)

        # Check if leave balance is sufficient for the specific leave type
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the leave request without deducting balance
        leave_request = HrLeaveRequest.objects.create(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            user=user,
            user_id=user_id,
            email=email,
            hr=hr,
            status='pending'
        )

        # Create a notification for the leave request
        HrApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date_obj} to {end_date_obj} for {leave_type}."
        )

        return Response({
            'message': 'Leave request submitted successfully!',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    
    
@api_view(['GET'])
def supervisor_leave_history_by_list(request):
    """
    API to fetch a list of all supervisor leave requests.
    """
    # Fetch all leave requests
    leave_requests = SupervisorLeaveRequest.objects.all().order_by('-start_date')

    # Check if no records are found
    if not leave_requests.exists():
        return Response({'error': 'No leave requests found.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the data
    serializer = SupervisorLeaveRequestSerializer(leave_requests, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)
##############################################################################################################################

@api_view(['GET'])
def supervisor_leave_calendar_view(request):
    """
    API to fetch approved leave requests for calendar view.
    """
    # Query approved leave requests
    approved_leaves = SupervisorLeaveRequest.objects.filter(status='approved')

    # Construct events data
    events = [
        {
            'id': leave.id,
            'title': str(leave.user),  # User's name or username
            'start': leave.start_date.isoformat(),  # Start date in ISO format
            'end': leave.end_date.isoformat(),      # End date in ISO format
            'description': leave.reason,           # Reason for the leave
        }
        for leave in approved_leaves
    ]

    # Return events as the response
    return Response({'events': events}, status=status.HTTP_200_OK)

##############################################################################################################################
@api_view(['GET'])
def supervisor_leave_calendar_view_by_id(request, id):
    """
    API to fetch approved leave requests for a specific supervisor by ID for calendar view.
    """
    # Filter approved leave requests for the specific supervisor
    approved_leaves = SupervisorLeaveRequest.objects.filter(user__id=id, status='approved')

    # Check if any leave requests exist
    if not approved_leaves.exists():
        return Response({'error': 'No approved leave requests found for this supervisor.'}, status=status.HTTP_404_NOT_FOUND)

    # Construct events data
    events = [
        {
            'id': leave.id,
            'title': str(leave.user),  # User's name or username
            'start': leave.start_date.isoformat(),  # Start date in ISO format
            'end': leave.end_date.isoformat(),      # End date in ISO format
            'description': leave.reason,           # Reason for the leave
        }
        for leave in approved_leaves
    ]

    # Return events as the response
    return Response({'events': events}, status=status.HTTP_200_OK)


@api_view(['GET'])
def supervisor_leave_calendar_view_by_list(request):
    """
    API to fetch all approved leave requests for supervisors for calendar view.
    """
    # Fetch all approved leave requests
    approved_leaves = SupervisorLeaveRequest.objects.filter(status='approved')

    # Check if any approved leave requests exist
    if not approved_leaves.exists():
        return Response({'error': 'No approved leave requests found.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare calendar event data
    events = [
        {
            'id': leave.id,
            'title': str(leave.user),  # User's name or username
            'start': leave.start_date.isoformat(),  # Start date in ISO format
            'end': leave.end_date.isoformat(),      # End date in ISO format
            'description': leave.reason,           # Reason for the leave
        }
        for leave in approved_leaves
    ]

    # Return events as response
    return Response({'events': events}, status=status.HTTP_200_OK)

############################################################################################################################3##



def send_supervisor_leave_notification(email, status, leave_type, start_date, end_date):
    """
    Helper function to send notification email for leave requests.
    """
    subject = f"Leave Request {status.capitalize()}"
    message = (
        f"Your leave request for {leave_type} from {start_date} to {end_date} has been {status.lower()}.\n"
        "Thank you for your patience.\n\n"
        "Best regards,\n"
        "Your Company"
    )
    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SupervisorLeaveBalance, Supervisor, SupervisorApplyNotification



##########################################################################################################################
@api_view(['GET'])
def supervisor_leave_policies_by_id(request, id):
    """
    API to retrieve leave balance for a specific supervisor by ID.
    """
    try:
        # Fetch supervisor leave balance
        supervisor_balance = SupervisorLeaveBalance.objects.get(user__id=id)

        # Fetch corresponding supervisor details
        supervisor = Supervisor.objects.get(username=supervisor_balance.user)

        # Prepare leave data
        leave_data = {
            'user': supervisor.supervisor_name,  # Supervisor's name
            'department': supervisor.department_name,  # Department name
            'role': supervisor.role,  # Role of the supervisor
            'leave_balance': {
                'total_leave_days': supervisor_balance.total_leave_days,
                'medical_leave': supervisor_balance.medical_leave,
                'vacation_leave': supervisor_balance.vacation_leave,
                'personal_leave': supervisor_balance.personal_leave,
            },
            'is_supervisor': True  # Flag indicating this is a supervisor
        }

    except SupervisorLeaveBalance.DoesNotExist:
        # Supervisor leave balance not found
        return Response({'error': 'Supervisor leave balance not found.'}, status=status.HTTP_404_NOT_FOUND)

    except Supervisor.DoesNotExist:
        # Supervisor details not found
        return Response({'error': 'Supervisor details not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Return leave data as response
    return Response({'leave_data': leave_data}, status=status.HTTP_200_OK)





@api_view(['POST'])
def supervisor_cancel_notification(request, notification_id):
    """
    Cancel a supervisor's leave notification.
    """
    try:
        notification = get_object_or_404(SupervisorApplyNotification, id=notification_id)
        notification.delete()
        return Response({'message': 'Notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


############################## hr leave function code ####################################

################july7#############################
@api_view(['GET'])
def hr_leave_policies(request):
    try:
        leave_balances = HrLeaveBalance.objects.all()
        leave_data = []

        for leave in leave_balances:
            try:
                hr = Hr.objects.get(username=leave.user)
                leave_data.append({
                    'id': leave.id,
                    'user': hr.hr_name,
                    'department': hr.department_name,
                    'role': hr.role,
                    'leave_balance': {
                        'medical_leave': leave.medical_leave,
                        'vacation_leave': leave.vacation_leave,
                        'personal_leave': leave.personal_leave,
                        'total_leave_days': leave.total_leave_days
                    }
                })
            except Hr.DoesNotExist:
                continue

        return Response(leave_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error fetching leave policies: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def update_hr_leave_balance(request, user):
    try:
        # Fetch the LeaveBalance object, or create a new one if it doesn't exist
        leave_balance, created = HrLeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )
        if created:
            message = f"Leave balance for {user} created successfully."
        else:
            message = f"Leave balance for {user} updated successfully."

        # Update leave fields
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        leave_balance.medical_leave = int(medical_leave)
        leave_balance.vacation_leave = int(vacation_leave)
        leave_balance.personal_leave = int(personal_leave)
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance for {user}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    
def hr_send_leave_notification(email, status, leave_type, start_date, end_date):
    """
    Sends an email notification to the user regarding their leave status.
    """
    subject = f"Leave Request {status.capitalize()}"
    message = (
        f"Dear User,\n\n"
        f"Your leave request for {leave_type} from {start_date} to {end_date} has been {status.lower()}.\n\n"
        f"Thank you for your patience.\n\n"
        f"Best regards,\n"
        f"Your Company"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except BadHeaderError:
        print("Invalid email header found. Email not sent.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")

#################july 7#################################

@api_view(['POST', 'GET'])
def hr_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = HrLeaveRequest.objects.get(id=leave_id)
        except HrLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If the status is already the same, no need to process
        if leave_request.status == status_update:
            return Response({'message': f'Leave request is already {status_update}.'}, status=status.HTTP_200_OK)

        # Calculate leave days only if approving
        leave_days_used = 0
        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            # Fetch or create leave balance
            leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=leave_request.user)

            # Check and deduct leave balance for the specific leave type
            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave < leave_days_used:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.medical_leave -= leave_days_used
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave < leave_days_used:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.vacation_leave -= leave_days_used
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave < leave_days_used:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.personal_leave -= leave_days_used

            # Update total leave days
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()

        # Update the leave request status
        leave_request.status = status_update
        leave_request.save()

        # Send email notification
        hr_send_leave_notification(
            leave_request.email,
            status_update,
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date,
        )

        # Create a notification
        HrNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request for {leave_request.leave_type} from {leave_request.start_date} to {leave_request.end_date} has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        search_leave_type = request.query_params.get('search_leave_type', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = HrLeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if search_leave_type:
            leave_requests = leave_requests.filter(leave_type=search_leave_type)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = HrLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
#### july7###################

@api_view(['DELETE'])
def delete_hr_leave(request, id):
    """
    Delete an HR leave request by ID, with validation for status and user permissions.
    """
    try:
        leave = HrLeaveRequest.objects.get(id=id)
        
        user_id = request.session.get('user_id')
        role = request.session.get('role')

        if not user_id or not role:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if role == 'hr':
            if leave.user_id != user_id:
                return Response(
                    {"detail": "You can only delete your own leave requests."},
                    status=status.HTTP_403_FORBIDDEN
                )
            if leave.status != 'pending':
                return Response(
                    {"detail": "Only pending leave requests can be deleted."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif role != 'admin':
            return Response(
                {"detail": "Only HR or admins can delete leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        leave.delete()

        if role == 'hr':
            HrNotification.objects.create(
                user='admin',
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"HR {leave.user} deleted their leave request (ID: {id})."
            )

        return Response(
            {"detail": "HR leave deleted successfully."},
            status=status.HTTP_200_OK
        )
    except HrLeaveRequest.DoesNotExist:
        return Response(
            {"detail": "HR leave record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        
        
@api_view(['POST'])
def hr_cancel_notification(request, id):
    """
    Cancel a supervisor's leave notification.
    """
    try:
        notification = get_object_or_404(HrApplyNotification, id=id)
        notification.delete()
        return Response({'message': 'Notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def hr_apply_leave(request):
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    leave_type = request.data.get('leave_type')
    reason = request.data.get('reason')
    user = request.data.get('user')
    user_id = request.data.get('user_id')
    email = request.data.get('email')

    try:
        hr = Hr.objects.get(hr_id=user_id)
    except Hr.DoesNotExist:
        return Response({'error': 'Hr not found.'}, status=status.HTTP_404_NOT_FOUND)

    start_date_obj = timezone.datetime.fromisoformat(start_date).date()
    end_date_obj = timezone.datetime.fromisoformat(end_date).date()

    total_days = (end_date_obj - start_date_obj).days + 1
    sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
    leave_days_used = total_days - sundays

    leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=user)

    if leave_balance.total_leave_days >= leave_days_used:
        leave_request = HrLeaveRequest(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            user=user,
            user_id=user_id,
            email=email,
            hr=hr        
            )
        leave_request.save()

        leave_balance.total_leave_days -= leave_days_used
        leave_balance.save()

        HrApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date} to {end_date}."
        )

        return Response({'message': 'Leave request submitted successfully!'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Insufficient leave balance!'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def hr_leave_history(request):
    user = request.user
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')

    filter_args = {'user': user}
    if from_date:
        filter_args['start_date__gte'] = from_date
    if to_date:
        filter_args['end_date__lte'] = to_date
    if status_filter:
        filter_args['status'] = status_filter

    leave_requests = HrLeaveRequest.objects.filter(**filter_args).order_by('-start_date')
    leave_data = [
        {
            'id': leave.id,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'leave_type': leave.leave_type,
            'status': leave.status,
            'reason': leave.reason,
        }
        for leave in leave_requests
    ]
    return Response(leave_data, status=status.HTTP_200_OK) 


@api_view(['PUT'])
def edit_manager_leave_balance(request, id):
    try:
        # Fetch the LeaveBalance object, or return 404 if not found
        try:
            leave_balance = ManagerLeaveBalance.objects.get(id=id)
        except ManagerLeaveBalance.DoesNotExist:
            return Response({'error': f'Leave balance with ID {id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get updated values (if provided)
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        # Validate numeric values
        try:
            leave_balance.medical_leave = int(medical_leave)
            leave_balance.vacation_leave = int(vacation_leave)
            leave_balance.personal_leave = int(personal_leave)
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recalculate total leave days and save
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': f'Leave balance with ID {id} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance with ID {id}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_manager_leave_balance(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = ManagerLeaveBalance.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Manager leave balance deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ManagerLeaveBalance.DoesNotExist:
        return Response(
            {"detail": "Manager Leave Balance record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def edit_employee_leave_balance(request, id):
    try:
        # Fetch the LeaveBalance object, or return 404 if not found
        try:
            leave_balance = LeaveBalance.objects.get(id=id)
        except LeaveBalance.DoesNotExist:
            return Response({'error': f'Leave balance with ID {id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get updated values (if provided)
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        # Validate numeric values
        try:
            leave_balance.medical_leave = int(medical_leave)
            leave_balance.vacation_leave = int(vacation_leave)
            leave_balance.personal_leave = int(personal_leave)
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recalculate total leave days and save
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': f'Leave balance with ID {id} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance with ID {id}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_employee_leave_balance(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = LeaveBalance.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Employee leave balance deleted successfully."},
            status=status.HTTP_200_OK
        )
    except LeaveBalance.DoesNotExist:
        return Response(
            {"detail": "Employee Leave Balance record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def edit_supervisor_leave_balance(request, id):
    try:
        # Fetch the LeaveBalance object, or return 404 if not found
        try:
            leave_balance = SupervisorLeaveBalance.objects.get(id=id)
        except SupervisorLeaveBalance.DoesNotExist:
            return Response({'error': f'Leave balance with ID {id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get updated values (if provided)
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        # Validate numeric values
        try:
            leave_balance.medical_leave = int(medical_leave)
            leave_balance.vacation_leave = int(vacation_leave)
            leave_balance.personal_leave = int(personal_leave)
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recalculate total leave days and save
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': f'Leave balance with ID {id} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance with ID {id}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_supervisor_leave_balance(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = SupervisorLeaveBalance.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Supervisor leave balance deleted successfully."},
            status=status.HTTP_200_OK
        )
    except SupervisorLeaveBalance.DoesNotExist:
        return Response(
            {"detail": "Supervisor Leave Balance record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
def edit_hr_leave_balance(request, id):
    try:
        # Fetch the LeaveBalance object, or return 404 if not found
        try:
            leave_balance = HrLeaveBalance.objects.get(id=id)
        except HrLeaveBalance.DoesNotExist:
            return Response({'error': f'Leave balance with ID {id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get updated values (if provided)
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        # Validate numeric values
        try:
            leave_balance.medical_leave = int(medical_leave)
            leave_balance.vacation_leave = int(vacation_leave)
            leave_balance.personal_leave = int(personal_leave)
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recalculate total leave days and save
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': f'Leave balance with ID {id} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance with ID {id}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_hr_leave_balance(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = HrLeaveBalance.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Hr leave balance deleted successfully."},
            status=status.HTTP_200_OK
        )
    except HrLeaveBalance.DoesNotExist:
        return Response(
            {"detail": "Hr Leave Balance record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ########## AR LEAVE ###############

@api_view(['GET'])
def ar_leave_policies(request):
    leave_balances = ArLeaveBalance.objects.all()
    leave_data = []

    for leave in leave_balances:
        try:
            ar = Ar.objects.get(username=leave.user)
            leave_data.append({
                'id':leave.id,
                'user': ar.ar_name,
                'department': ar.department_name,
                'role': ar.role,
                'leave_balance': {
                    'medical_leave': leave.medical_leave,
                    'vacation_leave': leave.vacation_leave,
                    'personal_leave': leave.personal_leave,
                    'total_leave_days': leave.total_leave_days
                }
            })
        except Ar.DoesNotExist:
            continue

    return Response(leave_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_ar_leave_balance(request, user):
    try:
        # Fetch the LeaveBalance object, or create a new one if it doesn't exist
        leave_balance, created = ArLeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )
        if created:
            message = f"Leave balance for {user} created successfully."
        else:
            message = f"Leave balance for {user} updated successfully."

        # Update leave fields
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        leave_balance.medical_leave = int(medical_leave)
        leave_balance.vacation_leave = int(vacation_leave)
        leave_balance.personal_leave = int(personal_leave)
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance for {user}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    
    
def ar_send_leave_notification(email, status, leave_type, start_date, end_date):
    """
    Sends an email notification to the user regarding their leave status.
    """
    subject = f"Leave Request {status.capitalize()}"
    message = (
        f"Dear User,\n\n"
        f"Your leave request for {leave_type} from {start_date} to {end_date} has been {status.lower()}.\n\n"
        f"Thank you for your patience.\n\n"
        f"Best regards,\n"
        f"Your Company"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except BadHeaderError:
        print("Invalid email header found. Email not sent.")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")


@api_view(['POST', 'GET']) 
def ar_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = ArLeaveRequest.objects.get(id=leave_id)
        except ArLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(1 for i in range(total_days) if (leave_request.start_date + timedelta(days=i)).weekday() == 6)
            leave_days_used = total_days - sundays

            leave_balance, _ = ArLeaveBalance.objects.get_or_create(user=leave_request.user)

            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave >= leave_days_used:
                    leave_balance.medical_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave >= leave_days_used:
                    leave_balance.vacation_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave >= leave_days_used:
                    leave_balance.personal_leave -= leave_days_used
                else:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

            leave_balance.total_leave_days = max(0, leave_balance.total_leave_days - leave_days_used)
            leave_balance.save()

        leave_request.status = status_update
        leave_request.save()

        # Send email notification
        ar_send_leave_notification(
            leave_request.email,
            status_update.lower(),
            leave_request.leave_type,
            leave_request.start_date,
            leave_request.end_date,
        )

        ArNotification.objects.create(
            user=leave_request.user,
            date=now().date(),
            time=now().time(),
            message=f"Your leave request has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = ArLeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = ArLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
@api_view(['DELETE'])
def delete_ar_leave(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = ArLeaveRequest.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Ar leave deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ArLeaveRequest.DoesNotExist:
        return Response(
            {"detail": "Ar Leave record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )    
        
        
        
@api_view(['POST'])
def ar_cancel_notification(request, id):
    """
    Cancel a supervisor's leave notification.
    """
    try:
        notification = get_object_or_404(ArApplyNotification, id=id)
        notification.delete()
        return Response({'message': 'Notification has been canceled successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'Error canceling notification: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def ar_apply_leave(request):
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    leave_type = request.data.get('leave_type')
    reason = request.data.get('reason')
    user = request.data.get('user')
    user_id = request.data.get('user_id')
    email = request.data.get('email')

    try:
        ar = Ar.objects.get(ar_id=user_id)
    except Ar.DoesNotExist:
        return Response({'error': 'Ar not found.'}, status=status.HTTP_404_NOT_FOUND)

    start_date_obj = timezone.datetime.fromisoformat(start_date).date()
    end_date_obj = timezone.datetime.fromisoformat(end_date).date()

    total_days = (end_date_obj - start_date_obj).days + 1
    sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
    leave_days_used = total_days - sundays

    leave_balance, _ = ArLeaveBalance.objects.get_or_create(user=user)

    if leave_balance.total_leave_days >= leave_days_used:
        leave_request = ArLeaveRequest(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            user=user,
            user_id=user_id,
            email=email,
            ar=ar        
            )
        leave_request.save()

        leave_balance.total_leave_days -= leave_days_used
        leave_balance.save()

        ArApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Leave requested from {start_date} to {end_date}."
        )

        return Response({'message': 'Leave request submitted successfully!'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': 'Insufficient leave balance!'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def ar_leave_history(request):
    user = request.user
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')

    filter_args = {'user': user}
    if from_date:
        filter_args['start_date__gte'] = from_date
    if to_date:
        filter_args['end_date__lte'] = to_date
    if status_filter:
        filter_args['status'] = status_filter

    leave_requests = ArLeaveRequest.objects.filter(**filter_args).order_by('-start_date')
    leave_data = [
        {
            'id': leave.id,
            'start_date': leave.start_date,
            'end_date': leave.end_date,
            'leave_type': leave.leave_type,
            'status': leave.status,
            'reason': leave.reason,
        }
        for leave in leave_requests
    ]
    return Response(leave_data, status=status.HTTP_200_OK) 

@api_view(['PUT'])
def edit_ar_leave_balance(request, id):
    try:
        # Fetch the LeaveBalance object, or return 404 if not found
        try:
            leave_balance = ArLeaveBalance.objects.get(id=id)
        except ArLeaveBalance.DoesNotExist:
            return Response({'error': f'Leave balance with ID {id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get updated values (if provided)
        medical_leave = request.data.get('medical_leave', leave_balance.medical_leave)
        vacation_leave = request.data.get('vacation_leave', leave_balance.vacation_leave)
        personal_leave = request.data.get('personal_leave', leave_balance.personal_leave)

        # Validate numeric values
        try:
            leave_balance.medical_leave = int(medical_leave)
            leave_balance.vacation_leave = int(vacation_leave)
            leave_balance.personal_leave = int(personal_leave)
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Recalculate total leave days and save
        leave_balance.recalculate_total_leave_days()
        leave_balance.save()

        return Response({'message': f'Leave balance with ID {id} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error updating leave balance with ID {id}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
def delete_ar_leave_balance(request, id):
    """
    Delete leave details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        leave = ArLeaveBalance.objects.get(id=id)
        
        # Delete the salary record
        leave.delete()
        return Response(
            {"detail": "Ar leave balance deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ArLeaveBalance.DoesNotExist:
        return Response(
            {"detail": "Ar Leave Balance record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def ar_leave_history_by_id(request, id):
    """
    Retrieve leave request history by user ID.
    """
    try:
        # Fetch leave requests for the given user ID
        leave_requests = get_list_or_404(ArLeaveRequest, ar__ar_id=id)
        
        # Serialize the list of leave requests
        serializer = ArLeaveRequestSerializer(leave_requests, many=True)
        
        # Return serialized data with HTTP 200 response

    
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import SupervisorLeaveRequest, LateloginReason,EmployeeLateLoginReason,HrLateLoginReason,ManagerLateLoginReason
from authentication.models import Supervisor
from .serializers import SupervisorLeaveRequestSerializer, SubmitLateLoginReasonSerializer,SubmitemployeeLateLoginReasonSerializer,SubmitHrLateLoginReasonSerializer,SubmitManagerLateLoginReasonSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def submit_late_login_reason(request):
    try:
        serializer = SubmitLateLoginReasonSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid input: {serializer.errors}")
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_id = serializer.validated_data['leave_id']
        reason_text = serializer.validated_data['reason'].strip()

        # Fetch the leave request
        leave_request = get_object_or_404(SupervisorLeaveRequest, id=leave_id)
        is_auto_leave_condition = leave_request.is_auto_leave or leave_request.reason == "Auto Leave: Late or No Login"
        if not is_auto_leave_condition:
            logger.warning(f"Leave ID {leave_id} is not an auto-leave request.")
            return Response(
                {'error': 'This leave request is not an auto-leave and cannot have a reason submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if supervisor exists
        if not leave_request.supervisor:
            logger.warning(f"No supervisor associated with leave_id={leave_id}")
            return Response(
                {'error': 'No supervisor associated with this leave request.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a reason has already been submitted
        if LateloginReason.objects.filter(leave_request=leave_request).exists():
            logger.warning(f"Reason already submitted for leave_id={leave_id}")
            return Response(
                {'error': 'A reason has already been submitted for this leave.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if submission is on the same day as the leave request
        today = timezone.localdate()
        leave_date = leave_request.start_date
        if today > leave_date:
            logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} after the leave date")
            return Response(
                {'error': 'Late login reasons can only be submitted on the same day as the leave.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if current time is within shift hours
        supervisor = leave_request.supervisor
        shift = supervisor.shift
        if not shift:
            logger.warning(f"No shift assigned to supervisor {supervisor.supervisor_id}")
            return Response(
                {'error': 'No shift assigned to this supervisor.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shift_start_datetime = datetime.combine(leave_date, shift.shift_start_time)
        shift_end_datetime = datetime.combine(leave_date, shift.shift_end_time)

        # Convert to timezone-aware datetimes
        shift_start_datetime = timezone.make_aware(shift_start_datetime, timezone.get_current_timezone())
        shift_end_datetime = timezone.make_aware(shift_end_datetime, timezone.get_current_timezone())

        # If shift ends before it starts (e.g., night shift crossing midnight), adjust end time to next day
        if shift_end_datetime < shift_start_datetime:
            shift_end_datetime += timedelta(days=1)

        current_datetime = timezone.now()

        # Check if current time is within shift hours
        if not (shift_start_datetime <= current_datetime <= shift_end_datetime):
            logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} outside shift hours")
            return Response(
                {'error': 'Late login reasons can only be submitted during shift hours on the same day.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the late login reason
        late_login_reason = LateloginReason.objects.create(
            supervisor=leave_request.supervisor,
            leave_request=leave_request,
            date=leave_request.start_date,
            reason=reason_text,
            status='pending'
        )

        leave_serializer = SupervisorLeaveRequestSerializer(leave_request)
        logger.info(f"Successfully submitted reason for leave_id={leave_id}")
        return Response({
            'message': 'Late login reason submitted successfully.',
            'data': leave_serializer.data
        }, status=status.HTTP_200_OK)

    except SupervisorLeaveRequest.DoesNotExist:
        logger.warning(f"No leave request found for leave_id={leave_id}")
        return Response(
            {'error': 'No leave request found with this ID.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        return Response(
            {'error': 'Invalid leave_id format. Must be an integer.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in submit_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An internal server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def admin_supervisor_late_login_reasons(request):
    try:
        late_login_reasons = LateloginReason.objects.select_related('supervisor', 'leave_request').values(
            'id',
            'supervisor__supervisor_id',
            'supervisor__supervisor_name',
            'date',
            'reason',
            'status',
            'leave_request__leave_type'
        )
        
        if not late_login_reasons:
            logger.warning("No late login reasons found matching the criteria.")
            
        data = {
            'late_login_reasons': [
                {
                    'id': reason['id'],
                    'supervisor_id': reason['supervisor__supervisor_id'],
                    'supervisor_name': reason['supervisor__supervisor_name'] or 'Unknown Supervisor',
                    'date': reason['date'].isoformat(),
                    'reason': reason['reason'] or 'No reason provided',
                    'status': reason['status'],
                    'leave_type': reason['leave_request__leave_type'] or 'N/A'
                } for reason in late_login_reasons
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in admin_supervisor_late_login_reasons: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def approve_late_login_reason(request, reason_id):
    try:
        late_login_reason = get_object_or_404(LateloginReason, id=reason_id)
        leave_request = late_login_reason.leave_request
        
        if late_login_reason.status != 'pending':
            return Response({'error': 'Only pending reasons can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the leave is an auto leave and was approved, restore the deducted leave balance
        if leave_request.is_auto_leave and leave_request.status == 'approved':
            leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=leave_request.user)
            if leave_request.leave_type == 'medical':
                leave_balance.medical_leave += 1
            elif leave_request.leave_type == 'vacation':
                leave_balance.vacation_leave += 1
            elif leave_request.leave_type == 'personal':
                leave_balance.personal_leave += 1
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()
        
        # Update LateLoginReason status
        late_login_reason.status = 'approved'
        late_login_reason.save()
        
        # Mark the associated leave request as rejected (not counted as leave)
        leave_request.status = 'rejected'
        leave_request.save()
        
        # Send notification
        SupervisorNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your late login reason for {leave_request.start_date} has been approved. The associated leave has been rejected."
        )

        logger.info(f"Approved late login reason ID: {reason_id}, set leave ID: {leave_request.id} to rejected")
        return Response({'message': 'Reason approved successfully. Associated leave marked as rejected.'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in approve_late_login_reason: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import transaction



@api_view(['POST'])
def reject_late_login_reason(request, reason_id):
    try:
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            late_login_reason = get_object_or_404(LateloginReason, id=reason_id)
            leave_request = late_login_reason.leave_request

            if late_login_reason.status != 'pending':
                return Response(
                    {'error': 'Only pending reasons can be rejected.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the leave is an auto leave
            if leave_request.is_auto_leave:
                # For auto leaves, do not deduct balance again as it was already deducted in supervisor_check_and_auto_leave
                logger.info(f"Rejected late login reason ID: {reason_id} for auto leave ID: {leave_request.id}. No additional balance deduction.")
            else:
                # For non-auto leaves, proceed with balance deduction if the leave is approved
                if leave_request.status == 'approved':
                    total_days = (leave_request.end_date - leave_request.start_date).days + 1
                    sundays = sum(
                        1 for i in range(total_days)
                        if (leave_request.start_date + timedelta(days=i)).weekday() == 6
                    )
                    leave_days_used = total_days - sundays

                    leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=leave_request.user)

                    # Check if sufficient balance exists before proceeding
                    if leave_request.leave_type == 'medical':
                        if leave_balance.medical_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient medical leave balance. Required: {leave_days_used}, Available: {leave_balance.medical_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.medical_leave -= leave_days_used
                    elif leave_request.leave_type == 'vacation':
                        if leave_balance.vacation_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient vacation leave balance. Required: {leave_days_used}, Available: {leave_balance.vacation_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.vacation_leave -= leave_days_used
                    elif leave_request.leave_type == 'personal':
                        if leave_balance.personal_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient personal leave balance. Required: {leave_days_used}, Available: {leave_balance.personal_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.personal_leave -= leave_days_used

                    # Update leave balance
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

            # Update LateLoginReason status
            late_login_reason.status = 'rejected'
            late_login_reason.save()

            # Send notification
            SupervisorNotification.objects.create(
                user=leave_request.user,
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"Your late login reason for {leave_request.start_date} has been rejected. The associated leave remains approved and your leave balance has been updated."
            )

            logger.info(f"Rejected late login reason ID: {reason_id}, leave ID: {leave_request.id} remains approved")
            return Response(
                {'message': 'Reason rejected successfully. Associated leave remains approved.'},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        logger.error(f"Error in reject_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    



@api_view(['PUT'])
def edit_supervisor_leave_request(request, leave_id):
    try:
        leave_request = SupervisorLeaveRequest.objects.get(id=leave_id)
        
        if leave_request.status != 'pending':
            return Response(
                {"error": "Only pending leave requests can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.session.get('user_id')
        if leave_request.user_id != user_id:
            return Response(
                {"error": "You can only edit your own leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        start_date = request.data.get('start_date', leave_request.start_date)
        end_date = request.data.get('end_date', leave_request.end_date)
        leave_type = request.data.get('leave_type', leave_request.leave_type)
        reason = request.data.get('reason', leave_request.reason)

        if not (start_date and end_date and leave_type and reason):
            return Response(
                {"error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response(
                {"error": "Invalid leave type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()

        if start_date_obj > end_date_obj:
            return Response(
                {"error": "End date must be after start date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        leave_balance, _ = SupervisorLeaveBalance.objects.get_or_create(user=leave_request.user)
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response(
                {"error": "Insufficient medical leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response(
                {"error": "Insufficient vacation leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response(
                {"error": "Insufficient personal leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.start_date = start_date_obj
        leave_request.end_date = end_date_obj
        leave_request.leave_type = leave_type
        leave_request.reason = reason
        leave_request.save()

        SupervisorNotification.objects.create(
            user='admin',
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Supervisor {leave_request.user} updated their pending leave request (ID: {leave_id}) for {leave_type} from {start_date_obj} to {end_date_obj}."
        )

        return Response(
            {"message": "Leave request updated successfully."},
            status=status.HTTP_200_OK
        )

    except SupervisorLeaveRequest.DoesNotExist:
        return Response(
            {"error": "Leave request not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

########################################july 7################################

@api_view(['POST'])
def submit_hr_late_login_reason(request):
    """
    API endpoint to submit a late login reason for an HR auto-leave request.
    """
    try:
        with transaction.atomic():  # Ensure atomic database operations
            serializer = SubmitHrLateLoginReasonSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid input: {serializer.errors}")
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            leave_id = serializer.validated_data['leave_id']
            reason_text = serializer.validated_data['reason'].strip()

            logger.debug(f"Received data - leave_id: {leave_id}, reason: {reason_text}")

            # Fetch the leave request
            leave_request = get_object_or_404(HrLeaveRequest, id=leave_id)
            logger.debug(f"Fetched leave_request: {leave_request.id}, is_auto_leave: {leave_request.is_auto_leave}, reason: {leave_request.reason}")

            is_auto_leave_condition = leave_request.is_auto_leave or leave_request.reason == "Auto Leave: Late or No Login"
            if not is_auto_leave_condition:
                logger.warning(f"Leave ID {leave_id} is not an auto-leave request.")
                return Response(
                    {'error': 'This leave request is not an auto-leave and cannot have a reason submitted.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if HR exists
            if not leave_request.hr:
                logger.warning(f"No HR associated with leave_id={leave_id}")
                return Response(
                    {'error': 'No HR associated with this leave request.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if a reason has already been submitted
            if HrLateLoginReason.objects.filter(leave_request=leave_request).exists():
                logger.warning(f"Reason already submitted for leave_id={leave_id}")
                return Response(
                    {'error': 'A reason has already been submitted for this leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if submission is on the same day as the leave request
            today = timezone.localdate()
            leave_date = leave_request.start_date
            logger.debug(f"Today: {today}, Leave date: {leave_date}")
            if today > leave_date:
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} after the leave date")
                return Response(
                    {'error': 'Late login reasons can only be submitted on the same day as the leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if current time is within shift hours
            hr = leave_request.hr
            shift = getattr(hr, 'shift', None)  # Handle case where shift might be None
            if not shift:
                logger.warning(f"No shift assigned to HR {hr.hr_id if hr else 'Unknown'}")
                return Response(
                    {'error': 'No shift assigned to this HR.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shift_start_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_start_time),
                timezone.get_current_timezone()
            )
            shift_end_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_end_time),
                timezone.get_current_timezone()
            )

            # If shift ends before it starts (e.g., night shift crossing midnight), adjust end time to next day
            if shift_end_datetime < shift_start_datetime:
                shift_end_datetime += timezone.timedelta(days=1)

            current_datetime = timezone.now()
            logger.debug(f"Shift: {shift_start_datetime} to {shift_end_datetime}, Current: {current_datetime}")

            # Check if current time is within shift hours
            if not (shift_start_datetime <= current_datetime <= shift_end_datetime):
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} outside shift hours")
                return Response(
                    {'error': 'Late login reasons can only be submitted during shift hours on the same day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the late login reason
            late_login_reason = HrLateLoginReason.objects.create(
                hr=leave_request.hr,
                leave_request=leave_request,
                date=leave_request.start_date,
                reason=reason_text,
                status='pending'
            )

            leave_serializer = HrLeaveRequestSerializer(leave_request)
            logger.info(f"Successfully submitted reason for leave_id={leave_id}")
            return Response({
                'message': 'Late login reason submitted successfully.',
                'data': leave_serializer.data
            }, status=status.HTTP_200_OK)

    except HrLeaveRequest.DoesNotExist:
        logger.warning(f"No leave request found for leave_id={leave_id}")
        return Response(
            {'error': 'No leave request found with this ID.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as ve:
        logger.error(f"ValueError in submit_hr_late_login_reason: {str(ve)}", exc_info=True)
        return Response(
            {'error': 'Invalid leave_id format. Must be an integer.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in submit_hr_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An internal server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['GET'])
def admin_hr_late_login_reasons(request):
    """
    API endpoint to retrieve all HR late login reasons for admin review.
    """
    try:
        late_login_reasons = HrLateLoginReason.objects.select_related('hr', 'leave_request').values(
            'id',
            'hr__hr_id',
            'hr__hr_name',
            'date',
            'reason',
            'status',
            'leave_request__leave_type'
        )
        
        if not late_login_reasons.exists():
            logger.warning("No late login reasons found matching the criteria.")
            data = {'late_login_reasons': []}
        else:
            data = {
                'late_login_reasons': [
                    {
                        'id': reason['id'],
                        'hr_id': reason['hr__hr_id'],
                        'hr_name': reason['hr__hr_name'] or 'Unknown HR',
                        'date': reason['date'].isoformat(),
                        'reason': reason['reason'] or 'No reason provided',
                        'status': reason['status'],
                        'leave_type': reason['leave_request__leave_type'] or 'N/A'
                    } for reason in late_login_reasons
                ]
            }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in admin_hr_late_login_reasons: {str(e)}", exc_info=True)
        return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def approve_hr_late_login_reason(request, reason_id):
    """
    API endpoint to approve an HR late login reason.
    """
    try:
        late_login_reason = get_object_or_404(HrLateLoginReason, id=reason_id)
        leave_request = late_login_reason.leave_request
        
        if late_login_reason.status != 'pending':
            return Response({'error': 'Only pending reasons can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the leave is an auto leave and was approved, restore the deducted leave balance
        if leave_request.is_auto_leave and leave_request.status == 'approved':
            leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=leave_request.user)
            if leave_request.leave_type == 'medical':
                leave_balance.medical_leave += 1
            elif leave_request.leave_type == 'vacation':
                leave_balance.vacation_leave += 1
            elif leave_request.leave_type == 'personal':
                leave_balance.personal_leave += 1
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()
        
        # Update HrLateLoginReason status
        late_login_reason.status = 'approved'
        late_login_reason.save()
        
        # Mark the associated leave request as rejected (not counted as leave)
        leave_request.status = 'rejected'
        leave_request.save()
        
        # Send notification
        HrNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your late login reason for {leave_request.start_date} has been approved. The associated leave has been rejected."
        )

        logger.info(f"Approved late login reason ID: {reason_id}, set leave ID: {leave_request.id} to rejected")
        return Response({'message': 'Reason approved successfully. Associated leave marked as rejected.'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in approve_hr_late_login_reason: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reject_hr_late_login_reason(request, reason_id):
    """
    API endpoint to reject an HR late login reason.
    """
    try:
        # Use a transaction to ensure atomicity
        with transaction.atomic():
            late_login_reason = get_object_or_404(HrLateLoginReason, id=reason_id)
            leave_request = late_login_reason.late_request

            if late_login_reason.status != 'pending':
                return Response(
                    {'error': 'Only pending reasons can be rejected.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the leave is an auto leave
            if leave_request.is_auto_leave:
                # For auto leaves, do not deduct balance again as it was already deducted
                logger.info(f"Rejected late login reason ID: {reason_id} for auto leave ID: {leave_request.id}. No additional balance deduction.")
            else:
                # For non-auto leaves, proceed with balance deduction if the leave is approved
                if leave_request.status == 'approved':
                    total_days = (leave_request.end_date - leave_request.start_date).days + 1
                    sundays = sum(
                        1 for i in range(total_days)
                        if (leave_request.start_date + timedelta(days=i)).weekday() == 6
                    )
                    leave_days_used = total_days - sundays

                    leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=leave_request.user)

                    # Check if sufficient balance exists before proceeding
                    if leave_request.leave_type == 'medical':
                        if leave_balance.medical_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient medical leave balance. Required: {leave_days_used}, Available: {leave_balance.medical_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.medical_leave -= leave_days_used
                    elif leave_request.leave_type == 'vacation':
                        if leave_balance.vacation_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient vacation leave balance. Required: {leave_days_used}, Available: {leave_balance.vacation_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.vacation_leave -= leave_days_used
                    elif leave_request.leave_type == 'personal':
                        if leave_balance.personal_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient personal leave balance. Required: {leave_days_used}, Available: {leave_balance.personal_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.personal_leave -= leave_days_used

                    # Update leave balance
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

            # Update HrLateLoginReason status
            late_login_reason.status = 'rejected'
            late_login_reason.save()

            # Send notification
            HrNotification.objects.create(
                user=leave_request.user,
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"Your late login reason for {leave_request.start_date} has been rejected. The associated leave remains approved and your leave balance has been updated."
            )

            logger.info(f"Rejected late login reason ID: {reason_id}, leave ID: {leave_request.id} remains approved")
            return Response(
                {'message': 'Reason rejected successfully. Associated leave remains approved.'},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        logger.error(f"Error in reject_hr_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def edit_hr_leave_request(request, leave_id):
    """
    API endpoint to edit a pending HR leave request by ID.
    """
    try:
        leave_request = HrLeaveRequest.objects.get(id=leave_id)
        
        if leave_request.status != 'pending':
            return Response(
                {"error": "Only pending leave requests can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.session.get('user_id')
        if leave_request.user_id != user_id:
            return Response(
                {"error": "You can only edit your own leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        start_date = request.data.get('start_date', leave_request.start_date)
        end_date = request.data.get('end_date', leave_request.end_date)
        leave_type = request.data.get('leave_type', leave_request.leave_type)
        reason = request.data.get('reason', leave_request.reason)

        if not (start_date and end_date and leave_type and reason):
            return Response(
                {"error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response(
                {"error": "Invalid leave type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use ISO format (e.g., YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date_obj > end_date_obj:
            return Response(
                {"error": "End date must be after start date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        leave_balance, _ = HrLeaveBalance.objects.get_or_create(user=leave_request.user)
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response(
                {"error": "Insufficient medical leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response(
                {"error": "Insufficient vacation leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response(
                {"error": "Insufficient personal leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.start_date = start_date_obj
        leave_request.end_date = end_date_obj
        leave_request.leave_type = leave_type
        leave_request.reason = reason
        leave_request.save()

        HrNotification.objects.create(
            user='admin',
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"HR {leave_request.user} updated their pending leave request (ID: {leave_id}) for {leave_type} from {start_date_obj} to {end_date_obj}."
        )

        return Response(
            {"message": "Leave request updated successfully."},
            status=status.HTTP_200_OK
        )

    except HrLeaveRequest.DoesNotExist:
        return Response(
            {"error": "Leave request not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    


@api_view(['POST'])
def submit_manager_late_login_reason(request):
    """
    API endpoint to submit a late login reason for a manager auto-leave request.
    """
    try:
        with transaction.atomic():  # Ensure atomic database operations
            serializer = SubmitManagerLateLoginReasonSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid input: {serializer.errors}")
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            leave_id = serializer.validated_data['leave_id']
            reason_text = serializer.validated_data['reason'].strip()

            logger.debug(f"Received data - leave_id: {leave_id}, reason: {reason_text}")

            # Fetch the leave request
            leave_request = get_object_or_404(ManagerLeaveRequest, id=leave_id)
            logger.debug(f"Fetched leave_request: {leave_request.id}, is_auto_leave: {leave_request.is_auto_leave}, reason: {leave_request.reason}")

            is_auto_leave_condition = leave_request.is_auto_leave or leave_request.reason == "Auto Leave: Late or No Login"
            if not is_auto_leave_condition:
                logger.warning(f"Leave ID {leave_id} is not an auto-leave request.")
                return Response(
                    {'error': 'This leave request is not an auto-leave and cannot have a reason submitted.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if Manager exists
            if not leave_request.manager:
                logger.warning(f"No Manager associated with leave_id={leave_id}")
                return Response(
                    {'error': 'No Manager associated with this leave request.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if a reason has already been submitted
            if ManagerLateLoginReason.objects.filter(leave_request=leave_request).exists():
                logger.warning(f"Reason already submitted for leave_id={leave_id}")
                return Response(
                    {'error': 'A reason has already been submitted for this leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if submission is on the same day as the leave request
            today = timezone.localdate()
            leave_date = leave_request.start_date
            logger.debug(f"Today: {today}, Leave date: {leave_date}")
            if today > leave_date:
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} after the leave date")
                return Response(
                    {'error': 'Late login reasons can only be submitted on the same day as the leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if current time is within shift hours
            manager = leave_request.manager
            shift = getattr(manager, 'shift', None)  # Handle case where shift might be None
            if not shift:
                logger.warning(f"No shift assigned to Manager {manager.manager_id if manager else 'Unknown'}")
                return Response(
                    {'error': 'No shift assigned to this Manager.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shift_start_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_start_time),
                timezone.get_current_timezone()
            )
            shift_end_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_end_time),
                timezone.get_current_timezone()
            )

            # If shift ends before it starts (e.g., night shift crossing midnight), adjust end time to next day
            if shift_end_datetime < shift_start_datetime:
                shift_end_datetime += timezone.timedelta(days=1)

            current_datetime = timezone.now()
            logger.debug(f"Shift: {shift_start_datetime} to {shift_end_datetime}, Current: {current_datetime}")

            # Check if current time is within shift hours
            if not (shift_start_datetime <= current_datetime <= shift_end_datetime):
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} outside shift hours")
                return Response(
                    {'error': 'Late login reasons can only be submitted during shift hours on the same day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the late login reason
            late_login_reason = ManagerLateLoginReason.objects.create(
                manager=leave_request.manager,
                leave_request=leave_request,
                date=leave_request.start_date,
                reason=reason_text,
                status='pending'
            )

            leave_serializer = ManagerLeaveRequestSerializer(leave_request)
            logger.info(f"Successfully submitted reason for leave_id={leave_id}")
            return Response({
                'message': 'Late login reason submitted successfully.',
                'data': leave_serializer.data
            }, status=status.HTTP_200_OK)

    except ManagerLeaveRequest.DoesNotExist:
        logger.warning(f"No leave request found for leave_id={leave_id}")
        return Response(
            {'error': 'No leave request found with this ID.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as ve:
        logger.error(f"ValueError in submit_manager_late_login_reason: {str(ve)}", exc_info=True)
        return Response(
            {'error': 'Invalid leave_id format. Must be an integer.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in submit_manager_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An internal server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    


@api_view(['GET'])
def admin_manager_late_login_reasons(request):
    """
    API endpoint to retrieve all Manager late login reasons for admin review.
    """
    try:
        late_login_reasons = ManagerLateLoginReason.objects.select_related('manager', 'leave_request').values(
            'id',
            'manager__manager_id',
            'manager__manager_name',
            'date',
            'reason',
            'status',
            'leave_request__leave_type'
        )
        
        if not late_login_reasons.exists():
            logger.warning("No late login reasons found matching the criteria.")
            data = {'late_login_reasons': []}
        else:
            data = {
                'late_login_reasons': [
                    {
                        'id': reason['id'],
                        'manager_id': reason['manager__manager_id'],
                        'manager_name': reason['manager__manager_name'] or 'Unknown Manager',
                        'date': reason['date'].isoformat(),
                        'reason': reason['reason'] or 'No reason provided',
                        'status': reason['status'],
                        'leave_type': reason['leave_request__leave_type'] or 'N/A'
                    } for reason in late_login_reasons
                ]
            }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in admin_manager_late_login_reasons: {str(e)}", exc_info=True)
        return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])
def approve_manager_late_login_reason(request, reason_id):
    """
    API endpoint to approve a Manager late login reason.
    """
    try:
        late_login_reason = get_object_or_404(ManagerLateLoginReason, id=reason_id)
        leave_request = late_login_reason.leave_request
        
        if late_login_reason.status != 'pending':
            return Response({'error': 'Only pending reasons can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the leave is an auto leave and was approved, restore the deducted leave balance
        if leave_request.is_auto_leave and leave_request.status == 'approved':
            leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(user=leave_request.user)
            if leave_request.leave_type == 'medical':
                leave_balance.medical_leave += 1
            elif leave_request.leave_type == 'vacation':
                leave_balance.vacation_leave += 1
            elif leave_request.leave_type == 'personal':
                leave_balance.personal_leave += 1
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()
        
        # Update ManagerLateLoginReason status
        late_login_reason.status = 'approved'
        late_login_reason.save()
        
        # Mark the associated leave request as rejected (not counted as leave)
        leave_request.status = 'rejected'
        leave_request.save()
        
        # Send notification
        ManagerNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your late login reason for {leave_request.start_date} has been approved. The associated leave has been rejected."
        )

        logger.info(f"Approved late login reason ID: {reason_id}, set leave ID: {leave_request.id} to rejected")
        return Response({'message': 'Reason approved successfully. Associated leave marked as rejected.'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in approve_manager_late_login_reason: {str(e)}", exc_info=True)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@api_view(['POST'])
def reject_manager_late_login_reason(request, reason_id):
    """
    API endpoint to reject a Manager late login reason.
    """
    try:
        with transaction.atomic():
            late_login_reason = get_object_or_404(ManagerLateLoginReason, id=reason_id)
            leave_request = late_login_reason.leave_request

            if late_login_reason.status != 'pending':
                return Response(
                    {'error': 'Only pending reasons can be rejected.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the leave is an auto leave
            if leave_request.is_auto_leave:
                # For auto leaves, do not deduct balance again as it was already deducted
                logger.info(f"Rejected late login reason ID: {reason_id} for auto leave ID: {leave_request.id}. No additional balance deduction.")
            else:
                # For non-auto leaves, proceed with balance deduction if the leave is approved
                if leave_request.status == 'approved':
                    total_days = (leave_request.end_date - leave_request.start_date).days + 1
                    sundays = sum(
                        1 for i in range(total_days)
                        if (leave_request.start_date + timedelta(days=i)).weekday() == 6
                    )
                    leave_days_used = total_days - sundays

                    leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(user=leave_request.user)

                    # Check if sufficient balance exists before proceeding
                    if leave_request.leave_type == 'medical':
                        if leave_balance.medical_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient medical leave balance. Required: {leave_days_used}, Available: {leave_balance.medical_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.medical_leave -= leave_days_used
                    elif leave_request.leave_type == 'vacation':
                        if leave_balance.vacation_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient vacation leave balance. Required: {leave_days_used}, Available: {leave_balance.vacation_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.vacation_leave -= leave_days_used
                    elif leave_request.leave_type == 'personal':
                        if leave_balance.personal_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient personal leave balance. Required: {leave_days_used}, Available: {leave_balance.personal_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.personal_leave -= leave_days_used

                    # Update leave balance
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

            # Update ManagerLateLoginReason status
            late_login_reason.status = 'rejected'
            late_login_reason.save()

            # Send notification
            ManagerNotification.objects.create(
                user=leave_request.user,
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"Your late login reason for {leave_request.start_date} has been rejected. The associated leave remains approved and your leave balance has been updated."
            )

            logger.info(f"Rejected late login reason ID: {reason_id}, leave ID: {leave_request.id} remains approved")
            return Response(
                {'message': 'Reason rejected successfully. Associated leave remains approved.'},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        logger.error(f"Error in reject_manager_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['PUT'])
def edit_manager_leave_request(request, leave_id):
    """
    API endpoint to edit a pending Manager leave request by ID.
    """
    try:
        leave_request = ManagerLeaveRequest.objects.get(id=leave_id)
        
        if leave_request.status != 'pending':
            return Response(
                {"error": "Only pending leave requests can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.session.get('user_id')
        if leave_request.user_id != user_id:
            return Response(
                {"error": "You can only edit your own leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        start_date = request.data.get('start_date', leave_request.start_date)
        end_date = request.data.get('end_date', leave_request.end_date)
        leave_type = request.data.get('leave_type', leave_request.leave_type)
        reason = request.data.get('reason', leave_request.reason)

        if not (start_date and end_date and leave_type and reason):
            return Response(
                {"error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response(
                {"error": "Invalid leave type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
            end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use ISO format (e.g., YYYY-MM-DD)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if start_date_obj > end_date_obj:
            return Response(
                {"error": "End date must be after start date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        leave_balance, _ = ManagerLeaveBalance.objects.get_or_create(user=leave_request.user)
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response(
                {"error": "Insufficient medical leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response(
                {"error": "Insufficient vacation leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response(
                {"error": "Insufficient personal leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.start_date = start_date_obj
        leave_request.end_date = end_date_obj
        leave_request.leave_type = leave_type
        leave_request.reason = reason
        leave_request.save()

        ManagerNotification.objects.create(
            user='admin',
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Manager {leave_request.user} updated their pending leave request (ID: {leave_id}) for {leave_type} from {start_date_obj} to {end_date_obj}."
        )

        return Response(
            {"message": "Leave request updated successfully."},
            status=status.HTTP_200_OK
        )

    except ManagerLeaveRequest.DoesNotExist:
        return Response(
            {"error": "Leave request not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view(['POST'])
def submit_employee_late_login_reason(request):
    """
    API endpoint to submit a late login reason for an employee auto-leave request.
    """
    try:
        with transaction.atomic():  # Ensure atomic database operations
            serializer = SubmitemployeeLateLoginReasonSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid input: {serializer.errors}")
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            leave_id = serializer.validated_data['leave_id']
            reason_text = serializer.validated_data['reason'].strip()

            logger.debug(f"Received data - leave_id: {leave_id}, reason: {reason_text}")

            # Fetch the leave request
            leave_request = get_object_or_404(LeaveRequest, id=leave_id)
            logger.debug(f"Fetched leave_request: {leave_request.id}, is_auto_leave: {leave_request.is_auto_leave}, reason: {leave_request.reason}")

            is_auto_leave_condition = leave_request.is_auto_leave or leave_request.reason == "Auto Leave: Late or No Login"
            if not is_auto_leave_condition:
                logger.warning(f"Leave ID {leave_id} is not an auto-leave request.")
                return Response(
                    {'error': 'This leave request is not an auto-leave and cannot have a reason submitted.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if employee exists
            if not leave_request.employee:
                logger.warning(f"No employee associated with leave_id={leave_id}")
                return Response(
                    {'error': 'No employee associated with this leave request.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if a reason has already been submitted
            if EmployeeLateLoginReason.objects.filter(leave_request=leave_request).exists():
                logger.warning(f"Reason already submitted for leave_id={leave_id}")
                return Response(
                    {'error': 'A reason has already been submitted for this leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if submission is on the same day as the leave request
            today = timezone.localdate()
            leave_date = leave_request.start_date
            logger.debug(f"Today: {today}, Leave date: {leave_date}")
            if today > leave_date:
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} after the leave date")
                return Response(
                    {'error': 'Late login reasons can only be submitted on the same day as the leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if current time is within shift hours
            employee = leave_request.employee
            shift = getattr(employee, 'shift', None)  # Handle case where shift might be None
            if not shift:
                logger.warning(f"No shift assigned to employee {employee.employee_id if employee else 'Unknown'}")
                return Response(
                    {'error': 'No shift assigned to this employee.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shift_start_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_start_time),
                timezone.get_current_timezone()
            )
            shift_end_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_date, shift.shift_end_time),
                timezone.get_current_timezone()
            )

            # If shift ends before it starts (e.g., night shift crossing midnight), adjust end time to next day
            if shift_end_datetime < shift_start_datetime:
                shift_end_datetime += timezone.timedelta(days=1)

            current_datetime = timezone.now()
            logger.debug(f"Shift: {shift_start_datetime} to {shift_end_datetime}, Current: {current_datetime}")

            # Check if current time is within shift hours
            if not (shift_start_datetime <= current_datetime <= shift_end_datetime):
                logger.warning(f"Attempt to submit late login reason for leave_id={leave_id} outside shift hours")
                return Response(
                    {'error': 'Late login reasons can only be submitted during shift hours on the same day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create the late login reason
            late_login_reason = EmployeeLateLoginReason.objects.create(
                employee=leave_request.employee,
                leave_request=leave_request,
                date=leave_request.start_date,
                reason=reason_text,
                status='pending'
            )

            leave_serializer = LeaveRequestSerializer(leave_request)
            logger.info(f"Successfully submitted reason for leave_id={leave_id}")
            return Response({
                'message': 'Late login reason submitted successfully.',
                'data': leave_serializer.data
            }, status=status.HTTP_200_OK)

    except LeaveRequest.DoesNotExist:
        logger.warning(f"No leave request found for leave_id={leave_id}")
        return Response(
            {'error': 'No leave request found with this ID.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as ve:
        logger.error(f"ValueError in submit_employee_late_login_reason: {str(ve)}", exc_info=True)
        return Response(
            {'error': 'Invalid leave_id format. Must be an integer.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in submit_employee_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An internal server error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
def admin_employee_late_login_reasons(request):
    try:
        late_login_reasons = EmployeeLateLoginReason.objects.select_related('employee', 'leave_request').values(
            'id',
            'employee__employee_id',
            'employee__employee_name',
            'date',
            'reason',
            'status',
            'leave_request__leave_type'
        )
        
        if not late_login_reasons:
            logger.warning("No late login reasons found matching the criteria.")
            
        data = {
            'late_login_reasons': [
                {
                    'id': reason['id'],
                    'employee_id': reason['employee__employee_id'],
                    'employee_name': reason['employee__employee_name'] or 'Unknown Employee',
                    'date': reason['date'].isoformat(),
                    'reason': reason['reason'] or 'No reason provided',
                    'status': reason['status'],
                    'leave_type': reason['leave_request__leave_type'] or 'N/A'
                } for reason in late_login_reasons
            ]
        }
        return Response(data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in admin_employee_late_login_reasons: {str(e)}", exc_info=True)
        return Response({'error': f'Internal server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def approve_employee_late_login_reason(request, reason_id):
    try:
        late_login_reason = get_object_or_404(EmployeeLateLoginReason, id=reason_id)
        leave_request = late_login_reason.leave_request
        
        if late_login_reason.status != 'pending':
            return Response({'error': 'Only pending reasons can be approved.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the leave is an auto leave and was approved, restore the deducted leave balance
        if leave_request.is_auto_leave and leave_request.status == 'approved':
            leave_balance, _ = LeaveBalance.objects.get_or_create(user=leave_request.user)
            if leave_request.leave_type == 'medical':
                leave_balance.medical_leave += 1
            elif leave_request.leave_type == 'vacation':
                leave_balance.vacation_leave += 1
            elif leave_request.leave_type == 'personal':
                leave_balance.personal_leave += 1
            leave_balance.recalculate_total_leave_days()
            leave_balance.save()
        
        # Update LateLoginReason status
        late_login_reason.status = 'approved'
        late_login_reason.save()
        
        # Mark the associated leave request as rejected (not counted as leave)
        leave_request.status = 'rejected'
        leave_request.save()
        
        # Send notification
        Notification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your late login reason for {leave_request.start_date} has been approved. The associated leave has been rejected."
        )

        logger.info(f"Approved late login reason ID: {reason_id}, set leave ID: {leave_request.id} to rejected")
        return Response({'message': 'Reason approved successfully. Associated leave marked as rejected.'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in approve_employee_late_login_reason: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reject_employee_late_login_reason(request, reason_id):
    try:
        with transaction.atomic():
            late_login_reason = get_object_or_404(EmployeeLateLoginReason, id=reason_id)
            leave_request = late_login_reason.leave_request

            if late_login_reason.status != 'pending':
                return Response(
                    {'error': 'Only pending reasons can be rejected.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the leave is an auto leave
            if leave_request.is_auto_leave:
                # For auto leaves, do not deduct balance again as it was already deducted in employee_check_and_auto_leave
                logger.info(f"Rejected late login reason ID: {reason_id} for auto leave ID: {leave_request.id}. No additional balance deduction.")
            else:
                # For non-auto leaves, proceed with balance deduction if the leave is approved
                if leave_request.status == 'approved':
                    total_days = (leave_request.end_date - leave_request.start_date).days + 1
                    sundays = sum(
                        1 for i in range(total_days)
                        if (leave_request.start_date + timedelta(days=i)).weekday() == 6
                    )
                    leave_days_used = total_days - sundays

                    leave_balance, _ = LeaveBalance.objects.get_or_create(user=leave_request.user)

                    # Check if sufficient balance exists before proceeding
                    if leave_request.leave_type == 'medical':
                        if leave_balance.medical_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient medical leave balance. Required: {leave_days_used}, Available: {leave_balance.medical_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.medical_leave -= leave_days_used
                    elif leave_request.leave_type == 'vacation':
                        if leave_balance.vacation_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient vacation leave balance. Required: {leave_days_used}, Available: {leave_balance.vacation_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.vacation_leave -= leave_days_used
                    elif leave_request.leave_type == 'personal':
                        if leave_balance.personal_leave < leave_days_used:
                            return Response(
                                {'error': f'Insufficient personal leave balance. Required: {leave_days_used}, Available: {leave_balance.personal_leave}'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        leave_balance.personal_leave -= leave_days_used

                    # Update leave balance
                    leave_balance.recalculate_total_leave_days()
                    leave_balance.save()

            # Update LateLoginReason status
            late_login_reason.status = 'rejected'
            late_login_reason.save()

            # Send notification
            Notification.objects.create(
                user=leave_request.user,
                date=timezone.now().date(),
                time=timezone.localtime(timezone.now()).time(),
                message=f"Your late login reason for {leave_request.start_date} has been rejected. The associated leave remains approved and your leave balance has been updated."
            )

            logger.info(f"Rejected late login reason ID: {reason_id}, leave ID: {leave_request.id} remains approved")
            return Response(
                {'message': 'Reason rejected successfully. Associated leave remains approved.'},
                status=status.HTTP_200_OK
            )

    except Exception as e:
        logger.error(f"Error in reject_employee_late_login_reason: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Internal server error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def edit_employee_leave_request(request, leave_id):
    try:
        leave_request = LeaveRequest.objects.get(id=leave_id)
        
        if leave_request.status != 'pending':
            return Response(
                {"error": "Only pending leave requests can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_id = request.session.get('user_id')
        if leave_request.user_id != user_id:
            return Response(
                {"error": "You can only edit your own leave requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        start_date = request.data.get('start_date', leave_request.start_date)
        end_date = request.data.get('end_date', leave_request.end_date)
        leave_type = request.data.get('leave_type', leave_request.leave_type)
        reason = request.data.get('reason', leave_request.reason)

        if not (start_date and end_date and leave_type and reason):
            return Response(
                {"error": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response(
                {"error": "Invalid leave type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()

        if start_date_obj > end_date_obj:
            return Response(
                {"error": "End date must be after start date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        leave_balance, _ = LeaveBalance.objects.get_or_create(user=leave_request.user)
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response(
                {"error": "Insufficient medical leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response(
                {"error": "Insufficient vacation leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif leave_type == 'personal' and leave_balance.personal_leave <-leave_days_used:
            return Response(
                {"error": "Insufficient personal leave balance."},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.start_date = start_date_obj
        leave_request.end_date = end_date_obj
        leave_request.leave_type = leave_type
        leave_request.reason = reason
        leave_request.save()

        Notification.objects.create(
            user='admin',
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Employee {leave_request.user} updated their pending leave request (ID: {leave_id}) for {leave_type} from {start_date_obj} to {end_date_obj}."
        )

        return Response(
            {"message": "Leave request updated successfully."},
            status=status.HTTP_200_OK
        )

    except LeaveRequest.DoesNotExist:
        return Response(
            {"error": "Leave request not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

############################### New Flow Changes ##################################################

@api_view(['PUT'])
def update_user_leave_balance(request, username):
    try:
        user = get_object_or_404(User, username=username)
        data = request.data

        leave_balance, created = UserLeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                'medical_leave': 0,
                'vacation_leave': 0,
                'personal_leave': 0,
                'total_leave_days': 0,
                'total_absent_days': 0,
            }
        )

        # Update fields only if present in request data
        leave_balance.medical_leave = data.get("medical_leave", leave_balance.medical_leave)
        leave_balance.vacation_leave = data.get("vacation_leave", leave_balance.vacation_leave)
        leave_balance.personal_leave = data.get("personal_leave", leave_balance.personal_leave)

        leave_balance.recalculate_total_leave_days()

        return Response({"success": "Leave balance updated successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": f"Error updating leave balance: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def user_leave_policies(request):
    try:
        users = User.objects.all()
        leave_data = []

        for user in users:
            try:
                leave_balance = user.leave_balance  # one-to-one relation
                leave_data.append({
                    'id': leave_balance.id,
                    'user': user.user_name,
                    'department': user.department.department_name if user.department else None,
                    'role': user.designation,
                    'leave_balance': {
                        'medical_leave': leave_balance.medical_leave,
                        'vacation_leave': leave_balance.vacation_leave,
                        'personal_leave': leave_balance.personal_leave,
                        'total_leave_days': leave_balance.total_leave_days,
                        'total_absent_days': leave_balance.total_absent_days
                    }
                })
            except UserLeaveBalance.DoesNotExist:
                continue

        return Response(leave_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'Error fetching leave policies: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
def edit_user_leave_balance(request, id):
    try:
        leave_balance = get_object_or_404(UserLeaveBalance, id=id)

        # Update fields from request data or keep existing values
        try:
            leave_balance.medical_leave = int(request.data.get('medical_leave', leave_balance.medical_leave))
            leave_balance.vacation_leave = int(request.data.get('vacation_leave', leave_balance.vacation_leave))
            leave_balance.personal_leave = int(request.data.get('personal_leave', leave_balance.personal_leave))
        except ValueError:
            return Response({'error': 'Leave values must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        leave_balance.recalculate_total_leave_days()

        return Response({'message': f'Leave balance for user {leave_balance.user.username} updated successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_user_leave_balance(request, id):
    try:
        leave_balance = get_object_or_404(UserLeaveBalance, id=id)
        designation = leave_balance.user.designation
        leave_balance.delete()

        return Response({"detail": f"{designation} leave balance deleted successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    



logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_user_late_login_reason(request):
    """
    Unified API endpoint to submit a late login reason for a User auto-leave request.
    Works for Employee, Supervisor, and HR (based on User.designation).
    """
    try:
        with transaction.atomic():
            serializer = UserLateLoginReasonSerializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Invalid input: {serializer.errors}")
                return Response(
                    {'error': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            leave_id = serializer.validated_data['leave_id']
            reason_text = serializer.validated_data['reason'].strip()

            leave_request = get_object_or_404(UserLeaveRequest, id=leave_id)

            # Check auto-leave condition
            if not (leave_request.is_auto_leave or leave_request.reason == "Auto Leave: Late or No Login"):
                return Response(
                    {'error': 'This leave request is not an auto-leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = leave_request.user
            if not user:
                return Response(
                    {'error': 'No user associated with this leave request.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure only one reason per leave
            if UserLateLoginReason.objects.filter(leave_request=leave_request).exists():
                return Response(
                    {'error': 'A reason has already been submitted for this leave.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Must be submitted same day
            today = timezone.localdate()
            if today > leave_request.start_date:
                return Response(
                    {'error': 'Late login reasons can only be submitted on the same day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Must be within shift hours
            shift = getattr(user, 'shift', None)
            if not shift:
                return Response(
                    {'error': f'No shift assigned to this {user.designation}.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            shift_start_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_request.start_date, shift.shift_start_time),
                timezone.get_current_timezone()
            )
            shift_end_datetime = timezone.make_aware(
                timezone.datetime.combine(leave_request.start_date, shift.shift_end_time),
                timezone.get_current_timezone()
            )
            if shift_end_datetime < shift_start_datetime:  # Night shift handling
                shift_end_datetime += timezone.timedelta(days=1)

            now = timezone.now()
            if not (shift_start_datetime <= now <= shift_end_datetime):
                return Response(
                    {'error': 'Late login reasons can only be submitted during shift hours.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save late login reason
            UserLateLoginReason.objects.create(
                user=user,
                leave_request=leave_request,
                date=leave_request.start_date,
                reason=reason_text,
                status='pending'
            )

            leave_serializer = UserLeaveRequestSerializer(leave_request)
            return Response({
                'message': f'Late login reason submitted successfully by {user.designation}.',
                'data': leave_serializer.data
            }, status=status.HTTP_200_OK)

    except UserLeaveRequest.DoesNotExist:
        return Response({'error': 'No leave request found with this ID.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in submit_user_late_login_reason: {str(e)}", exc_info=True)
        return Response({'error': 'An internal server error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST', 'GET'])
def user_leave_status(request):
    if request.method == 'POST':
        leave_id = request.data.get('leave_id')
        status_update = request.data.get('status')

        if status_update not in ['approved', 'rejected']:
            return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            leave_request = UserLeaveRequest.objects.get(id=leave_id)
        except UserLeaveRequest.DoesNotExist:
            return Response({'error': 'Leave request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if leave_request.status == status_update:
            return Response({'message': f'Leave request is already {status_update}.'}, status=status.HTTP_200_OK)

        leave_days_used = 0
        if status_update == 'approved':
            total_days = (leave_request.end_date - leave_request.start_date).days + 1
            sundays = sum(
                1 for i in range(total_days)
                if (leave_request.start_date + timedelta(days=i)).weekday() == 6
            )
            leave_days_used = total_days - sundays

            # Fetch or create leave balance
            leave_balance, _ = UserLeaveBalance.objects.get_or_create(user=leave_request.user)

            # Deduct leave balance
            if leave_request.leave_type == 'medical':
                if leave_balance.medical_leave < leave_days_used:
                    return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.medical_leave -= leave_days_used
            elif leave_request.leave_type == 'vacation':
                if leave_balance.vacation_leave < leave_days_used:
                    return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.vacation_leave -= leave_days_used
            elif leave_request.leave_type == 'personal':
                if leave_balance.personal_leave < leave_days_used:
                    return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
                leave_balance.personal_leave -= leave_days_used

            leave_balance.recalculate_total_leave_days()
            leave_balance.save()

        # Update leave request
        leave_request.status = status_update
        leave_request.save()

        # Create notifications
        UserNotification.objects.create(
            user=leave_request.user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"Your leave request for {leave_request.leave_type} from {leave_request.start_date} to {leave_request.end_date} has been {status_update}."
        )

        return Response({'message': f'Leave request has been {status_update}.'}, status=status.HTTP_200_OK)

    elif request.method == 'GET':
        search_user_id = request.query_params.get('search_user_id', '')
        email = request.query_params.get('email', '')
        search_status = request.query_params.get('search_status', '')
        search_leave_type = request.query_params.get('search_leave_type', '')
        from_date = request.query_params.get('from_date', '')
        to_date = request.query_params.get('to_date', '')

        leave_requests = UserLeaveRequest.objects.all()
        if search_user_id:
            leave_requests = leave_requests.filter(user_id=search_user_id)
        if search_status:
            leave_requests = leave_requests.filter(status=search_status)
        if search_leave_type:
            leave_requests = leave_requests.filter(leave_type=search_leave_type)
        if email:
            leave_requests = leave_requests.filter(email=email)
        if from_date:
            leave_requests = leave_requests.filter(start_date__gte=from_date)
        if to_date:
            leave_requests = leave_requests.filter(end_date__lte=to_date)

        serializer = UserLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
def user_apply_leave(request):
    """
    Unified API to apply leave for any user (Employee, Supervisor, HR).
    """
    try:
        # Extract request data
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        leave_type = request.data.get('leave_type')
        reason = request.data.get('reason')
        leave_proof = request.FILES.get('leave_proof')
        user_id = request.data.get('user_id')

        # Validate required fields
        if not (start_date and end_date and leave_type and user_id):
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate leave type
        valid_leave_types = ['medical', 'vacation', 'personal']
        if leave_type not in valid_leave_types:
            return Response({'error': 'Invalid leave type.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user
        try:
            user = User.objects.get(user_id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date strings
        start_date_obj = timezone.datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end_date_obj = timezone.datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()

        if start_date_obj > end_date_obj:
            return Response({'error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total leave days (excluding Sundays)
        total_days = (end_date_obj - start_date_obj).days + 1
        sundays = sum(1 for i in range(total_days) if (start_date_obj + timedelta(days=i)).weekday() == 6)
        leave_days_used = total_days - sundays

        # Fetch or create leave balance
        leave_balance, _ = UserLeaveBalance.objects.get_or_create(user=user)

        # Check if balance is enough
        if leave_type == 'medical' and leave_balance.medical_leave < leave_days_used:
            return Response({'error': 'Insufficient medical leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'vacation' and leave_balance.vacation_leave < leave_days_used:
            return Response({'error': 'Insufficient vacation leave balance.'}, status=status.HTTP_400_BAD_REQUEST)
        elif leave_type == 'personal' and leave_balance.personal_leave < leave_days_used:
            return Response({'error': 'Insufficient personal leave balance.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create leave request
        leave_request = UserLeaveRequest.objects.create(
            start_date=start_date_obj,
            end_date=end_date_obj,
            leave_type=leave_type,
            reason=reason,
            leave_proof=leave_proof,
            user=user,
            email=user.email,
            status='pending'
        )

        # Notification
        UserApplyNotification.objects.create(
            user=user,
            date=timezone.now().date(),
            time=timezone.localtime(timezone.now()).time(),
            message=f"{user.designation} requested {leave_type} leave from {start_date_obj} to {end_date_obj}"
        )

        return Response({
            'message': 'Leave request submitted successfully!',
            'leave_id': leave_request.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def user_leave_history(request):
    """
    Fetch leave history with optional filters:
    user_id, from_date, to_date, status
    """
    user_id = request.query_params.get('user_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')
    status_filter = request.query_params.get('status')

    filter_args = {}
    if user_id:
        filter_args['user__user_id'] = user_id
    if from_date:
        filter_args['start_date__gte'] = from_date
    if to_date:
        filter_args['end_date__lte'] = to_date
    if status_filter:
        filter_args['status'] = status_filter

    leave_requests = UserLeaveRequest.objects.filter(**filter_args).order_by('-start_date')
    serializer = UserLeaveRequestSerializer(leave_requests, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def user_leave_history_by_id(request, id):
    """
    Retrieve leave request history for a specific user ID.
    """
    try:
        leave_requests = get_list_or_404(UserLeaveRequest, user__user_id=id)
        serializer = UserLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def user_leave_history_list(request):
    """
    Fetch all leave requests for all users.
    """
    try:
        leave_requests = UserLeaveRequest.objects.all().order_by('-start_date')
        serializer = UserLeaveRequestSerializer(leave_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)