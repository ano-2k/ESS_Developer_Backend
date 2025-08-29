from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from rest_framework import status
from datetime import datetime, timedelta, timezone
from calendar import calendar, monthrange
from authentication.models import Admin, Ar, Manager, Supervisor, Hr, User,Department
from leaves.models import ArLeaveRequest, LeaveRequest, ManagerLeaveRequest, SupervisorLeaveRequest,HrLeaveRequest,LateloginReason
from .models import CalendarEvent, Employee, ResetRequest, Shift, Attendance, Location, PermissionHour
from authentication.serializers import LocationSerializer, ShiftSerializer
from datetime import datetime,time
from django.db.models import Q

#admin chart
@api_view(['GET'])
def get_checked_in_users(request):
    """Fetch all users from Attendance table where 'time_in' is present"""
    current_date = now().date()
    checked_in_users = Attendance.objects.filter(date=current_date,time_in__isnull=False)
    serializer = AttendanceSerializer(checked_in_users, many=True)
    return Response({"checked_in_users": serializer.data})

@api_view(['GET'])
def attendance_history(request):
    try:
        # Fetch all attendance records
        attendance = Attendance.objects.all()
        
        # Serialize the data
        serializer = AttendanceSerializer(attendance, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Attendance.DoesNotExist:
        # Handle case where Attendance records do not exist
        return Response(
            {"error": "No attendance records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#-------------altered view after location field added --------------------

@api_view(['POST'])
def employee_attendance_form(request, user_id):
    try:
        employee = Employee.objects.get(employee_id=user_id)

        # Safe location and shift handling
        location = employee.location
        locations = [location] if location else []
        location_serializer = LocationSerializer(locations, many=True)
        shift = employee.shift
        shift_serializer = ShiftSerializer(shift) if shift else None

        today = timezone.localdate()
        last_attendance = Attendance.objects.filter(employee=employee, date=today).first()

        show_checkout = False
        thank_you_message = ''
        already_checked_out = False
        first_in_time = "--:--"
        last_out_time = "--:--"
        on_leave = False

        leave_request = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            on_leave = True

        if last_attendance:
            if last_attendance.time_in:
                first_in_time = last_attendance.time_in.strftime("%I:%M %p")
            if last_attendance.time_out:
                last_out_time = last_attendance.time_out.strftime("%I:%M %p")

            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                approved_reset = ResetRequest.objects.filter(
                    employee=employee,
                    date=today,
                    status='approved'
                ).exists()
                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    already_checked_out = True
                    thank_you_message = 'You have already checked out for today.'
                    return Response({
                        'locations': location_serializer.data,
                        'shift': shift_serializer.data if shift_serializer else None,
                        'show_checkout': False,
                        'thank_you_message': thank_you_message,
                        'already_checked_out': already_checked_out,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'on_leave': on_leave,
                    }, status=status.HTTP_200_OK)

        if on_leave:
            return Response({
                'locations': location_serializer.data,
                'shift': shift_serializer.data if shift_serializer else None,
                'show_checkout': False,
                'thank_you_message': '',
                'already_checked_out': False,
                'first_in_time': first_in_time,
                'last_out_time': last_out_time,
                'on_leave': on_leave,
            }, status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data if shift_serializer else None,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message,
            'already_checked_out': already_checked_out,
            'first_in_time': first_in_time,
            'last_out_time': last_out_time,
            'on_leave': on_leave,
        }, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_employee_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "Employee ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = Employee.objects.get(employee_id=user_id)
        today = datetime.now().date()

        leave_request = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            if Attendance.objects.filter(employee=employee, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                employee=employee,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({
                "message": "Checked in successfully.",
                "time_in": current_time.strftime('%H:%M:%S'),
                "in_status": in_status
            }, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            time_out = datetime.now().strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                employee=employee,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(
                    employee=employee,
                    date=today,
                    status='approved'
                ).exists()
                if reset_approved:
                    last_attendance = Attendance.objects.filter(employee=employee, date=today).first()
                else:
                    return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

            if not last_attendance:
                return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                #time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(today, current_time) - datetime.combine(today, time_in)

            break_start = time(13, 0, 0)
            break_end = time(14, 0, 0)
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({
                "message": "Checked out successfully.",
                "time_out": time_out,
                "out_status": out_status
            }, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def calculate_total_present_days(employee_id):
    """
    Calculate total present days for an employee based on total working hours.

    :param employee_id: ID of the employee
    :return: Total present days (float)
    """
    # Fetch all attendance records for the employee
    attendance_records = Attendance.objects.filter(employee_id=employee_id).exclude(total_working_hours=None)

    # Sum up the total working hours across all records
    total_seconds = sum(
        int(timedelta(
            hours=int(hours.split(':')[0]), 
            minutes=int(hours.split(':')[1]),
            seconds=int(hours.split(':')[2])
        ).total_seconds()) for hours in attendance_records.values_list('total_working_hours', flat=True)
    )

    # Convert total seconds to hours
    total_hours = total_seconds / 3600

    # Calculate present days (8 hours = 1 day)
    present_days = total_hours / 8
    
    
    return round(present_days, 2)  # Round off to 2 decimal placesdir


# July 21 Updated Version 

@api_view(['GET'])
def employee_attendance_history(request, user_id):
    # Get date range from query parameters (not request.data for GET requests)
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    # Parse date strings to date objects if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        from_date = None
        to_date = None

    # Fetch the employee to get their assigned shift
    try:
        employee = Employee.objects.get(employee_id=user_id)
        assigned_shift = employee.shift
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    # Base queries filtered by employee
    attendance_query = Attendance.objects.filter(employee__employee_id=user_id).select_related('shift', 'location')
    leave_query = LeaveRequest.objects.filter(employee__employee_id=user_id, status='approved')

    # Apply date range filtering if provided
    if from_date and to_date:
        attendance_query = attendance_query.filter(date__range=[from_date, to_date])
        leave_query = leave_query.filter(Q(start_date__lte=to_date) & Q(end_date__gte=from_date))

    # Prepare attendance records with reset request status, shift details, and overtime
    attendance_records = []
    for record in attendance_query:
        reset_request = ResetRequest.objects.filter(employee=record.employee, date=record.date).order_by('-created_at').first()
        shift = employee.shift  # Use employee's assigned shift
        shift_start = shift.shift_start_time if shift else None
        shift_end = shift.shift_end_time if shift else None

        # Calculate overtime hours (decimal)
        overtime = "N/A"
        if shift_end and record.time_out and record.time_in:
            shift_end_datetime = datetime.combine(record.date, shift_end)
            if hasattr(record.time_out, 'date'):
                time_out_date = record.time_out.date()
            else:
                time_out_datetime = datetime.combine(record.date, record.time_out)
                time_out_date = time_out_datetime.date()
            if time_out_date == record.date:
                time_out_datetime = datetime.combine(record.date, record.time_out)
                if time_out_datetime > shift_end_datetime:
                    overtime_delta = time_out_datetime - shift_end_datetime
                    overtime_hours = overtime_delta.total_seconds() / 3600
                    overtime = round(overtime_hours, 2)

        # Calculate total working hours formatted as HH:MM:SS with leading zeros
        total_working_hours = record.total_working_hours  # fallback
        if record.time_in and record.time_out:
            time_in_datetime = datetime.combine(record.date, record.time_in)
            time_out_datetime = datetime.combine(record.date, record.time_out)
            if time_out_datetime >= time_in_datetime:
                working_hours_delta = time_out_datetime - time_in_datetime
                total_seconds = int(working_hours_delta.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                total_working_hours = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        attendance_records.append({
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'date': record.date.strftime('%Y-%m-%d'),
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request",
            'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
            'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
            'out_status': record.out_status,
            'overtime': overtime,
        })

    # Prepare leave records with employee's shift details
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            if from_date and to_date and not (from_date <= leave_date <= to_date):
                continue
            leave_records.append({
                'employee_id': employee.employee_id,
                'employee_name': employee.employee_name,
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'leave',
                'time_in': None,
                'time_out': None,
                'total_working_hours': "00:00:00",
                'reset_status': "No Request",
                'shift_start_time': assigned_shift.shift_start_time.strftime('%H:%M:%S') if assigned_shift and assigned_shift.shift_start_time else None,
                'shift_end_time': assigned_shift.shift_end_time.strftime('%H:%M:%S') if assigned_shift and assigned_shift.shift_end_time else None,
                'out_status': None,
                'overtime': None,
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else None,
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else None
    }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def employee_all_attendance_history(request):
    try:
        # Get date range from query parameters
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        employees = Employee.objects.all().prefetch_related('shift')
        all_records = []

        # Parse date strings to date objects if provided
        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                if from_date > to_date:
                    return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            from_date = None
            to_date = None

        for employee in employees:
            shift = employee.shift
            shift_start = shift.shift_start_time if shift else None
            shift_end = shift.shift_end_time if shift else None

            # Base queries filtered by employee
            attendance_query = Attendance.objects.filter(employee=employee).select_related('shift', 'location')
            leave_query = LeaveRequest.objects.filter(employee=employee, status='approved')

            # Apply date range filtering if provided
            if from_date and to_date:
                attendance_query = attendance_query.filter(date__range=[from_date, to_date])
                leave_query = leave_query.filter(Q(start_date__lte=to_date) & Q(end_date__gte=from_date))

            # Prepare attendance records list
            attendance_records = []
            for record in attendance_query:
                reset_request = ResetRequest.objects.filter(employee=employee, date=record.date).order_by('-created_at').first()
                
                # Calculate overtime hours (decimal)
                overtime = "N/A"
                if shift_end and record.time_out and record.time_in:
                    shift_end_datetime = datetime.combine(record.date, shift_end)
                    if hasattr(record.time_out, 'date'):
                        time_out_date = record.time_out.date()
                    else:
                        time_out_datetime = datetime.combine(record.date, record.time_out)
                        time_out_date = time_out_datetime.date()
                    if time_out_date == record.date:
                        time_out_datetime = datetime.combine(record.date, record.time_out)
                        if time_out_datetime > shift_end_datetime:
                           overtime_delta = time_out_datetime - shift_end_datetime
                           total_seconds = int(overtime_delta.total_seconds())
                           hours = total_seconds // 3600
                           minutes = (total_seconds % 3600) // 60
                           seconds = total_seconds % 60
                           overtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"


                # Calculate total working hours formatted as HH:MM:SS with leading zeros
                total_working_hours = record.total_working_hours  # fallback
                if record.time_in and record.time_out:
                    time_in_datetime = datetime.combine(record.date, record.time_in)
                    time_out_datetime = datetime.combine(record.date, record.time_out)
                    if time_out_datetime >= time_in_datetime:
                        working_hours_delta = time_out_datetime - time_in_datetime
                        total_seconds = int(working_hours_delta.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        seconds = total_seconds % 60
                        total_working_hours = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                attendance_records.append({
                    'employee_id': employee.employee_id,
                    'employee_name': employee.employee_name,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'type': 'attendance',
                    'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
                    'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
                    'total_working_hours': total_working_hours,
                    'reset_status': reset_request.status if reset_request else "No Request",
                    'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
                    'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
                    'out_status': record.out_status,
                    'overtime': overtime,
                })

            # Prepare leave records
            leave_records = []
            for leave in leave_query:
                leave_days = (leave.end_date - leave.start_date).days + 1
                for i in range(leave_days):
                    leave_date = leave.start_date + timedelta(days=i)
                    if from_date and to_date and not (from_date <= leave_date <= to_date):
                        continue
                    leave_records.append({
                        'employee_id': employee.employee_id,
                        'employee_name': employee.employee_name,
                        'date': leave_date.strftime('%Y-%m-%d'),
                        'type': 'leave',
                        'time_in': None,
                        'time_out': None,
                        'total_working_hours': "00:00:00",
                        'reset_status': "No Request",
                        'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
                        'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
                        'out_status': None,
                        'overtime': None,
                    })

            # Combine attendance and leave records
            all_records.extend(attendance_records + leave_records)

        # Sort all records by date ascending
        all_records.sort(key=lambda x: x['date'])

        return Response({
            'all_records': all_records,
            'from_date': from_date.strftime('%Y-%m-%d') if from_date else None,
            'to_date': to_date.strftime('%Y-%m-%d') if to_date else None
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import timedelta
from django.utils.dateformat import format
from .models import Attendance
from leaves.models import LeaveRequest

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from datetime import timedelta
from .models import Employee, Attendance
from leaves.models import LeaveRequest


from django.utils import timezone
from datetime import datetime, timedelta, time  

@api_view(['POST'])
def manager_attendance_form(request, user_id):
    try:
        manager = Manager.objects.get(manager_id=user_id)

        # Safe location and shift handling
        location = manager.location
        locations = [location] if location else []
        location_serializer = LocationSerializer(locations, many=True)
        shift = manager.shift
        shift_serializer = ShiftSerializer(shift) if shift else None

        today = timezone.localtime().date()
        last_attendance = Attendance.objects.filter(manager=manager, date=today).first()

        show_checkout = False
        thank_you_message = ''
        already_checked_out = False
        first_in_time = "--:--"
        last_out_time = "--:--"
        on_leave = False

        leave_request = ManagerLeaveRequest.objects.filter(
            manager=manager,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            on_leave = True

        if last_attendance:
            if last_attendance.time_in:
                first_in_time = last_attendance.time_in.strftime("%I:%M %p")
            if last_attendance.time_out:
                last_out_time = last_attendance.time_out.strftime("%I:%M %p")

            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                approved_reset = ResetRequest.objects.filter(
                    manager=manager,
                    date=today,
                    status='approved'
                ).exists()
                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    already_checked_out = True
                    thank_you_message = 'You have already checked out for today.'
                    return Response({
                        'locations': location_serializer.data,
                        'shift': shift_serializer.data if shift_serializer else None,
                        'show_checkout': False,
                        'thank_you_message': thank_you_message,
                        'already_checked_out': already_checked_out,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'on_leave': on_leave,
                    }, status=status.HTTP_200_OK)

        if on_leave:
            return Response({
                'locations': location_serializer.data,
                'shift': shift_serializer.data if shift_serializer else None,
                'show_checkout': False,
                'thank_you_message': '',
                'already_checked_out': False,
                'first_in_time': first_in_time,
                'last_out_time': last_out_time,
                'on_leave': on_leave,
            }, status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data if shift_serializer else None,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message,
            'already_checked_out': already_checked_out,
            'first_in_time': first_in_time,
            'last_out_time': last_out_time,
            'on_leave': on_leave,
        }, status=status.HTTP_200_OK)

    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def submit_manager_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "Manager ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(manager_id=user_id)
        today = datetime.now().date()

        leave_request = ManagerLeaveRequest.objects.filter(
            manager=manager,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            if Attendance.objects.filter(manager=manager, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                manager=manager,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({
                "message": "Checked in successfully.",
                "time_in": current_time.strftime('%H:%M:%S'),
                "in_status": in_status
            }, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            time_out = datetime.now().strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                manager=manager,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(
                    manager=manager,
                    date=today,
                    status='approved'
                ).exists()
                if reset_approved:
                    last_attendance = Attendance.objects.filter(manager=manager, date=today).first()
                else:
                    return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

            if not last_attendance:
                return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(today, current_time) - datetime.combine(today, time_in)

            break_start = time(13, 0, 0)
            break_end = time(14, 0, 0)
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({
                "message": "Checked out successfully.",
                "time_out": time_out,
                "out_status": out_status
            }, status=status.HTTP_200_OK)

    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
from django.utils.timezone import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from .models import Attendance, ResetRequest
from datetime import datetime, timedelta, date

@api_view(['GET'])
def manager_attendance_history(request, user_id):
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')

    attendance_query = Attendance.objects.filter(manager__manager_id=user_id)
    leave_query = ManagerLeaveRequest.objects.filter(manager__manager_id=user_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare attendance records with reset request status
    attendance_records = []
    for record in attendance_query.select_related('shift', 'location'):
        reset_request = ResetRequest.objects.filter(manager=record.manager, date=record.date).order_by('-created_at').first()
        attendance_records.append({
            'date': record.date,
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': record.total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request"
        })

    # Prepare leave records
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'date': leave_date,
                'type': 'leave'
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    # Convert date objects to string format for JSON response
    for record in all_records:
        if isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        elif isinstance(record['date'], date):
            record['date'] = record['date'].strftime('%Y-%m-%d')


    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def manager_employee_attendance_history(request):
    # Step 1: Retrieve user_id from session 
    manager_id = request.session.get('user_id')

    if not manager_id:
        return Response({'error': 'Manager not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)

    # Step 2: Check if the user has a manager role
    try:
        manager = Manager.objects.get(manager_id=manager_id)
    except Manager.DoesNotExist:
        return Response({'error': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

    # Step 3: Retrieve employee_id, from_date, and to_date from query parameters
    employee_id = request.data.get('user_id')
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')

    if not employee_id:
        return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(employee__employee_id=employee_id)
    leave_query = LeaveRequest.objects.filter(employee__employee_id=employee_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare attendance records
    attendance_records = [
        {
            'date': record.date,
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': record.total_working_hours
        }
        for record in attendance_query.select_related('shift', 'location')
    ]

    # Prepare leave records
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'date': leave_date,
                'type': 'leave'
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    # Convert date objects to string format for JSON response
    for record in all_records:
        record['date'] = record['date'].strftime('%Y-%m-%d')

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def manager_employee_attendance_history(request):
#     manager_id = request.session.get('user_id')

#     if not manager_id:
#         return Response({'error': 'Manager not logged in.'}, status=status.HTTP_401_UNAUTHORIZED)

#     # Step 2: Check if the user has a manager role
#     try:
#         manager = Manager.objects.get(manager_id=manager_id)
#     except Manager.DoesNotExist:
#         return Response({'error': 'You do not have permission to access this resource.'}, status=status.HTTP_403_FORBIDDEN)

#     # Step 3: Retrieve employee_id, from_date, and to_date from query parameters
#     employee_id = request.query_params.get('user_id')
#     from_date = request.query_params.get('from_date')
#     to_date = request.query_params.get('to_date')

#     if not employee_id:
#         return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#     # Initialize attendance and leave queries
#     attendance_query = Attendance.objects.filter(employee__employee_id=employee_id)
#     leave_query = LeaveRequest.objects.filter(employee__employee_id=employee_id, status='approved')

#     # Filter by date range if provided
#     if from_date and to_date:
#         try:
#             from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
#             to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

#             if from_date > to_date:
#                 return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

#             attendance_query = attendance_query.filter(date__range=[from_date, to_date])
#             leave_query = leave_query.filter(
#                 Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
#             )
#         except ValueError:
#             return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

#     # Prepare attendance records
#     attendance_records = [
#         {
#             'date': record.date,
#             'type': 'attendance',
#             'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
#             'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
#             'total_working_hours': record.total_working_hours
#         }
#         for record in attendance_query.select_related('shift', 'location')
#     ]

#     # Prepare leave records
#     leave_records = []
#     for leave in leave_query:
#         leave_days = (leave.end_date - leave.start_date).days + 1
#         for i in range(leave_days):
#             leave_date = leave.start_date + timedelta(days=i)
#             leave_records.append({
#                 'date': leave_date,
#                 'type': 'leave'
#             })

#     # Merge and sort all records by date
#     all_records = attendance_records + leave_records
#     all_records.sort(key=lambda x: x['date'])

#     # Convert date objects to string format for JSON response
#     for record in all_records:
#         record['date'] = record['date'].strftime('%Y-%m-%d')

#     return Response({
#         'all_records': all_records,
#         'from_date': from_date,
#         'to_date': to_date
#     }, status=status.HTTP_200_OK)
    
@api_view(['POST'])
def employee_request_check_out_reset(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        today = datetime.today()

        # Check if the employee exists
        try:
            employee = Employee.objects.get(employee_id=user_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

        last_attendance = Attendance.objects.filter(
            employee=employee,
            date=today,
            time_in__isnull=False
        ).first()

        if not last_attendance:
            return Response({"detail": "You can't reset the checkout time before check-in."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the employee has already checked out
        if last_attendance.time_out is None:
            # Employee has not checked out yet
            return Response({"detail": "You can't reset the checkout time before checkout."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if a reset request has already been made for today
        existing_request = ResetRequest.objects.filter(
            employee=employee,
            date=today,
            status='Pending'
        ).exists()

        if existing_request:
            return Response({"detail": "You have already sent the request. Please wait until the checkout time is reset."}, status=status.HTTP_400_BAD_REQUEST)

        # If the employee has checked in and no existing request, process the reset request
        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        # Insert the new reset request into the model
        reset_request = ResetRequest(
            employee=employee,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def manager_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', employee__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            employee_attendance = Attendance.objects.get(
                employee=reset_request.employee,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'employee_id': reset_request.employee.employee_id,  
                'username': reset_request.employee.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': employee_attendance.shift.shift_number if employee_attendance.shift else None,  
                'time_in': employee_attendance.time_in,
                'time_out': employee_attendance.time_out,
                'in_status': employee_attendance.in_status,
                'out_status': employee_attendance.out_status,
                'notes': employee_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def approve_and_reset_checkout_time(request, request_id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=request_id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    employee_id = reset_request.employee.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(employee_id=employee_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Manager'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_reset_request(request, request_id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=request_id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def manager_request_check_out_reset(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        today = datetime.today()

        # Check if the manager exists
        try:
            manager = Manager.objects.get(manager_id=user_id)
        except Manager.DoesNotExist:
            return Response({"detail": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

        last_attendance = Attendance.objects.filter(
            manager=manager,
            date=today,
            time_in__isnull=False
        ).first()

        if not last_attendance:
            return Response({"detail": "You can't reset the checkout time before check-in."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the manager has already checked out
        if last_attendance.time_out is None:
            # Manager has not checked out yet
            return Response({"detail": "You can't reset the checkout time before checkout."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if a reset request has already been made for today
        existing_request = ResetRequest.objects.filter(
            manager=manager,
            date=today,
            status='Pending'
        ).exists()

        if existing_request:
            return Response({"detail": "You have already sent the request. Please wait until the checkout time is reset."}, status=status.HTTP_400_BAD_REQUEST)

        # If the manager has checked in and no existing request, process the reset request
        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        # Insert the new reset request into the model
        reset_request = ResetRequest(
            manager=manager,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def hr_attendance_request_reset(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        today = datetime.today()

        # Check if the manager exists
        try:
            hr = Hr.objects.get(hr_id=user_id)
        except Hr.DoesNotExist:
            return Response({"detail": "Hr not found."}, status=status.HTTP_404_NOT_FOUND)

        last_attendance = Attendance.objects.filter(
            hr=hr,
            date=today,
            time_in__isnull=False
        ).first()

        if not last_attendance:
            return Response({"detail": "You can't reset the checkout time before check-in."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the manager has already checked out
        if last_attendance.time_out is None:
            # Manager has not checked out yet
            return Response({"detail": "You can't reset the checkout time before checkout."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if a reset request has already been made for today
        existing_request = ResetRequest.objects.filter(
            hr=hr,
            date=today,
            status='Pending'
        ).exists()

        if existing_request:
            return Response({"detail": "You have already sent the request. Please wait until the checkout time is reset."}, status=status.HTTP_400_BAD_REQUEST)

        # If the manager has checked in and no existing request, process the reset request
        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        # Insert the new reset request into the model
        reset_request = ResetRequest(
            hr=hr,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def admin_manager_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', manager__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            manager_attendance = Attendance.objects.get(
                manager=reset_request.manager,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'manager_id': reset_request.manager.manager_id,  
                'username': reset_request.manager.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': manager_attendance.shift.shift_number if manager_attendance.shift else None,  
                'time_in': manager_attendance.time_in,
                'time_out': manager_attendance.time_out,
                'in_status': manager_attendance.in_status,
                'out_status': manager_attendance.out_status,
                'notes': manager_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_approve_and_reset_checkout_time(request, id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    manager_id = reset_request.manager.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(manager_id=manager_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def admin_reject_manager_reset_request(request,id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def admin_employee_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', employee__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            employee_attendance = Attendance.objects.get(
                employee=reset_request.employee,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'employee_id': reset_request.employee.employee_id,  
                'username': reset_request.employee.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': employee_attendance.shift.shift_number if employee_attendance.shift else None,  
                'time_in': employee_attendance.time_in,
                'time_out': employee_attendance.time_out,
                'in_status': employee_attendance.in_status,
                'out_status': employee_attendance.out_status,
                'notes': employee_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_approve_and_reset_employee_checkout_time(request, id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    employee_id = reset_request.employee.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(employee_id=employee_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def admin_reject_employee_reset_request(request, id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def md_employee_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', employee__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            employee_attendance = Attendance.objects.get(
                employee=reset_request.employee,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'employee_id': reset_request.employee.employee_id,  
                'username': reset_request.employee.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': employee_attendance.shift.shift_number if employee_attendance.shift else None,  
                'time_in': employee_attendance.time_in,
                'time_out': employee_attendance.time_out,
                'in_status': employee_attendance.in_status,
                'out_status': employee_attendance.out_status,
                'notes': employee_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def md_approve_and_reset_employee_checkout_time(request, request_id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=request_id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    employee_id = reset_request.employee.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(employee_id=employee_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by MD'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def md_reject_employee_reset_request(request, request_id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=request_id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def md_manager_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', manager__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            manager_attendance = Attendance.objects.get(
                manager=reset_request.manager,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'manager_id': reset_request.manager.manager_id,  
                'username': reset_request.manager.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': manager_attendance.shift.shift_number if manager_attendance.shift else None,  
                'time_in': manager_attendance.time_in,
                'time_out': manager_attendance.time_out,
                'in_status': manager_attendance.in_status,
                'out_status': manager_attendance.out_status,
                'notes': manager_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def md_approve_and_reset_manager_checkout_time(request, request_id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=request_id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    manager_id = reset_request.manager.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(manager_id=manager_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by MD'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def md_reject_manager_reset_request(request, request_id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=request_id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

from datetime import datetime, timedelta, date



@api_view(['POST'])
def supervisor_attendance_form(request, user_id):
    try:
        supervisor = Supervisor.objects.get(supervisor_id=user_id)

        locations = [supervisor.location] if supervisor.location else []
        if locations and len(locations) > 1:
            locations = [locations[0]]

        location_serializer = LocationSerializer(locations, many=True)

        shift = supervisor.shift
        shift_serializer = ShiftSerializer(shift) if shift else None

        today = datetime.now().date()
        last_attendance = Attendance.objects.filter(supervisor=supervisor, date=today).first()

        show_checkout = False
        thank_you_message = ''
        already_checked_out = False
        first_in_time = "--:--"
        last_out_time = "--:--"

        if last_attendance:
            if last_attendance.time_in:
                first_in_time = last_attendance.time_in.strftime("%I:%M %p")
            if last_attendance.time_out:
                last_out_time = last_attendance.time_out.strftime("%I:%M %p")

            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                approved_reset = ResetRequest.objects.filter(
                    supervisor=supervisor,
                    date=today,
                    status='Approved',
                ).exists()

                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    already_checked_out = True
                    thank_you_message = 'You have already checked out for today.'

                    return Response({
                        'locations': location_serializer.data,
                        'shift': shift_serializer.data,
                        'show_checkout': False,
                        'thank_you_message': thank_you_message,
                        'already_checked_out': already_checked_out,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                    }, status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data if shift_serializer else None,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message,
            'already_checked_out': already_checked_out,
            'first_in_time': first_in_time,
            'last_out_time': last_out_time,
        }, status=status.HTTP_200_OK)

    except Supervisor.DoesNotExist:
        return Response({'error': 'Supervisor not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_supervisor_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "Supervisor ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        supervisor = Supervisor.objects.get(supervisor_id=user_id)

        # Check leave status
        today = datetime.now().date()
        leave_request = SupervisorLeaveRequest.objects.filter(
            supervisor=supervisor,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request:
            # Since approved auto-leave reasons delete the leave request, this block will only catch non-auto-leaves or unprocessed auto-leaves
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            today = datetime.now().date()
            if Attendance.objects.filter(supervisor=supervisor, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                supervisor=supervisor,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            today = datetime.now().date()
            time_out = datetime.now().strftime('%H:%M:%S')

            # Try to get open attendance first
            last_attendance = Attendance.objects.filter(
                supervisor__supervisor_id=user_id,
                date=today,
                time_out=None
            ).first()

            # If already checked out, check if reset is approved
            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(
                    supervisor__supervisor_id=user_id,
                    date=today,
                    status='approved'
                ).exists()
                if reset_approved:
                    last_attendance = Attendance.objects.filter(
                        supervisor__supervisor_id=user_id,
                        date=today
                    ).first()
                else:
                    return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

            if not last_attendance:
                return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(datetime.today(), shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), time_in)

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            # Save updates
            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

    except Supervisor.DoesNotExist:
        return Response({'error': 'Supervisor not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def supervisor_attendance_history(request, user_id):
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')

    attendance_query = Attendance.objects.filter(supervisor__supervisor_id=user_id)
    leave_query = SupervisorLeaveRequest.objects.filter(supervisor__supervisor_id=user_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare attendance records with reset request status
    attendance_records = []
    for record in attendance_query.select_related('shift', 'location'):
        reset_request = ResetRequest.objects.filter(supervisor=record.supervisor, date=record.date).order_by('-created_at').first()
        attendance_records.append({
            'date': record.date,
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': record.total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request"
        })

    # Prepare leave records
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'date': leave_date,
                'type': 'leave'
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    # Convert date objects to string format for JSON response
    for record in all_records:
        if isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        elif isinstance(record['date'], date):
            record['date'] = record['date'].strftime('%Y-%m-%d')


    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def supervisor_request_check_out_reset(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        today = datetime.today()

        # Check if the employee exists
        try:
            supervisor = Supervisor.objects.get(supervisor_id=user_id)
        except Supervisor.DoesNotExist:
            return Response({"detail": "Supervisor not found."}, status=status.HTTP_404_NOT_FOUND)

        last_attendance = Attendance.objects.filter(
            supervisor=supervisor,
            date=today,
            time_in__isnull=False
        ).first()

        if not last_attendance:
            return Response({"detail": "You can't reset the checkout time before check-in."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the employee has already checked out
        if last_attendance.time_out is None:
            # Employee has not checked out yet
            return Response({"detail": "You can't reset the checkout time before checkout."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if a reset request has already been made for today
        existing_request = ResetRequest.objects.filter(
            supervisor=supervisor,
            date=today,
            status='Pending'
        ).exists()

        if existing_request:
            return Response({"detail": "You have already sent the request. Please wait until the checkout time is reset."}, status=status.HTTP_400_BAD_REQUEST)

        # If the employee has checked in and no existing request, process the reset request
        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        # Insert the new reset request into the model
        reset_request = ResetRequest(
            supervisor=supervisor,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)
    
    
@api_view(['GET'])
def admin_supervisor_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', supervisor__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            supervisor_attendance = Attendance.objects.get(
                supervisor=reset_request.supervisor,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'supervisor_id': reset_request.supervisor.supervisor_id,  
                'username': reset_request.supervisor.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': supervisor_attendance.shift.shift_number if supervisor_attendance.shift else None,  
                'time_in': supervisor_attendance.time_in,
                'time_out': supervisor_attendance.time_out,
                'in_status': supervisor_attendance.in_status,
                'out_status': supervisor_attendance.out_status,
                'notes': supervisor_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_approve_and_reset_supervisor_checkout_time(request, id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    supervisor_id = reset_request.supervisor.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(supervisor_id=supervisor_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def admin_reject_supervisor_reset_request(request, id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def md_supervisor_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', supervisor__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            supervisor_attendance = Attendance.objects.get(
                supervisor=reset_request.supervisor,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'supervisor_id': reset_request.supervisor.supervisor_id,  
                'username': reset_request.supervisor.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': supervisor_attendance.shift.shift_number if supervisor_attendance.shift else None,  
                'time_in': supervisor_attendance.time_in,
                'time_out': supervisor_attendance.time_out,
                'in_status': supervisor_attendance.in_status,
                'out_status': supervisor_attendance.out_status,
                'notes': supervisor_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def md_approve_and_reset_supervisor_checkout_time(request, request_id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=request_id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    supervisor_id = reset_request.supervisor.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(supervisor_id=supervisor_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def md_reject_supervisor_reset_request(request, request_id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=request_id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def admin_employee_attendance_history(request):
    # Retrieve manager_id, from_date, and to_date from query parameters
    employee_id = request.query_params.get('employee_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not employee_id:
        return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(employee__employee_id=employee_id)
    leave_query = LeaveRequest.objects.filter(employee__employee_id=employee_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize attendance records and add manager_name
    attendance_records = []
    for attendance in attendance_query:
        attendance_records.append({
            'id': attendance.id,
            'employee_name': employee.employee_name,  # Include manager name
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time_in': attendance.time_in,
            'time_out': attendance.time_out,
            'in_status': attendance.in_status,
            'out_status': attendance.out_status,
            'overtime': attendance.overtime,
            'total_working_hours': attendance.total_working_hours,
            'type': 'attendance',
        })

    # Prepare leave records manually with manager_name
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'employee_name': employee.employee_name,  # Include manager name
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'on leave'
            })

    # Combine attendance and leave records, and sort by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def admin_supervisor_attendance_history(request):
    # Retrieve manager_id, from_date, and to_date from query parameters
    supervisor_id = request.query_params.get('supervisor_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not supervisor_id:
        return Response({'error': 'Supervisor ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        supervisor = Supervisor.objects.get(supervisor_id=supervisor_id)
    except Supervisor.DoesNotExist:
        return Response({"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(supervisor__supervisor_id=supervisor_id)
    leave_query = SupervisorLeaveRequest.objects.filter(supervisor__supervisor_id=supervisor_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize attendance records and add manager_name
    attendance_records = []
    for attendance in attendance_query:
        attendance_records.append({
            'id': attendance.id,
            'supervisor_name': supervisor.supervisor_name,  # Include manager name
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time_in': attendance.time_in,
            'time_out': attendance.time_out,
            'in_status': attendance.in_status,
            'out_status': attendance.out_status,
            'overtime': attendance.overtime,
            'total_working_hours': attendance.total_working_hours,
            'type': 'attendance',
        })

    # Prepare leave records manually with manager_name
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'supervisor_name': supervisor.supervisor_name,  # Include manager name
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'on leave'
            })

    # Combine attendance and leave records, and sort by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
    
@api_view(['GET'])
def admin_manager_attendance_history(request):
    # Retrieve manager_id, from_date, and to_date from query parameters
    manager_id = request.query_params.get('manager_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not manager_id:
        return Response({'error': 'Manager ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(manager_id=manager_id)
    except Manager.DoesNotExist:
        return Response({"detail": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(manager__manager_id=manager_id)
    leave_query = ManagerLeaveRequest.objects.filter(manager__manager_id=manager_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize attendance records and add manager_name
    attendance_records = []
    for attendance in attendance_query:
        attendance_records.append({
            'id': attendance.id,
            'manager_name': manager.manager_name,  # Include manager name
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time_in': attendance.time_in,
            'time_out': attendance.time_out,
            'in_status': attendance.in_status,
            'out_status': attendance.out_status,
            'overtime': attendance.overtime,
            'total_working_hours': attendance.total_working_hours,
            'type': 'attendance',
        })

    # Prepare leave records manually with manager_name
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'manager_name': manager.manager_name,  # Include manager name
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'on leave'
            })

    # Combine attendance and leave records, and sort by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
    
    #new function added############################################################################################


@api_view(['GET'])
def admin_all_managers_attendance_history(request):
    # Get role, from_date and to_date from query params
    role = "manager"  # optional
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    # Get managers by role (if specified), otherwise all managers
    managers = Manager.objects.all()
    

    try:
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    all_records = []

    # Loop through each manager to gather attendance and leave records
    for manager in managers:
        attendance_query = Attendance.objects.filter(manager__role=role)
        leave_query = ManagerLeaveRequest.objects.filter(manager__role=role, status='approved')

        # Filter by date range
        if from_date and to_date:
            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )

        # Attendance records
        for attendance in attendance_query:
            all_records.append({
                'id': attendance.id,
                'manager_id': manager.manager_id,
                'manager_name': manager.manager_name,
                'date': attendance.date.strftime('%Y-%m-%d'),
                'time_in': attendance.time_in,
                'time_out': attendance.time_out,
                'in_status': attendance.in_status,
                'out_status': attendance.out_status,
                'overtime': attendance.overtime,
                'total_working_hours': attendance.total_working_hours,
                'type': 'attendance',
            })

        # Leave records
        for leave in leave_query:
            leave_days = (leave.end_date - leave.start_date).days + 1
            for i in range(leave_days):
                leave_date = leave.start_date + timedelta(days=i)
                if not from_date or (from_date <= leave_date <= to_date):
                    all_records.append({
                        'manager_id': manager.manager_id,
                        'manager_name': manager.manager_name,
                        'date': leave_date.strftime('%Y-%m-%d'),
                        'type': 'on leave'
                    })

    # Sort all records by date
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date,
        'role_filter': role
    }, status=status.HTTP_200_OK)
  

    #new function added############################################################################################

@api_view(['GET'])
def admin_all_hrs_attendance_history(request):
    # Get role, from_date and to_date from query params
    role = "hr"  # optional
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    # Get managers by role (if specified), otherwise all managers
    hrs = Hr.objects.all()
    

    try:
        if from_date and to_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    all_records = []

    # Loop through each manager to gather attendance and leave records
    for hr in hrs:
        attendance_query = Attendance.objects.filter(hr__role=role)
        leave_query = HrLeaveRequest.objects.filter(hr__role=role, status='approved')

        # Filter by date range
        if from_date and to_date:
            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )

        # Attendance records
        for attendance in attendance_query:
            all_records.append({
                'id': attendance.id,
                'hr_id': hr.hr_id,
                'hr_name': hr.hr_name,
                'date': attendance.date.strftime('%Y-%m-%d'),
                'time_in': attendance.time_in,
                'time_out': attendance.time_out,
                'in_status': attendance.in_status,
                'out_status': attendance.out_status,
                'overtime': attendance.overtime,
                'total_working_hours': attendance.total_working_hours,
                'type': 'attendance',
            })

        # Leave records
        for leave in leave_query:
            leave_days = (leave.end_date - leave.start_date).days + 1
            for i in range(leave_days):
                leave_date = leave.start_date + timedelta(days=i)
                if not from_date or (from_date <= leave_date <= to_date):
                    all_records.append({
                        'hr_id': hr.hr_id,
                        'hr_name': hr.hr_name,
                        'date': leave_date.strftime('%Y-%m-%d'),
                        'type': 'on leave'
                    })

    # Sort all records by date
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date,
        'role_filter': role
    }, status=status.HTTP_200_OK)
  

@api_view(['GET'])
def manager_weekly_attendance_chart(request,user_id):
    # user_id = request.session.get('user_id')  # Assuming employee ID is stored in session
    
    try:
        # Get the current week offset from GET parameters (how many weeks to move forward/backward)
        week_offset = int(request.GET.get('week_offset', 0))
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Adjust the week by the offset
        end_of_week = start_of_week + timedelta(days=6)

        # Initialize a dictionary to store total hours per day with the date
        weekly_hours = {}
        labels = []
        
        # Variables to store total hours for the week and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Populate the days of the week (Monday to Saturday)
        for i in range(6):  # Monday to Saturday
            day_date = start_of_week + timedelta(days=i)
            day_label = day_date.strftime('%a %b %d')  # Format: "Mon Sep 11"
            labels.append(day_label)
            weekly_hours[day_label] = 0  # Initialize the hours for each day as 0

        # Get all attendance entries for the selected week
        attendance_records = Attendance.objects.filter(
            manager__manager_id=user_id,
            date__range=[start_of_week, end_of_week]
        )

        # Get all approved leave requests for the selected week
        approved_leaves = ManagerLeaveRequest.objects.filter(
            manager__manager_id=user_id,
            start_date__lte=end_of_week,
            end_date__gte=start_of_week,
            status='approved'
        )

        leave_days = set()
        for leave in approved_leaves:
            # Iterate through the leave days within the week
            leave_start = max(leave.start_date, start_of_week)
            leave_end = min(leave.end_date, end_of_week)
            for i in range((leave_end - leave_start).days + 1):
                leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
                leave_days.add(leave_day)

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                # Convert time_in and time_out to datetime and calculate work duration
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                day_label = record.date.strftime('%a %b %d')  # Ensure record.date is also handled as date
                if day_label in weekly_hours:
                    weekly_hours[day_label] += work_duration

                # Calculate total hours and overtime
                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Get the current month
        current_month = start_of_week.strftime('%B')

        work_data = list(weekly_hours.values())
        leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

        # Prepare the response data
        response_data = {
            'labels': labels,  # List of days with their respective dates
            'work_data': work_data,  # Corresponding hours worked
            'month': current_month,
            'leave_data': leave_data,  # Days where the employee was on leave
            'week_offset': week_offset,  # Current week offset for navigation
            'total_hours': total_hours,  # Total hours worked in the week
            'total_overtime': total_overtime,  # Total overtime worked in the week
        }

        # Return the success response with status 200
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError:
        # Handle errors related to invalid week_offset
        error_data = {
            'message': 'Invalid week_offset parameter. Please provide a valid integer value.'
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        error_data = {
            'message': 'An unexpected error occurred.',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def employee_weekly_attendance(request,user_id):
    # Get the user ID from the session or request
    # user_id = query_params.get('user_id')
    # print (user_id ,"natha da kiyala")
    # if not user_id:
    #     return Response({"error": "User not authenticated."}, status=401)

    # Get the current week offset from query parameters
    week_offset = int(request.query_params.get('week_offset', 0))

    # Calculate the start and end dates for the target week
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # Initialize data structures
    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  # Standard working hours per day

    # Initialize labels and weekly_hours for each day of the week
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        day_label = day_date.strftime('%a %b %d')
        labels.append(day_label)
        weekly_hours[day_label] = 0

    # Fetch attendance, permissions, and leave data
    attendance_records = Attendance.objects.filter(
        employee__employee_id=user_id,
        date__range=[start_of_week, end_of_week]
    )
    permission_records = PermissionHour.objects.filter(
        employee__employee_id=user_id,
        date__range=[start_of_week, end_of_week],
        status='Approved'
    )
    approved_leaves = LeaveRequest.objects.filter(
        employee__employee_id=user_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    # Track leave days
    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
            leave_days.add(leave_day)

    # Process attendance records
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) -
            datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    # Process permission records
    permission_hours = {label: 0 for label in labels}
    for permission in permission_records:
        permission_duration = (
            datetime.combine(datetime.today(), permission.end_time) -
            datetime.combine(datetime.today(), permission.start_time)
        ).total_seconds() / 3600
        day_label = permission.date.strftime('%a %b %d')
        if day_label in permission_hours:
            permission_hours[day_label] += permission_duration

    # Prepare data for the API response
    work_data = list(weekly_hours.values())
    permission_data = list(permission_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Construct the response
    response_data = {
        'labels': labels,
        'work_data': work_data,
        'permission_data': permission_data,
        'leave_data': leave_data,
        'week_offset': week_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
    }

    return Response(response_data)


@api_view(['GET', 'POST'])
def show_employees_weekly_chart(request):
    try:
        # Step 1: Handle POST request for form submission (employee ID)
        if request.method == 'POST':
            employee_id = request.data.get('employee_id')  # Get employee ID from request body
        else:
            # Step 2: Handle GET request for week navigation
            employee_id = request.GET.get('employee_id')  # Get employee ID from query parameters

        # Step 3: Check if employee_id is provided
        if not employee_id:
            return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 4: Get the current week offset from GET parameters (how many weeks to move forward/backward)
        week_offset = int(request.GET.get('week_offset', 0))  # Default to current week if no offset

        # Step 5: Calculate the start and end of the week based on today’s date
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Step 6: Initialize variables for weekly data
        weekly_hours = {}  # Dictionary to store total hours per day
        labels = []  # Days of the week
        total_hours = 0  # Total worked hours for the week
        total_overtime = 0  # Total overtime for the week
        daily_working_hours = 8  # Standard working hours per day

        # Step 7: Generate labels and initialize weekly_hours for each day of the week
        for i in range(7):  # Iterate through Monday to Sunday
            day_date = start_of_week + timedelta(days=i)
            day_label = day_date.strftime('%a %b %d')  # Format: "Mon Sep 11"
            labels.append(day_label)
            weekly_hours[day_label] = 0  # Initialize hours for the day

        # Step 8: Retrieve attendance records for the selected employee and week
        attendance_records = Attendance.objects.filter(
            employee__employee_id=employee_id,  # Filter by Employee ID
            date__range=[start_of_week, end_of_week]  # Filter by date range (week)
        )

        # Step 9: Retrieve approved leave requests for the same employee and week
        approved_leaves = LeaveRequest.objects.filter(
            employee__employee_id=employee_id,
            status='approved',
            start_date__lte=end_of_week,
            end_date__gte=start_of_week
        )

        # Step 10: Track leave days (for charting)
        leave_days = set()
        for leave in approved_leaves:
            leave_start = max(leave.start_date, start_of_week)
            leave_end = min(leave.end_date, end_of_week)
            for i in range((leave_end - leave_start).days + 1):
                leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
                leave_days.add(leave_day)

        # Step 11: Calculate total worked hours and overtime
        for record in attendance_records:
            if record.time_in and record.time_out:
                # Calculate work duration in hours
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                day_label = record.date.strftime('%a %b %d')  # e.g. 'Mon Sep 11'
                if day_label in weekly_hours:
                    weekly_hours[day_label] += work_duration  # Add work hours to the corresponding day

                total_hours += work_duration  # Accumulate total hours worked
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours  # Calculate overtime

        # Round total hours and overtime for precision
        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Step 12: Get the current month (for display)
        current_month = start_of_week.strftime('%B')

        # Step 13: Prepare the data for the chart
        work_data = list(weekly_hours.values())  # List of worked hours for each day
        leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]  # Leave data

        # Step 14: Prepare the response data
        response_data = {
            'labels': labels,  # List of formatted days
            'data': work_data,  # Hours worked data
            'leave_data': leave_data,  # Leave days data
            'month': current_month,  # Current month (for display)
            'week_offset': week_offset,  # Week offset for navigation
            'total_hours': total_hours,  # Total worked hours
            'total_overtime': total_overtime,  # Total overtime
            'employee_id': employee_id,  # Employee ID for reference
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    
@api_view(['GET'])
def employee_monthly_attendance_chart(request,user_id):
    # user_id = request.session.get('user_id')
    try:
        # Retrieve employee ID from session
        
        # if not user_id:
            # return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get month offset from query parameters
        try:
            month_offset = int(request.GET.get('month_offset', 0))
        except ValueError:
            return Response({'error': 'Invalid month_offset parameter. It must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the target month and year
        today = datetime.now()
        target_month = today.month + month_offset
        target_year = today.year

        # Adjust for year overflow/underflow
        if target_month < 1:
            target_month += 12
            target_year -= 1
        elif target_month > 12:
            target_month -= 12
            target_year += 1

        # Determine the start and end of the target month
        start_of_month = datetime(target_year, target_month, 1)
        last_day = monthrange(target_year, target_month)[1]
        end_of_month = datetime(target_year, target_month, last_day)

        # Initialize data structures
        labels = [f"Week {i + 1}" for i in range(4)]
        weekly_hours = [0] * 4
        permission_hours = [0] * 4
        leave_days = [0] * 4
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Fetch relevant records
        attendance_records = Attendance.objects.filter(
            employee__employee_id=user_id,
            date__range=[start_of_month, end_of_month]
        )
        permission_records = PermissionHour.objects.filter(
            employee__employee_id=user_id,
            date__range=[start_of_month, end_of_month],
            status='Approved'
        )
        approved_leaves = LeaveRequest.objects.filter(
            employee__employee_id=user_id,
            status='approved',
            start_date__lte=end_of_month,
            end_date__gte=start_of_month
        )

        # Process attendance records
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = (datetime.combine(datetime.today(), record.time_out) -
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                week_num = (record.date.day - 1) // 7
                if week_num < 4:
                    weekly_hours[week_num] += work_duration
                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        # Process permission records
        for permission in permission_records:
            permission_duration = (
                datetime.combine(datetime.today(), permission.end_time) -
                datetime.combine(datetime.today(), permission.start_time)
            ).total_seconds() / 3600
            week_num = (permission.date.day - 1) // 7
            if week_num < 4:
                permission_hours[week_num] += permission_duration

        # Process leave records
        for leave in approved_leaves:
            leave_start = max(leave.start_date, start_of_month.date())
            leave_end = min(leave.end_date, end_of_month.date())
            while leave_start <= leave_end:
                week_num = (leave_start.day - 1) // 7
                if week_num < 4:
                    leave_days[week_num] += 1
                leave_start += timedelta(days=1)

        # Prepare response data
        response_data = {
            'labels': labels,
            'work_data': weekly_hours,
            'permission_data': permission_hours,
            'leave_data': leave_days,
            'month_offset': month_offset,
            'total_hours': round(total_hours, 2),
            'total_overtime': round(total_overtime, 2),
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

@api_view(['GET'])
def employee_yearly_attendance_chart(request):
    try:
        # Assuming employee ID is stored in the session
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current year offset from GET parameters (how many years to move forward/backward)
        year_offset = int(request.GET.get('year_offset', 0))

        # Get today's date and adjust the year by the offset
        today = datetime.now()
        current_year = today.year + year_offset

        # Initialize data structures to store monthly hours, permission hours, and leave data
        monthly_hours = [0] * 12  # For 12 months
        monthly_working_days = [0] * 12  # To track the number of working days per month
        monthly_permission_hours = [0] * 12  # To track permission hours per month
        monthly_leave_days = [0] * 12  # To track leave days
        month_labels = [datetime(current_year, i + 1, 1).strftime('%B') for i in range(12)]  # Month names

        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Get attendance records for the employee during the selected year
        attendance_records = Attendance.objects.filter(
            employee__employee_id=user_id,
            date__year=current_year
        )

        # Get permission hour records for the employee during the selected year
        permission_records = PermissionHour.objects.filter(
            employee__employee_id=user_id,
            date__year=current_year,
            status='Approved'  # Include only approved permission hours
        )

        # Get approved leave requests for the selected year
        approved_leaves = LeaveRequest.objects.filter(
            employee__employee_id=user_id,
            status='approved',
            start_date__year=current_year
        )

        # Process attendance records
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = datetime.combine(datetime.today(), record.time_out) - datetime.combine(datetime.today(), record.time_in)
                hours_worked = work_duration.total_seconds() / 3600  # Convert seconds to hours

                # Determine the month (0-based index for the list)
                month_num = record.date.month - 1

                monthly_hours[month_num] += hours_worked
                monthly_working_days[month_num] += 1  # Increment the count of working days for this month

                total_hours += hours_worked
                if hours_worked > daily_working_hours:
                    total_overtime += hours_worked - daily_working_hours

        # Process permission records
        for permission in permission_records:
            month_num = permission.date.month - 1
            permission_duration = (
                datetime.combine(datetime.today(), permission.end_time) - 
                datetime.combine(datetime.today(), permission.start_time)
            ).total_seconds() / 3600  # Convert seconds to hours
            monthly_permission_hours[month_num] += permission_duration

        # Process leave records
        for leave in approved_leaves:
            leave_start = leave.start_date
            leave_end = leave.end_date
            current_month = leave_start.month
            while leave_start <= leave_end:
                if leave_start.year == current_year:
                    month_num = leave_start.month - 1
                    monthly_leave_days[month_num] += 1
                leave_start += timedelta(days=1)

        total_hours = round(total_hours, 3)
        total_overtime = round(total_overtime, 3)

        # Prepare response data
        response_data = {
            'year': current_year,  # Current year
            'labels': month_labels,  # Month labels for the chart
            'monthly_hours': monthly_hours,  # Total working hours per month
            'monthly_permission_hours': monthly_permission_hours,  # Total permission hours per month
            'monthly_leave_days': monthly_leave_days,  # Total leave days per month
            'total_hours': total_hours,  # Total hours worked in the year
            'total_overtime': total_overtime,  # Total overtime worked in the year
            'year_offset': year_offset,  # Pass the current year offset for navigation
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    
@api_view(['GET'])
def manager_monthly_attendance_chart(request,user_id):
    try:
        # Assuming manager ID is stored in the session
        # user_id = request.session.get('user_id')
        # if not user_id:
        #     return Response({'error': 'Manager ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current month offset from GET parameters (how many months to move forward/backward)
        month_offset = int(request.GET.get('month_offset', 0))

        # Get today's date and adjust the month by the offset
        today = datetime.now()
        current_month = today.month + month_offset
        current_year = today.year

        # Handle year overflow/underflow when adjusting months
        if current_month < 1:
            current_month += 12
            current_year -= 1
        elif current_month > 12:
            current_month -= 12
            current_year += 1

        # Determine the first and last day of the month
        start_of_month = datetime(current_year, current_month, 1)
        last_day = monthrange(current_year, current_month)[1]  # Get the number of days in the month
        end_of_month = datetime(current_year, current_month, last_day)

        # Initialize data structures to store weekly hours and leave information
        weekly_hours = [0, 0, 0, 0]  # For 4 weeks
        working_days_per_week = [0, 0, 0, 0]  # To track the number of working days per week
        week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]  # Week labels
        
        # Variables to store total hours for the month and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Get all attendance entries for the selected month
        attendance_records = Attendance.objects.filter(
            manager__manager_id=user_id,
            date__range=[start_of_month, end_of_month]
        )

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = datetime.combine(datetime.today(), record.time_out) - datetime.combine(datetime.today(), record.time_in)
                hours_worked = work_duration.total_seconds() / 3600  # Convert seconds to hours

                # Determine which week the record falls into (1-7 = Week 1, etc.)
                week_num = (record.date.day - 1) // 7  # Get week number (0, 1, 2, or 3)
                if week_num < 4:  # Ensure we don't go beyond Week 4
                    weekly_hours[week_num] += hours_worked
                    working_days_per_week[week_num] += 1  # Increment the count of working days for this week

                # Calculate total hours and overtime
                total_hours += hours_worked
                if hours_worked > daily_working_hours:
                    total_overtime += hours_worked - daily_working_hours

        total_hours = round(total_hours, 3)
        total_overtime = round(total_overtime, 3)

        # Calculate the average hours per week by dividing the total hours by the number of working days
        average_hours_per_week = []
        for week_num in range(4):
            if working_days_per_week[week_num] > 0:
                avg_hours = weekly_hours[week_num] / working_days_per_week[week_num]
            else:
                avg_hours = 0
            average_hours_per_week.append(round(avg_hours, 2))

        # Zip the week labels with the average working hours to pass them together in the response
        week_avg_data = list(zip(week_labels, average_hours_per_week))

        # Get the month name for display
        current_month_name = start_of_month.strftime('%B')

        # Prepare response data
        response_data = {
            'month': current_month_name,  # Current month name
            'week_avg_data': week_avg_data,  # Pass the zipped week labels and average hours
            'total_hours': total_hours,  # Total hours worked in the month
            'total_overtime': total_overtime,  # Total overtime worked in the month
            'month_offset': month_offset,  # Pass the current month offset for navigation
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    
    
    
@api_view(['GET'])
def show_employees_monthly_chart(request):
    try:
        # Retrieve employee ID from the GET parameters
        employee_id = request.GET.get('employee_id')
        if not employee_id:
            return Response({'error': 'Employee ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the month offset from GET parameters (how many months to move forward/backward)
        month_offset = int(request.GET.get('month_offset', 0))
        today = datetime.now().date()
        current_month = today.month + month_offset
        current_year = today.year

        if current_month < 1:
            current_month += 12
            current_year -= 1
        elif current_month > 12:
            current_month -= 12
            current_year += 1

        # Determine the start and end of the month
        start_of_month = datetime(current_year, current_month, 1)
        last_day = monthrange(current_year, current_month)[1]
        end_of_month = datetime(current_year, current_month, last_day)

        # Initialize weekly hours and leave data
        weekly_hours = [0] * 4  # For 4 weeks in a month
        leave_weeks = [0] * 4  # To track leave days per week
        week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8

        # Get attendance records for the employee during the selected month
        attendance_records = Attendance.objects.filter(
            employee__employee_id=employee_id,
            date__range=[start_of_month.date(), end_of_month.date()]
        )

        # Calculate total working hours and overtime for each week
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                week_num = (record.date.day - 1) // 7
                if week_num < 4:
                    weekly_hours[week_num] += work_duration

                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Calculate weekly averages
        weekly_averages = [0] * 4
        for week_num in range(4):
            if leave_weeks[week_num] == 0 and weekly_hours[week_num] > 0:
                # Count the working days in that week
                working_days = Attendance.objects.filter(
                    employee__employee_id=employee_id,
                    date__range=[start_of_month.date() + timedelta(weeks=week_num),
                                 start_of_month.date() + timedelta(weeks=week_num + 1) - timedelta(days=1)],
                    time_in__isnull=False,
                    time_out__isnull=False
                ).count()
                if working_days > 0:
                    weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

        # Prepare response data
        response_data = {
            'labels': week_labels,
            'data': weekly_hours,
            'month': start_of_month.strftime('%B'),
            'month_offset': month_offset,
            'total_hours': total_hours,
            'total_overtime': total_overtime,
            'employee_id': employee_id,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    
@api_view(['POST'])
def request_permission_hours(request):
    try:
        # Get the data from the POST request
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        reason = request.data.get('reason')

        # Validate that all required fields are present
        if not date or not start_time or not end_time or not reason:
            return Response({'error': 'All fields are required (date, start_time, end_time, reason).'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate that the start time is earlier than the end time
        if start_time >= end_time:
            return Response({'error': 'Start time must be before end time.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the employee from the session (assuming session-based authentication)
        try:
            employee = Employee.objects.get(employee_id=request.session['user_id'])
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found. Please log in again.'}, status=status.HTTP_404_NOT_FOUND)

        # Create the PermissionHour record
        permission_hour = PermissionHour.objects.create(
            employee=employee,
            date=date,
            start_time=start_time,
            end_time=end_time,
            reason=reason
        )

        return Response({'message': 'Permission hours request submitted successfully.'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Return a 500 internal server error if something goes wrong
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['PUT'])
def update_permission_hour(request, id):
    try:
        # Retrieve the specific PermissionHour object by ID
        permission_hour = PermissionHour.objects.get(id=id)
        
        # Retrieve updated data from the request
        start_time = request.data.get('start_time', permission_hour.start_time)
        end_time = request.data.get('end_time', permission_hour.end_time)
        reason = request.data.get('reason', permission_hour.reason)
        
        # Validate logical consistency (start time must be before end time)
        if start_time >= end_time:
            return Response({"error": "Start time must be before end time."}, status=400)
        
        # Update the permission hour fields
        permission_hour.start_time = start_time
        permission_hour.end_time = end_time
        permission_hour.reason = reason
        permission_hour.save()
        
        return Response({"message": "Permission hour request updated successfully."}, status=200)
    
    except PermissionHour.DoesNotExist:
        return Response({"error": "Permission hour request not found."}, status=404)

@api_view(['DELETE'])
def delete_permission_hour(request, id):
    try:
        # Retrieve the specific PermissionHour object by ID
        permission_hour = PermissionHour.objects.get(id=id)
        
        # Delete the permission hour request
        permission_hour.delete()
        
        return Response({"message": "Permission hour request deleted successfully."}, status=204)
    
    except PermissionHour.DoesNotExist:
        return Response({"error": "Permission hour request not found."}, status=404)


@api_view(['GET'])
def get_permission_hours(request):
    try:
        # Retrieve the employee from the session
        employee = Employee.objects.get(employee_id=request.session['user_id'])
        
        # Get all permission hour requests for this employee
        permission_hours = PermissionHour.objects.filter(employee=employee)
        
        # Create a response with the list of permission hours
        data = [
            {
                'id': ph.id,
                'date': ph.date,
                'start_time': ph.start_time,
                'end_time': ph.end_time,
                'reason': ph.reason
            }
            for ph in permission_hours
        ]
        
        return Response(data, status=200)
    
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)   
    


@api_view(['GET'])
def get_all_permission_hours(request):
    try:
        # Retrieve all employees
        employees = Employee.objects.all()

        # Create a list to accumulate all permission hour data
        all_permission_hours = []

        for employee in employees:
            # Get all permission hours for this employee
            permission_hours = PermissionHour.objects.filter(employee=employee)

            # Add each permission hour entry for the employee to the list
            for ph in permission_hours:
                all_permission_hours.append({
                    'id': ph.id,
                    'employee_id': employee.id,  # Add employee ID to know which employee the hours belong to
                    'date': ph.date,
                    'start_time': ph.start_time,
                    'end_time': ph.end_time,
                    'reason': ph.reason,
                    'status':ph.status
                })

        # Return the list of all permission hours as the response
        return Response(all_permission_hours, status=200)

    except Employee.DoesNotExist:
        return Response({"error": "Employee not found."}, status=404)

    
@api_view(['GET'])
def manage_permission_hours(request):
    try:
        # Fetch all permission hour requests with 'Pending' status
        pending_requests = PermissionHour.objects.filter(status='Pending')

        # Prepare the data to be returned in JSON format
        data = [
            {
                'id': request.id,
                'employee_id': request.employee.employee_id,
                'date': request.date,
                'start_time': request.start_time,
                'end_time': request.end_time,
                'reason': request.reason,
                'status': request.status
            }
            for request in pending_requests
        ]

        # Return a JSON response with the list of pending requests
        return Response(data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        # Handle case when no permission hour requests are found or some other db issue occurs
        return Response({"error": "No pending permission hour requests found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # General error handler
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(['POST'])
def approve_permission_hour(request, permission_id):
    try:
        # Retrieve the permission hour object by ID
        permission = PermissionHour.objects.get(id=permission_id)

        # Get the action (approve or reject) from the POST request
        action = request.data.get('action')

        # Ensure 'action' is either 'approve' or 'reject'
        if action not in ['approve', 'reject']:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'approve':
            # Update the permission status to 'Approved'
            permission.status = 'Approved'
            
            # Calculate the duration of permission hours
            start_time = datetime.combine(datetime.min, permission.start_time)
            end_time = datetime.combine(datetime.min, permission.end_time)
            permission_duration = end_time - start_time

            # Save the duration in the PermissionHour table
            permission.duration = permission_duration

            # Send approval email to the employee
            send_mail(
                'Permission Request Approved',
                f'Your permission request for {permission_duration} hours on {permission.date} has been approved.',
                'admin@example.com',
                [permission.employee.email]
            )

        elif action == 'reject':
            # Update the permission status to 'Rejected'
            permission.status = 'Rejected'

            # Send rejection email to the employee
            send_mail(
                'Permission Request Rejected',
                f'Your permission request on {permission.date} has been rejected.',
                'admin@example.com',
                [permission.employee.email]
            )

        # Save the changes to the database
        permission.save()

        return Response({"message": f"Permission request has been {permission.status.lower()}."}, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        # If the permission hour is not found
        return Response({"error": "Permission request not found."}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # General exception handling for any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def get_permission_hour(request, permission_id):
    try:
        permission = PermissionHour.objects.get(id=permission_id)
        data = {
            'id': permission.id,
            'employee_id': permission.employee.employee_id,
            'date': permission.date,
            'start_time': permission.start_time,
            'end_time': permission.end_time,
            'status': permission.status,
            'reason': permission.reason,
            'duration': permission.duration
        }
        return Response(data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({"error": "Permission hour request not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['PUT'])
def update_permission_hour(request, permission_id):
    try:
        permission = PermissionHour.objects.get(id=permission_id)

        # Get updated fields from the request
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        reason = request.data.get('reason')

        # Validate the logic of start and end times
        if start_time >= end_time:
            return Response({"error": "Start time must be before end time."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the fields
        permission.start_time = start_time
        permission.end_time = end_time
        permission.reason = reason

        # Recalculate the duration
        start_time_obj = datetime.combine(datetime.min, permission.start_time)
        end_time_obj = datetime.combine(datetime.min, permission.end_time)
        permission.duration = end_time_obj - start_time_obj

        # Save the updated request
        permission.save()

        return Response({"message": "Permission hour request updated successfully."}, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        return Response({"error": "Permission hour request not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
@api_view(['DELETE'])
def delete_permission_hour(request, permission_id):
    try:
        permission = PermissionHour.objects.get(id=permission_id)
        permission.delete()
        return Response({"message": "Permission hour request deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except ObjectDoesNotExist:
        return Response({"error": "Permission hour request not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
##############################################################################################

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Schedule, Manager, Employee
from .serializers import AttendanceSerializer, CalendarEventSerializer, ScheduleSerializer
from datetime import datetime, timedelta

@api_view(['GET'])
def interview_schedule(request):
    """
    Fetch all interview schedules.
    """
    schedules = Schedule.objects.all()
    serializer = ScheduleSerializer(schedules, many=True)
    return Response(serializer.data)


# GET: Fetch a single interview schedule by ID


@api_view(['POST'])
def add_interview_schedule(request):
    serializer = ScheduleSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "interview schedule added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# PUT: Update an existing interview schedule by ID
@api_view(['PUT'])
def interview_schedule_update(request, id):
    schedule = Schedule.objects.get(id=id)
    serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "interview Update dated successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Delete an interview schedule by ID
@api_view(['DELETE'])
def interview_schedule_delete(request, id):
    """
    Delete an interview schedule by ID.
    """
    try:
        schedule = Schedule.objects.get(id=id)
    except Schedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)

    schedule.delete()  # Delete the schedule
    return Response({'message': 'Schedule deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def interview_schedule_detail(request, id):
    """
    Fetch a single interview schedule by ID.
    """
    try:
        schedule = Schedule.objects.get(id=id)
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data)
    except Schedule.DoesNotExist:
        return Response({'error': 'Schedule not found.'}, status=status.HTTP_404_NOT_FOUND)






####################################################################
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import DepartmentActiveJob
from .serializers import DepartmentActiveJobSerializer

# GET: List all active department jobs
# GET: List all active department jobs
@api_view(['GET'])
def department_active_jobs(request):
    """
    Get all department active job openings.
    """
    jobs = DepartmentActiveJob.objects.all()
    serializer = DepartmentActiveJobSerializer(jobs, many=True)
    return Response(serializer.data)

# GET: Get a specific department active job opening by ID
@api_view(['GET'])
def get_department_active_job(request, job_id):
    """
    Get a department active job opening by ID.
    """
    try:
        job = DepartmentActiveJob.objects.get(id=job_id)
    except DepartmentActiveJob.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentActiveJobSerializer(job)
    return Response(serializer.data)

# POST: Create a new active department job opening
@api_view(['POST'])
def add_department_active_job(request):
    """
    Add a new department active job opening.
    """
    serializer = DepartmentActiveJobSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT: Update an existing department active job by ID
@api_view(['PUT'])
def update_department_active_job(request, job_id):
    """
    Update a department active job opening by ID.
    """
    try:
        job = DepartmentActiveJob.objects.get(id=job_id)
    except DepartmentActiveJob.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DepartmentActiveJobSerializer(job, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Delete a department active job by ID
@api_view(['DELETE'])
def delete_department_active_job(request, job_id):
    """
    Delete a department active job opening by ID.
    """
    try:
        job = DepartmentActiveJob.objects.get(id=job_id)
    except DepartmentActiveJob.DoesNotExist:
        return Response({'error': 'Job not found.'}, status=status.HTTP_404_NOT_FOUND)

    job.delete()
    return Response({'message': 'Job deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)






#calender event


##############################   API  ############################
# views.py
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CalendarEvent
from .serializers import CalendarEventSerializer

# GET: Retrieve all events
@api_view(['GET'])
def calendar_view(request):
    """
    Retrieve all calendar events.
    """
    events = CalendarEvent.objects.all()
    serializer = CalendarEventSerializer(events, many=True)
    return Response(serializer.data)
# GET: Retrieve a specific event by ID
@api_view(['GET'])
def get_event_by_id(request, id):
    """
    Retrieve a specific event by ID.
    """
    try:
        event = CalendarEvent.objects.get(id=id)
    except CalendarEvent.DoesNotExist:
        return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CalendarEventSerializer(event)
    return Response(serializer.data)

# POST: Add a new event
@api_view(['POST'])
def add_event(request):
    """
    Add a new calendar event.
    """
    serializer = CalendarEventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT: Update an existing event by ID
@api_view(['PUT'])
def update_event(request, id):
    """
    Update an existing event by ID.
    """
    try:
        event = CalendarEvent.objects.get(id=id)
    except CalendarEvent.DoesNotExist:
        return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CalendarEventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Delete an event by ID
@api_view(['DELETE'])
def delete_event(request, id):
    """
    Delete an event by ID.
    """
    try:
        event = CalendarEvent.objects.get(id=id)
    except CalendarEvent.DoesNotExist:
        return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)

    event.delete()
    return Response({'message': 'Event deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)



#offers

        
#####################################  API   ##############################
        
        
        
# views.py
# views.py
from rest_framework.decorators import api_view
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from .models import Offer
from .serializers import OfferSerializer
from django.shortcuts import get_object_or_404

# GET and POST: List and Create offers
@api_view(['GET', 'POST'])
def offer_list(request):
    if request.method == 'GET':
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers, many=True)
        return Response({
            'pending_offers': [offer for offer in serializer.data if offer['status'] == 'pending'],
            'accepted_offers': [offer for offer in serializer.data if offer['status'] == 'accepted'],
            'rejected_offers': [offer for offer in serializer.data if offer['status'] == 'rejected']
        })

    elif request.method == 'POST':
        serializer = OfferSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_offer_status(request, id):
    try:
        offer = Offer.objects.get(id=id)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    status = request.data.get('status')
    if status not in ['accepted', 'rejected']:
        return Response({'error': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    offer.status = status
    offer.save()
    return Response({'message': 'Offer status updated successfully.'})

@api_view(['GET'])
def get_offer_by_id(request, id):
    offer = get_object_or_404(Offer, id=id)
    serializer = OfferSerializer(offer)
    return Response(serializer.data)

@api_view(['DELETE'])
def delete_offer(request, id):
    try:
        offer = Offer.objects.get(id=id)
    except Offer.DoesNotExist:
        return Response({'error': 'Offer not found.'}, status=status.HTTP_404_NOT_FOUND)

    offer.delete()
    return Response({'message': 'Offer deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

def send_offer_email(offer):
    subject = f"Offer for {offer.position}"
    recipient_email = offer.email
    sender_email = settings.DEFAULT_FROM_EMAIL

    # Ensure the template exists at this path
    message = render_to_string('authentication/offer_email.html', {'offer': offer})

    try:
        send_mail(
            subject,
            message,
            sender_email,
            [recipient_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")

from .models import ProFeedback
from .serializers import ProFeedbackSerializer

# GET: Retrieve all feedback
@api_view(['GET'])
def feedback_list(request):
    """
    Retrieve all pending feedback records.
    """
    feedbacks = ProFeedback.objects.all()
    serializer = ProFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)

# GET: Retrieve specific feedback by ID
@api_view(['GET'])
def get_feedback(request, feedback_id):
    """
    Retrieve a specific feedback record by ID.
    """
    try:
        feedback = ProFeedback.objects.get(id=feedback_id)
    except ProFeedback.DoesNotExist:
        return Response({'error': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProFeedbackSerializer(feedback)
    return Response(serializer.data)

# POST: Add new feedback
@api_view(['POST'])
def add_feedback(request):
    """
    Add a new feedback record.
    """
    serializer = ProFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# PUT: Update existing feedback by ID
@api_view(['PUT'])
def update_feedback(request, feedback_id):
    """
    Update a feedback record by ID.
    """
    try:
        feedback = ProFeedback.objects.get(id=feedback_id)
    except ProFeedback.DoesNotExist:
        return Response({'error': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProFeedbackSerializer(feedback, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE: Delete feedback by ID
@api_view(['DELETE'])
def delete_feedback(request, feedback_id):
    """
    Delete a feedback record by ID.
    """
    try:
        feedback = ProFeedback.objects.get(id=feedback_id)
    except ProFeedback.DoesNotExist:
        return Response({'error': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

    feedback.delete()
    return Response({'message': 'Feedback deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


from .models import Shift_attendance
from .serializers import ShiftAttendanceSerializer
from rest_framework.decorators import APIView

    
# Shift Attendance API
class ShiftAttendanceListCreateAPIView(APIView):
    def get(self, request):
        shifts = Shift_attendance.objects.all()
        serializer = ShiftAttendanceSerializer(shifts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShiftAttendanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShiftAttendanceDetailAPIView(APIView):
    def get(self, request, pk):
        shift = Shift_attendance.objects.get(pk=pk)
        serializer = ShiftAttendanceSerializer(shift)
        return Response(serializer.data)

    def put(self, request, pk):
        shift = Shift_attendance.objects.get(pk=pk)
        serializer = ShiftAttendanceSerializer(shift, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        shift = Shift_attendance.objects.get(pk=pk)
        shift.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from datetime import datetime, timedelta
# from calendar import monthrange
# from .models import Attendance


# @api_view(['POST'])
# def admin_employee_weekly_chart(request):
#     employee_id = request.data.get('employee_id')
#     if not employee_id:
#         return Response({'error': 'Employee ID is required.'}, status=400)

#     week_offset = int(request.data.get('week_offset', 0))
    
#     today = datetime.now().date()
#     start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)

#     weekly_hours = {}
#     labels = []
#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8

#     for i in range(6):
#         day_date = start_of_week + timedelta(days=i)
#         labels.append(day_date.strftime('%a %b %d'))
#         weekly_hours[labels[-1]] = 0

#     attendance_records = Attendance.objects.filter(
#         employee__employee_id=employee_id,
#         date__range=[start_of_week, end_of_week]
#     )

#     approved_leaves = LeaveRequest.objects.filter(
#         employee__employee_id=employee_id,
#         status='approved',
#         start_date__lte=end_of_week,
#         end_date__gte=start_of_week
#     )

#     leave_days = set()
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_week)
#         leave_end = min(leave.end_date, end_of_week)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             day_label = record.date.strftime('%a %b %d')
#             if day_label in weekly_hours:
#                 weekly_hours[day_label] += work_duration
#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     work_data = list(weekly_hours.values())
#     leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

#     return Response({
#         'labels': labels,
#         'data': work_data,
#         'leave_data': leave_data,
#         'month': start_of_week.strftime('%B'),
#         'week_offset': week_offset,
#         'total_hours': round(total_hours, 2),
#         'total_overtime': round(total_overtime, 2),
#         'employee_id': employee_id,
#     })

# from datetime import datetime, timedelta
# from calendar import monthrange
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Attendance

# @api_view(['POST'])
# def admin_employee_monthly_chart(request):
#     employee_id = request.data.get('employee_id')
    
#     if not employee_id:
#         return Response({"error": "Employee ID is required."}, status=400)

#     month_offset = int(request.GET.get('month_offset', 0))
    
#     today = datetime.now().date()
#     current_month = today.month + month_offset
#     current_year = today.year

#     if current_month < 1:
#         current_month += 12
#         current_year -= 1
#     elif current_month > 12:
#         current_month -= 12
#         current_year += 1

#     start_of_month = datetime(current_year, current_month, 1).date()
#     last_day = monthrange(current_year, current_month)[1]
#     end_of_month = datetime(current_year, current_month, last_day).date()

#     weekly_hours = [0] * 4  # For 4 weeks in the month
#     leave_weeks = [0] * 4   # To track leave days per week
#     week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8  

#     # Get all attendance entries for the selected month
#     attendance_records = Attendance.objects.filter(
#         employee__employee_id=employee_id,
#         date__range=[start_of_month, end_of_month]
#     )

#     # Get approved leave requests overlapping with the selected month
#     approved_leaves = LeaveRequest.objects.filter(
#         employee__employee_id=employee_id,
#         status='approved',
#         start_date__lte=end_of_month,
#         end_date__gte=start_of_month
#     )

#     # Track leave days per week
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_month)
#         leave_end = min(leave.end_date, end_of_month)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_day = leave_start + timedelta(days=i)
#             week_num = (leave_day.day - 1) // 7
#             if week_num < 4:
#                 leave_weeks[week_num] += 1  # Increment leave count per week

#     # Calculate total working hours and overtime for each week
#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             week_num = (record.date.day - 1) // 7
#             if week_num < 4:
#                 weekly_hours[week_num] += work_duration

#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     total_hours = round(total_hours, 2)
#     total_overtime = round(total_overtime, 2)

#     # Calculate weekly averages
#     weekly_averages = [0] * 4
#     for week_num in range(4):
#         working_days = Attendance.objects.filter(
#             employee__employee_id=employee_id,
#             date__range=[start_of_month + timedelta(weeks=week_num),
#                          start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
#             time_in__isnull=False,
#             time_out__isnull=False
#         ).count()
#         if working_days > 0:
#             weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

#     current_month_name = start_of_month.strftime('%B')

#     # Prepare response data
#     response_data = {
#         'labels': week_labels,
#         'work_data': weekly_hours,
#         'leave_data': leave_weeks,  # Include leave data per week
#         'month': current_month_name,
#         'month_offset': month_offset,
#         'total_hours': total_hours,
#         'total_overtime': total_overtime,
#         'employee_id': employee_id,
#         'average_hours_per_week': total_hours / 4 if total_hours else 0,
#         'weekly_averages': weekly_averages,
#     }

#     return Response(response_data)


# @api_view(['POST'])
# def admin_manager_weekly_chart(request):
#     manager_id = request.data.get('manager_id')
#     if not manager_id:
#         return Response({'error': 'Manager ID is required.'}, status=400)

#     week_offset = int(request.data.get('week_offset', 0))
    
#     today = datetime.now().date()
#     start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)

#     weekly_hours = {}
#     labels = []
#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8

#     for i in range(6):
#         day_date = start_of_week + timedelta(days=i)
#         labels.append(day_date.strftime('%a %b %d'))
#         weekly_hours[labels[-1]] = 0

#     attendance_records = Attendance.objects.filter(
#         manager__manager_id=manager_id,
#         date__range=[start_of_week, end_of_week]
#     )

#     approved_leaves = ManagerLeaveRequest.objects.filter(
#         manager__manager_id=manager_id,
#         status='approved',
#         start_date__lte=end_of_week,
#         end_date__gte=start_of_week
#     )

#     leave_days = set()
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_week)
#         leave_end = min(leave.end_date, end_of_week)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             day_label = record.date.strftime('%a %b %d')
#             if day_label in weekly_hours:
#                 weekly_hours[day_label] += work_duration
#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     work_data = list(weekly_hours.values())
#     leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

#     return Response({
#         'labels': labels,
#         'data': work_data,
#         'leave_data': leave_data,
#         'month': start_of_week.strftime('%B'),
#         'week_offset': week_offset,
#         'total_hours': round(total_hours, 2),
#         'total_overtime': round(total_overtime, 2),
#         'manager_id': manager_id,
#     })

# @api_view(['POST'])
# def admin_manager_monthly_chart(request):
#     manager_id = request.data.get('manager_id')
    
#     if not manager_id:
#         return Response({"error": "Employee ID is required."}, status=400)

#     month_offset = int(request.GET.get('month_offset', 0))
    
#     today = datetime.now().date()
#     current_month = today.month + month_offset
#     current_year = today.year

#     if current_month < 1:
#         current_month += 12
#         current_year -= 1
#     elif current_month > 12:
#         current_month -= 12
#         current_year += 1

#     start_of_month = datetime(current_year, current_month, 1).date()
#     last_day = monthrange(current_year, current_month)[1]
#     end_of_month = datetime(current_year, current_month, last_day).date()

#     weekly_hours = [0] * 4  # For 4 weeks in the month
#     leave_weeks = [0] * 4   # To track leave days per week
#     week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8  

#     # Get all attendance entries for the selected month
#     attendance_records = Attendance.objects.filter(
#         manager__manager_id=manager_id,
#         date__range=[start_of_month, end_of_month]
#     )

#     # Get approved leave requests overlapping with the selected month
#     approved_leaves = ManagerLeaveRequest.objects.filter(
#         manager__manager_id=manager_id,
#         status='approved',
#         start_date__lte=end_of_month,
#         end_date__gte=start_of_month
#     )

#     # Track leave days per week
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_month)
#         leave_end = min(leave.end_date, end_of_month)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_day = leave_start + timedelta(days=i)
#             week_num = (leave_day.day - 1) // 7
#             if week_num < 4:
#                 leave_weeks[week_num] += 1  # Increment leave count per week

#     # Calculate total working hours and overtime for each week
#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             week_num = (record.date.day - 1) // 7
#             if week_num < 4:
#                 weekly_hours[week_num] += work_duration

#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     total_hours = round(total_hours, 2)
#     total_overtime = round(total_overtime, 2)

#     # Calculate weekly averages
#     weekly_averages = [0] * 4
#     for week_num in range(4):
#         working_days = Attendance.objects.filter(
#             manager__manager_id=manager_id,
#             date__range=[start_of_month + timedelta(weeks=week_num),
#                          start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
#             time_in__isnull=False,
#             time_out__isnull=False
#         ).count()
#         if working_days > 0:
#             weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

#     current_month_name = start_of_month.strftime('%B')

#     # Prepare response data
#     response_data = {
#         'labels': week_labels,
#         'work_data': weekly_hours,
#         'leave_data': leave_weeks,  # Include leave data per week
#         'month': current_month_name,
#         'month_offset': month_offset,
#         'total_hours': total_hours,
#         'total_overtime': total_overtime,
#         'manager_id': manager_id,
#         'average_hours_per_week': total_hours / 4 if total_hours else 0,
#         'weekly_averages': weekly_averages,
#     }

#     return Response(response_data)

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from datetime import datetime, timedelta
# from calendar import monthrange
# from .models import Attendance


# @api_view(['POST'])
# def admin_employee_weekly_chart(request):
#     employee_id = request.data.get('employee_id')
#     if not employee_id:
#         return Response({'error': 'Employee ID is required.'}, status=400)

#     week_offset = int(request.data.get('week_offset', 0))
    
#     today = datetime.now().date()
#     start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)

#     weekly_hours = {}
#     labels = []
#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8

#     for i in range(6):
#         day_date = start_of_week + timedelta(days=i)
#         labels.append(day_date.strftime('%a %b %d'))
#         weekly_hours[labels[-1]] = 0

#     attendance_records = Attendance.objects.filter(
#         employee__employee_id=employee_id,
#         date__range=[start_of_week, end_of_week]
#     )

#     approved_leaves = LeaveRequest.objects.filter(
#         employee__employee_id=employee_id,
#         status='approved',
#         start_date__lte=end_of_week,
#         end_date__gte=start_of_week
#     )

#     leave_days = set()
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_week)
#         leave_end = min(leave.end_date, end_of_week)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             day_label = record.date.strftime('%a %b %d')
#             if day_label in weekly_hours:
#                 weekly_hours[day_label] += work_duration
#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     work_data = list(weekly_hours.values())
#     leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

#     return Response({
#         'labels': labels,
#         'data': work_data,
#         'leave_data': leave_data,
#         'month': start_of_week.strftime('%B'),
#         'week_offset': week_offset,
#         'total_hours': round(total_hours, 2),
#         'total_overtime': round(total_overtime, 2),
#         'employee_id': employee_id,
#     })

# from datetime import datetime, timedelta
# from calendar import monthrange
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Attendance

# @api_view(['POST'])
# def admin_employee_monthly_chart(request):
#     employee_id = request.data.get('employee_id')
    
#     if not employee_id:
#         return Response({"error": "Employee ID is required."}, status=400)

#     month_offset = int(request.GET.get('month_offset', 0))
    
#     today = datetime.now().date()
#     current_month = today.month + month_offset
#     current_year = today.year

#     if current_month < 1:
#         current_month += 12
#         current_year -= 1
#     elif current_month > 12:
#         current_month -= 12
#         current_year += 1

#     start_of_month = datetime(current_year, current_month, 1).date()
#     last_day = monthrange(current_year, current_month)[1]
#     end_of_month = datetime(current_year, current_month, last_day).date()

#     weekly_hours = [0] * 4  # For 4 weeks in the month
#     leave_weeks = [0] * 4   # To track leave days per week
#     week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8  

#     # Get all attendance entries for the selected month
#     attendance_records = Attendance.objects.filter(
#         employee__employee_id=employee_id,
#         date__range=[start_of_month, end_of_month]
#     )

#     # Get approved leave requests overlapping with the selected month
#     approved_leaves = LeaveRequest.objects.filter(
#         employee__employee_id=employee_id,
#         status='approved',
#         start_date__lte=end_of_month,
#         end_date__gte=start_of_month
#     )

#     # Track leave days per week
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_month)
#         leave_end = min(leave.end_date, end_of_month)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_day = leave_start + timedelta(days=i)
#             week_num = (leave_day.day - 1) // 7
#             if week_num < 4:
#                 leave_weeks[week_num] += 1  # Increment leave count per week

#     # Calculate total working hours and overtime for each week
#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             week_num = (record.date.day - 1) // 7
#             if week_num < 4:
#                 weekly_hours[week_num] += work_duration

#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     total_hours = round(total_hours, 2)
#     total_overtime = round(total_overtime, 2)

#     # Calculate weekly averages
#     weekly_averages = [0] * 4
#     for week_num in range(4):
#         working_days = Attendance.objects.filter(
#             employee__employee_id=employee_id,
#             date__range=[start_of_month + timedelta(weeks=week_num),
#                          start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
#             time_in__isnull=False,
#             time_out__isnull=False
#         ).count()
#         if working_days > 0:
#             weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

#     current_month_name = start_of_month.strftime('%B')

#     # Prepare response data
#     response_data = {
#         'labels': week_labels,
#         'work_data': weekly_hours,
#         'leave_data': leave_weeks,  # Include leave data per week
#         'month': current_month_name,
#         'month_offset': month_offset,
#         'total_hours': total_hours,
#         'total_overtime': total_overtime,
#         'employee_id': employee_id,
#         'average_hours_per_week': total_hours / 4 if total_hours else 0,
#         'weekly_averages': weekly_averages,
#     }

#     return Response(response_data)


# @api_view(['POST'])
# def admin_manager_weekly_chart(request):
#     manager_id = request.data.get('manager_id')
#     if not manager_id:
#         return Response({'error': 'Manager ID is required.'}, status=400)

#     week_offset = int(request.data.get('week_offset', 0))
    
#     today = datetime.now().date()
#     start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)

#     weekly_hours = {}
#     labels = []
#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8

#     for i in range(6):
#         day_date = start_of_week + timedelta(days=i)
#         labels.append(day_date.strftime('%a %b %d'))
#         weekly_hours[labels[-1]] = 0

#     attendance_records = Attendance.objects.filter(
#         manager__manager_id=manager_id,
#         date__range=[start_of_week, end_of_week]
#     )

#     approved_leaves = ManagerLeaveRequest.objects.filter(
#         manager__manager_id=manager_id,
#         status='approved',
#         start_date__lte=end_of_week,
#         end_date__gte=start_of_week
#     )

#     leave_days = set()
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_week)
#         leave_end = min(leave.end_date, end_of_week)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             day_label = record.date.strftime('%a %b %d')
#             if day_label in weekly_hours:
#                 weekly_hours[day_label] += work_duration
#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     work_data = list(weekly_hours.values())
#     leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

#     return Response({
#         'labels': labels,
#         'data': work_data,
#         'leave_data': leave_data,
#         'month': start_of_week.strftime('%B'),
#         'week_offset': week_offset,
#         'total_hours': round(total_hours, 2),
#         'total_overtime': round(total_overtime, 2),
#         'manager_id': manager_id,
#     })

# @api_view(['POST'])
# def admin_manager_monthly_chart(request):
#     manager_id = request.data.get('manager_id')
    
#     if not manager_id:
#         return Response({"error": "Employee ID is required."}, status=400)

#     month_offset = int(request.GET.get('month_offset', 0))
    
#     today = datetime.now().date()
#     current_month = today.month + month_offset
#     current_year = today.year

#     if current_month < 1:
#         current_month += 12
#         current_year -= 1
#     elif current_month > 12:
#         current_month -= 12
#         current_year += 1

#     start_of_month = datetime(current_year, current_month, 1).date()
#     last_day = monthrange(current_year, current_month)[1]
#     end_of_month = datetime(current_year, current_month, last_day).date()

#     weekly_hours = [0] * 4  # For 4 weeks in the month
#     leave_weeks = [0] * 4   # To track leave days per week
#     week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

#     total_hours = 0
#     total_overtime = 0
#     daily_working_hours = 8  

#     # Get all attendance entries for the selected month
#     attendance_records = Attendance.objects.filter(
#         manager__manager_id=manager_id,
#         date__range=[start_of_month, end_of_month]
#     )

#     # Get approved leave requests overlapping with the selected month
#     approved_leaves = ManagerLeaveRequest.objects.filter(
#         manager__manager_id=manager_id,
#         status='approved',
#         start_date__lte=end_of_month,
#         end_date__gte=start_of_month
#     )

#     # Track leave days per week
#     for leave in approved_leaves:
#         leave_start = max(leave.start_date, start_of_month)
#         leave_end = min(leave.end_date, end_of_month)
#         for i in range((leave_end - leave_start).days + 1):
#             leave_day = leave_start + timedelta(days=i)
#             week_num = (leave_day.day - 1) // 7
#             if week_num < 4:
#                 leave_weeks[week_num] += 1  # Increment leave count per week

#     # Calculate total working hours and overtime for each week
#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(datetime.today(), record.time_out) - 
#                              datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
#             week_num = (record.date.day - 1) // 7
#             if week_num < 4:
#                 weekly_hours[week_num] += work_duration

#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     total_hours = round(total_hours, 2)
#     total_overtime = round(total_overtime, 2)

#     # Calculate weekly averages
#     weekly_averages = [0] * 4
#     for week_num in range(4):
#         working_days = Attendance.objects.filter(
#             manager__manager_id=manager_id,
#             date__range=[start_of_month + timedelta(weeks=week_num),
#                          start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
#             time_in__isnull=False,
#             time_out__isnull=False
#         ).count()
#         if working_days > 0:
#             weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

#     current_month_name = start_of_month.strftime('%B')

#     # Prepare response data
#     response_data = {
#         'labels': week_labels,
#         'work_data': weekly_hours,
#         'leave_data': leave_weeks,  # Include leave data per week
#         'month': current_month_name,
#         'month_offset': month_offset,
#         'total_hours': total_hours,
#         'total_overtime': total_overtime,
#         'manager_id': manager_id,
#         'average_hours_per_week': total_hours / 4 if total_hours else 0,
#         'weekly_averages': weekly_averages,
#     }

#     return Response(response_data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
from calendar import monthrange
from .models import Attendance


@api_view(['POST'])
def admin_employee_weekly_chart(request):
    employee_id = request.data.get('employee_id')
    if not employee_id:
        return Response({'error': 'Employee ID is required.'}, status=400)

    week_offset = int(request.data.get('week_offset', 0))
    
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8

    for i in range(6):
        day_date = start_of_week + timedelta(days=i)
        labels.append(day_date.strftime('%a %b %d'))
        weekly_hours[labels[-1]] = 0

    attendance_records = Attendance.objects.filter(
        employee__employee_id=employee_id,
        date__range=[start_of_week, end_of_week]
    )

    approved_leaves = LeaveRequest.objects.filter(
        employee__employee_id=employee_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration
            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    work_data = list(weekly_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    return Response({
        'labels': labels,
        'data': work_data,
        'leave_data': leave_data,
        'month': start_of_week.strftime('%B'),
        'week_offset': week_offset,
        'total_hours': round(total_hours, 2),
        'total_overtime': round(total_overtime, 2),
        'employee_id': employee_id,
    })

from datetime import datetime, timedelta
from calendar import monthrange
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Attendance

@api_view(['POST'])
def admin_employee_monthly_chart(request):
    employee_id = request.data.get('employee_id')
    
    if not employee_id:
        return Response({"error": "Employee ID is required."}, status=400)

    month_offset = int(request.GET.get('month_offset', 0))
    
    today = datetime.now().date()
    current_month = today.month + month_offset
    current_year = today.year

    if current_month < 1:
        current_month += 12
        current_year -= 1
    elif current_month > 12:
        current_month -= 12
        current_year += 1

    start_of_month = datetime(current_year, current_month, 1).date()
    last_day = monthrange(current_year, current_month)[1]
    end_of_month = datetime(current_year, current_month, last_day).date()

    weekly_hours = [0] * 4  # For 4 weeks in the month
    leave_weeks = [0] * 4   # To track leave days per week
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  

    # Get all attendance entries for the selected month
    attendance_records = Attendance.objects.filter(
        employee__employee_id=employee_id,
        date__range=[start_of_month, end_of_month]
    )

    # Get approved leave requests overlapping with the selected month
    approved_leaves = LeaveRequest.objects.filter(
        employee__employee_id=employee_id,
        status='approved',
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )

    # Track leave days per week
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_month)
        leave_end = min(leave.end_date, end_of_month)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = leave_start + timedelta(days=i)
            week_num = (leave_day.day - 1) // 7
            if week_num < 4:
                leave_weeks[week_num] += 1  # Increment leave count per week

    # Calculate total working hours and overtime for each week
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            week_num = (record.date.day - 1) // 7
            if week_num < 4:
                weekly_hours[week_num] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Calculate weekly averages
    weekly_averages = [0] * 4
    for week_num in range(4):
        working_days = Attendance.objects.filter(
            employee__employee_id=employee_id,
            date__range=[start_of_month + timedelta(weeks=week_num),
                         start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
            time_in__isnull=False,
            time_out__isnull=False
        ).count()
        if working_days > 0:
            weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

    current_month_name = start_of_month.strftime('%B')

    # Prepare response data
    response_data = {
        'labels': week_labels,
        'work_data': weekly_hours,
        'leave_data': leave_weeks,  # Include leave data per week
        'month': current_month_name,
        'month_offset': month_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
        'employee_id': employee_id,
        'average_hours_per_week': total_hours / 4 if total_hours else 0,
        'weekly_averages': weekly_averages,
    }

    return Response(response_data)


@api_view(['POST'])
def admin_manager_weekly_chart(request):
    manager_id = request.data.get('manager_id')
    if not manager_id:
        return Response({'error': 'Manager ID is required.'}, status=400)

    week_offset = int(request.data.get('week_offset', 0))
    
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8

    for i in range(6):
        day_date = start_of_week + timedelta(days=i)
        labels.append(day_date.strftime('%a %b %d'))
        weekly_hours[labels[-1]] = 0

    attendance_records = Attendance.objects.filter(
        manager__manager_id=manager_id,
        date__range=[start_of_week, end_of_week]
    )

    approved_leaves = ManagerLeaveRequest.objects.filter(
        manager__manager_id=manager_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration
            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    work_data = list(weekly_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    return Response({
        'labels': labels,
        'data': work_data,
        'leave_data': leave_data,
        'month': start_of_week.strftime('%B'),
        'week_offset': week_offset,
        'total_hours': round(total_hours, 2),
        'total_overtime': round(total_overtime, 2),
        'manager_id': manager_id,
    })

@api_view(['POST'])
def admin_manager_monthly_chart(request):
    manager_id = request.data.get('manager_id')
    
    if not manager_id:
        return Response({"error": "Employee ID is required."}, status=400)

    month_offset = int(request.GET.get('month_offset', 0))
    
    today = datetime.now().date()
    current_month = today.month + month_offset
    current_year = today.year

    if current_month < 1:
        current_month += 12
        current_year -= 1
    elif current_month > 12:
        current_month -= 12
        current_year += 1

    start_of_month = datetime(current_year, current_month, 1).date()
    last_day = monthrange(current_year, current_month)[1]
    end_of_month = datetime(current_year, current_month, last_day).date()

    weekly_hours = [0] * 4  # For 4 weeks in the month
    leave_weeks = [0] * 4   # To track leave days per week
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  

    # Get all attendance entries for the selected month
    attendance_records = Attendance.objects.filter(
        manager__manager_id=manager_id,
        date__range=[start_of_month, end_of_month]
    )

    # Get approved leave requests overlapping with the selected month
    approved_leaves = ManagerLeaveRequest.objects.filter(
        manager__manager_id=manager_id,
        status='approved',
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )

    # Track leave days per week
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_month)
        leave_end = min(leave.end_date, end_of_month)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = leave_start + timedelta(days=i)
            week_num = (leave_day.day - 1) // 7
            if week_num < 4:
                leave_weeks[week_num] += 1  # Increment leave count per week

    # Calculate total working hours and overtime for each week
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            week_num = (record.date.day - 1) // 7
            if week_num < 4:
                weekly_hours[week_num] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Calculate weekly averages
    weekly_averages = [0] * 4
    for week_num in range(4):
        working_days = Attendance.objects.filter(
            manager__manager_id=manager_id,
            date__range=[start_of_month + timedelta(weeks=week_num),
                         start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
            time_in__isnull=False,
            time_out__isnull=False
        ).count()
        if working_days > 0:
            weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

    current_month_name = start_of_month.strftime('%B')

    # Prepare response data
    response_data = {
        'labels': week_labels,
        'work_data': weekly_hours,
        'leave_data': leave_weeks,  # Include leave data per week
        'month': current_month_name,
        'month_offset': month_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
        'manager_id': manager_id,
        'average_hours_per_week': total_hours / 4 if total_hours else 0,
        'weekly_averages': weekly_averages,
    }

    return Response(response_data)



@api_view(['POST'])
def admin_supervisor_weekly_chart(request):
    supervisor_id = request.data.get('supervisor_id')
    if not supervisor_id:
        return Response({'error': 'Supervisor ID is required.'}, status=400)

    week_offset = int(request.data.get('week_offset', 0))
    
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8

    for i in range(6):
        day_date = start_of_week + timedelta(days=i)
        labels.append(day_date.strftime('%a %b %d'))
        weekly_hours[labels[-1]] = 0

    attendance_records = Attendance.objects.filter(
        supervisor__supervisor_id=supervisor_id,
        date__range=[start_of_week, end_of_week]
    )

    approved_leaves = SupervisorLeaveRequest.objects.filter(
        supervisor__supervisor_id=supervisor_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration
            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    work_data = list(weekly_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    return Response({
        'labels': labels,
        'data': work_data,
        'leave_data': leave_data,
        'month': start_of_week.strftime('%B'),
        'week_offset': week_offset,
        'total_hours': round(total_hours, 2),
        'total_overtime': round(total_overtime, 2),
        'supervisor_id': supervisor_id,
    })

@api_view(['POST'])
def admin_supervisor_monthly_chart(request):
    supervisor_id = request.data.get('supervisor_id')
    
    if not supervisor_id:
        return Response({"error": "Supervisor ID is required."}, status=400)

    month_offset = int(request.GET.get('month_offset', 0))
    
    today = datetime.now().date()
    current_month = today.month + month_offset
    current_year = today.year

    if current_month < 1:
        current_month += 12
        current_year -= 1
    elif current_month > 12:
        current_month -= 12
        current_year += 1

    start_of_month = datetime(current_year, current_month, 1).date()
    last_day = monthrange(current_year, current_month)[1]
    end_of_month = datetime(current_year, current_month, last_day).date()

    weekly_hours = [0] * 4  # For 4 weeks in the month
    leave_weeks = [0] * 4   # To track leave days per week
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  

    # Get all attendance entries for the selected month
    attendance_records = Attendance.objects.filter(
        supervisor__supervisor_id=supervisor_id,
        date__range=[start_of_month, end_of_month]
    )

    # Get approved leave requests overlapping with the selected month
    approved_leaves = SupervisorLeaveRequest.objects.filter(
        supervisor__supervisor_id=supervisor_id,
        status='approved',
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )

    # Track leave days per week
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_month)
        leave_end = min(leave.end_date, end_of_month)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = leave_start + timedelta(days=i)
            week_num = (leave_day.day - 1) // 7
            if week_num < 4:
                leave_weeks[week_num] += 1  # Increment leave count per week

    # Calculate total working hours and overtime for each week
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            week_num = (record.date.day - 1) // 7
            if week_num < 4:
                weekly_hours[week_num] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Calculate weekly averages
    weekly_averages = [0] * 4
    for week_num in range(4):
        working_days = Attendance.objects.filter(
            supervisor__supervisor_id=supervisor_id,
            date__range=[start_of_month + timedelta(weeks=week_num),
                         start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
            time_in__isnull=False,
            time_out__isnull=False
        ).count()
        if working_days > 0:
            weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

    current_month_name = start_of_month.strftime('%B')

    # Prepare response data
    response_data = {
        'labels': week_labels,
        'work_data': weekly_hours,
        'leave_data': leave_weeks,  # Include leave data per week
        'month': current_month_name,
        'month_offset': month_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
        'supervisor_id': supervisor_id,
        'average_hours_per_week': total_hours / 4 if total_hours else 0,
        'weekly_averages': weekly_averages,
    }

    return Response(response_data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OnboardingTask
from .serializers import OnboardingTaskSerializer

class OnboardingDashboard(APIView):
    def get(self, request):
        tasks = OnboardingTask.objects.all()
        serializer = OnboardingTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OnboardingTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OnboardingTaskDetailAPIView(APIView):
    def get(self, request, pk):
        try:
            task = OnboardingTask.objects.get(pk=pk)
            serializer = OnboardingTaskSerializer(task)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OnboardingTask.DoesNotExist:
            return Response({'error': 'Onboarding task not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def add_shift_time(request):
    serializer = ShiftAttendanceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Shift time added successfully!"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_shift_time(request, id):
    time = Shift_attendance.objects.get(id=id)
    serializer = ShiftAttendanceSerializer(time, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Shift Update dated successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_shift_time(request, id):
    try:
        time = Shift_attendance.objects.get(id=id)
        time.delete()
        return Response({"message": "Shift time deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Shift_attendance.DoesNotExist:
        return Response({"error": "Time not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def overall_shift_time(request):
    try:
        # Fetch all department records from the database
        time = Shift_attendance.objects.all()

        # Serialize the department data (many=True indicates multiple objects)
        serializer = ShiftAttendanceSerializer(time, many=True)

        # Return the serialized data as a response
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        # In case of any unexpected errors
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.utils.timezone import now

# @api_view(['GET'])
# def supervisor_weekly_attendance(request, user_id):
#     try:
#         week_offset = int(request.query_params.get('week_offset', 0) or 0)
#     except ValueError:
#         return Response({"error": "Invalid week offset"}, status=400)

#     # Calculate the target week range
#     today = now().date()
#     start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#     end_of_week = start_of_week + timedelta(days=6)

#     # Initialize variables
#     labels = [(start_of_week + timedelta(days=i)).strftime('%a %b %d') for i in range(7)]
#     weekly_hours = {label: 0 for label in labels}
#     # permission_hours = {label: 0 for label in labels}
#     total_hours, total_overtime, daily_working_hours = 0, 0, 8

#     # Fetch attendance, permissions, and leave records
#     attendance_records = Attendance.objects.filter(
#         supervisor_supervisor_id=user_id, date_range=[start_of_week, end_of_week]
#     )
#     # permission_records = PermissionHour.objects.filter(
#     #     supervisor_supervisor_id=user_id, date_range=[start_of_week, end_of_week], status='Approved'
#     # )
#     approved_leaves = SupervisorLeaveRequest.objects.filter(
#         supervisor__supervisor_id=user_id, status='approved',
#         start_date_lte=end_of_week, end_date_gte=start_of_week
#     )

#     # Track leave days using a set
#     leave_days = { (leave.start_date + timedelta(days=i)).strftime('%a %b %d')
#                 for leave in approved_leaves
#                 for i in range((leave.end_date - leave.start_date).days + 1)
#                 if start_of_week <= leave.start_date + timedelta(days=i) <= end_of_week }

#     # Process attendance records
#     for record in attendance_records:
#         if record.time_in and record.time_out:
#             work_duration = (datetime.combine(today, record.time_out) - datetime.combine(today, record.time_in)).total_seconds() / 3600
#             day_label = record.date.strftime('%a %b %d')
#             if day_label in weekly_hours:
#                 weekly_hours[day_label] += work_duration

#             total_hours += work_duration
#             if work_duration > daily_working_hours:
#                 total_overtime += work_duration - daily_working_hours

#     # Process permission records
#     # for permission in permission_records:
#     #     permission_duration = (datetime.combine(today, permission.end_time) - datetime.combine(today, permission.start_time)).total_seconds() / 3600
#     #     day_label = permission.date.strftime('%a %b %d')
#     #     if day_label in permission_hours:
#     #         permission_hours[day_label] += permission_duration

#     # Prepare response data
#     response_data = {
#         'labels': labels,
#         'work_data': list(weekly_hours.values()),
#         # 'permission_data': list(permission_hours.values()),
#         'leave_data': [daily_working_hours if label in leave_days else 0 for label in labels],
#         'week_offset': week_offset,
#         'total_hours': round(total_hours, 2),
#         'total_overtime': round(total_overtime, 2),
#     }

#     return Response(response_data)

@api_view(['GET'])
def supervisor_weekly_attendance(request,user_id):
    # user_id = request.session.get('user_id')  # Assuming employee ID is stored in session
    
    try:
        # Get the current week offset from GET parameters (how many weeks to move forward/backward)
        week_offset = int(request.GET.get('week_offset', 0))
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Adjust the week by the offset
        end_of_week = start_of_week + timedelta(days=6)

        # Initialize a dictionary to store total hours per day with the date
        weekly_hours = {}
        labels = []
        
        # Variables to store total hours for the week and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Populate the days of the week (Monday to Saturday)
        for i in range(6):  # Monday to Saturday
            day_date = start_of_week + timedelta(days=i)
            day_label = day_date.strftime('%a %b %d')  # Format: "Mon Sep 11"
            labels.append(day_label)
            weekly_hours[day_label] = 0  # Initialize the hours for each day as 0

        # Get all attendance entries for the selected week
        attendance_records = Attendance.objects.filter(
            supervisor__supervisor_id=user_id,
            date__range=[start_of_week, end_of_week]
        )

        # Get all approved leave requests for the selected week
        approved_leaves = SupervisorLeaveRequest.objects.filter(
            supervisor__supervisor_id=user_id,
            start_date__lte=end_of_week,
            end_date__gte=start_of_week,
            status='approved'
        )

        leave_days = set()
        for leave in approved_leaves:
            # Iterate through the leave days within the week
            leave_start = max(leave.start_date, start_of_week)
            leave_end = min(leave.end_date, end_of_week)
            for i in range((leave_end - leave_start).days + 1):
                leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
                leave_days.add(leave_day)

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                # Convert time_in and time_out to datetime and calculate work duration
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                day_label = record.date.strftime('%a %b %d')  # Ensure record.date is also handled as date
                if day_label in weekly_hours:
                    weekly_hours[day_label] += work_duration

                # Calculate total hours and overtime
                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Get the current month
        current_month = start_of_week.strftime('%B')

        work_data = list(weekly_hours.values())
        leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

        # Prepare the response data
        response_data = {
            'labels': labels,  # List of days with their respective dates
            'work_data': work_data,  # Corresponding hours worked
            'month': current_month,
            'leave_data': leave_data,  # Days where the employee was on leave
            'week_offset': week_offset,  # Current week offset for navigation
            'total_hours': total_hours,  # Total hours worked in the week
            'total_overtime': total_overtime,  # Total overtime worked in the week
        }


        # Return the success response with status 200
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError:
        # Handle errors related to invalid week_offset
        error_data = {
            'message': 'Invalid week_offset parameter. Please provide a valid integer value.'
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        error_data = {
            'message': 'An unexpected error occurred.',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def supervisor_monthly_attendance_chart(request,user_id):
    try:
        # Assuming manager ID is stored in the session
        # user_id = request.session.get('user_id')
        # if not user_id:
        #     return Response({'error': 'Manager ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current month offset from GET parameters (how many months to move forward/backward)
        month_offset = int(request.GET.get('month_offset', 0))

        # Get today's date and adjust the month by the offset
        today = datetime.now()
        current_month = today.month + month_offset
        current_year = today.year

        # Handle year overflow/underflow when adjusting months
        if current_month < 1:
            current_month += 12
            current_year -= 1
        elif current_month > 12:
            current_month -= 12
            current_year += 1

        # Determine the first and last day of the month
        start_of_month = datetime(current_year, current_month, 1)
        last_day = monthrange(current_year, current_month)[1]  # Get the number of days in the month
        end_of_month = datetime(current_year, current_month, last_day)

        # Initialize data structures to store weekly hours and leave information
        weekly_hours = [0, 0, 0, 0]  # For 4 weeks
        working_days_per_week = [0, 0, 0, 0]  # To track the number of working days per week
        week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]  # Week labels
        
        # Variables to store total hours for the month and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Get all attendance entries for the selected month
        attendance_records = Attendance.objects.filter(
            supervisor__supervisor_id=user_id,
            date__range=[start_of_month, end_of_month]
        )

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = datetime.combine(datetime.today(), record.time_out) - datetime.combine(datetime.today(), record.time_in)
                hours_worked = work_duration.total_seconds() / 3600  # Convert seconds to hours

                # Determine which week the record falls into (1-7 = Week 1, etc.)
                week_num = (record.date.day - 1) // 7  # Get week number (0, 1, 2, or 3)
                if week_num < 4:  # Ensure we don't go beyond Week 4
                    weekly_hours[week_num] += hours_worked
                    working_days_per_week[week_num] += 1  # Increment the count of working days for this week

                # Calculate total hours and overtime
                total_hours += hours_worked
                if hours_worked > daily_working_hours:
                    total_overtime += hours_worked - daily_working_hours

        total_hours = round(total_hours, 3)
        total_overtime = round(total_overtime, 3)

        # Calculate the average hours per week by dividing the total hours by the number of working days
        average_hours_per_week = []
        for week_num in range(4):
            if working_days_per_week[week_num] > 0:
                avg_hours = weekly_hours[week_num] / working_days_per_week[week_num]
            else:
                avg_hours = 0
            average_hours_per_week.append(round(avg_hours, 2))

        # Zip the week labels with the average working hours to pass them together in the response
        week_avg_data = list(zip(week_labels, average_hours_per_week))

        # Get the month name for display
        current_month_name = start_of_month.strftime('%B')

        # Prepare response data
        response_data = {
            # 'month': current_month_name,  # Current month name
            # 'week_avg_data': week_avg_data,  # Pass the zipped week labels and average hours
            # 'work_data': week_avg_data,  # Pass the zipped week labels and average hours
            # 'work_hours': total_hours,  # Total hours worked in the month
            # 'total_overtime': total_overtime,  # Total overtime worked in the month
            # 'month_offset': month_offset,  # Pass the current month offset for navigation

            'month': current_month_name,  # Current month name
            'week_avg_data': week_avg_data,  # Pass the zipped week labels and average hours
            'total_hours': total_hours,  # Total hours worked in the month
            'work_data': average_hours_per_week,  # Total hours worked in the month
            'total_overtime': total_overtime,  # Total overtime worked in the month
            'month_offset': month_offset,
            'labels':week_avg_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   

def supervisor_calculate_total_present_days(supervisor_id):
    """
    Calculate total present days for an employee based on total working hours.

    :param employee_id: ID of the employee
    :return: Total present days (float)
    """
    # Fetch all attendance records for the employee
    attendance_records = Attendance.objects.filter(supervisor_id=supervisor_id).exclude(total_working_hours=None)

    # Sum up the total working hours across all records
    total_seconds = sum(
        int(timedelta(
            hours=int(hours.split(':')[0]), 
            minutes=int(hours.split(':')[1]),
            seconds=int(hours.split(':')[2])
        ).total_seconds()) for hours in attendance_records.values_list('total_working_hours', flat=True)
    )

    # Convert total seconds to hours
    total_hours = total_seconds / 3600

    # Calculate present days (8 hours = 1 day)
    present_days = total_hours / 8
    
    
    return round(present_days, 2)  # Round off to 2 decimal placesdir

# hr attendance all function code 
    # #############################################################################################################
    ##################################################################################################################
@api_view(['GET'])
def admin_hr_attendance_history(request):
    # Retrieve manager_id, from_date, and to_date from query parameters
    hr_id = request.query_params.get('hr_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not hr_id:
        return Response({'error': 'Hr ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({"detail": "Hr not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(hr__hr_id=hr_id)
    leave_query = HrLeaveRequest.objects.filter(hr__hr_id=hr_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize attendance records and add manager_name
    attendance_records = []
    for attendance in attendance_query:
        attendance_records.append({
            'id': attendance.id,
            'hr_name': hr.hr_name,  # Include manager name
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time_in': attendance.time_in,
            'time_out': attendance.time_out,
            'in_status': attendance.in_status,
            'out_status': attendance.out_status,
            'overtime': attendance.overtime,
            'total_working_hours': attendance.total_working_hours,
            'type': 'attendance',
        })

    # Prepare leave records manually with manager_name
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'hr_name': hr.hr_name,  # Include manager name
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'on leave'
            })

    # Combine attendance and leave records, and sort by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
def admin_hr_weekly_chart(request):
    hr_id = request.data.get('hr_id')
    if not hr_id:
        return Response({'error': 'Hr ID is required.'}, status=400)

    week_offset = int(request.data.get('week_offset', 0))
    
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8

    for i in range(6):
        day_date = start_of_week + timedelta(days=i)
        labels.append(day_date.strftime('%a %b %d'))
        weekly_hours[labels[-1]] = 0

    attendance_records = Attendance.objects.filter(
        hr__hr_id=hr_id,
        date__range=[start_of_week, end_of_week]
    )

    approved_leaves = HrLeaveRequest.objects.filter(
        hr__hr_id=hr_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration
            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    work_data = list(weekly_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    return Response({
        'labels': labels,
        'data': work_data,
        'leave_data': leave_data,
        'month': start_of_week.strftime('%B'),
        'week_offset': week_offset,
        'total_hours': round(total_hours, 2),
        'total_overtime': round(total_overtime, 2),
        'hr_id': hr_id,
    })

@api_view(['POST'])
def admin_hr_monthly_chart(request):
    hr_id = request.data.get('hr_id')
    
    if not hr_id:
        return Response({"error": "Hr ID is required."}, status=400)

    month_offset = int(request.GET.get('month_offset', 0))
    
    today = datetime.now().date()
    current_month = today.month + month_offset
    current_year = today.year

    if current_month < 1:
        current_month += 12
        current_year -= 1
    elif current_month > 12:
        current_month -= 12
        current_year += 1

    start_of_month = datetime(current_year, current_month, 1).date()
    last_day = monthrange(current_year, current_month)[1]
    end_of_month = datetime(current_year, current_month, last_day).date()

    weekly_hours = [0] * 4  # For 4 weeks in the month
    leave_weeks = [0] * 4   # To track leave days per week
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  

    # Get all attendance entries for the selected month
    attendance_records = Attendance.objects.filter(
        hr__hr_id=hr_id,
        date__range=[start_of_month, end_of_month]
    )

    # Get approved leave requests overlapping with the selected month
    approved_leaves = HrLeaveRequest.objects.filter(
        hr__hr_id=hr_id,
        status='approved',
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )

    # Track leave days per week
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_month)
        leave_end = min(leave.end_date, end_of_month)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = leave_start + timedelta(days=i)
            week_num = (leave_day.day - 1) // 7
            if week_num < 4:
                leave_weeks[week_num] += 1  # Increment leave count per week

    # Calculate total working hours and overtime for each week
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            week_num = (record.date.day - 1) // 7
            if week_num < 4:
                weekly_hours[week_num] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Calculate weekly averages
    weekly_averages = [0] * 4
    for week_num in range(4):
        working_days = Attendance.objects.filter(
            hr__hr_id=hr_id,
            date__range=[start_of_month + timedelta(weeks=week_num),
                         start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
            time_in__isnull=False,
            time_out__isnull=False
        ).count()
        if working_days > 0:
            weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

    current_month_name = start_of_month.strftime('%B')

    # Prepare response data
    response_data = {
        'labels': week_labels,
        'work_data': weekly_hours,
        'leave_data': leave_weeks,  # Include leave data per week
        'month': current_month_name,
        'month_offset': month_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
        'hr_id': hr_id,
        'average_hours_per_week': total_hours / 4 if total_hours else 0,
        'weekly_averages': weekly_averages,
    }

    return Response(response_data)


@api_view(['GET'])
def admin_hr_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', hr__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            hr_attendance = Attendance.objects.get(
                hr=reset_request.hr,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'hr_id': reset_request.hr.hr_id,  
                'username': reset_request.hr.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': hr_attendance.shift.shift_number if hr_attendance.shift else None,  
                'time_in': hr_attendance.time_in,
                'time_out': hr_attendance.time_out,
                'in_status': hr_attendance.in_status,
                'out_status': hr_attendance.out_status,
                'notes': hr_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_hr_approve_and_reset_checkout_time(request, id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    hr_id = reset_request.hr.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(hr_id=hr_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "Hr Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def admin_hr_reject_manager_reset_request(request, id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def hr_attendance_form(request, user_id):
    try:
        hr = Hr.objects.get(hr_id=user_id)

        locations = [hr.location] if hr.location else []
        if locations and len(locations) > 1:
            locations = [locations[0]]

        location_serializer = LocationSerializer(locations, many=True)
        shift_serializer = ShiftSerializer(hr.shift) if hr.shift else None

        today = timezone.localdate()
        last_attendance = Attendance.objects.filter(hr=hr, date=today).first()

        show_checkout = False
        thank_you_message = ''
        already_checked_out = False
        first_in_time = "--:--"
        last_out_time = "--:--"
        on_leave = False

        leave_request = HrLeaveRequest.objects.filter(
            hr=hr,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            on_leave = True

        if last_attendance:
            if last_attendance.time_in:
                first_in_time = last_attendance.time_in.strftime("%I:%M %p")
            if last_attendance.time_out:
                last_out_time = last_attendance.time_out.strftime("%I:%M %p")

            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                approved_reset = ResetRequest.objects.filter(
                    hr=hr,
                    date=today,
                    status='approved'
                ).exists()
                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    already_checked_out = True
                    thank_you_message = 'You have already checked out for today.'
                    return Response({
                        'locations': location_serializer.data,
                        'shift': shift_serializer.data if shift_serializer else None,
                        'show_checkout': False,
                        'thank_you_message': thank_you_message,
                        'already_checked_out': already_checked_out,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'on_leave': on_leave,
                    }, status=status.HTTP_200_OK)

        if on_leave:
            return Response({
                'locations': location_serializer.data,
                'shift': shift_serializer.data if shift_serializer else None,
                'show_checkout': False,
                'thank_you_message': '',
                'already_checked_out': False,
                'first_in_time': first_in_time,
                'last_out_time': last_out_time,
                'on_leave': on_leave,
            }, status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data if shift_serializer else None,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message,
            'already_checked_out': already_checked_out,
            'first_in_time': first_in_time,
            'last_out_time': last_out_time,
            'on_leave': on_leave,
        }, status=status.HTTP_200_OK)

    except Hr.DoesNotExist:
        return Response({'error': 'HR not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def submit_hr_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "HR ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hr = Hr.objects.get(hr_id=user_id)
        today = datetime.now().date()

        leave_request = HrLeaveRequest.objects.filter(
            hr=hr,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()

        if leave_request:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            if Attendance.objects.filter(hr=hr, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                hr=hr,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({
                "message": "Checked in successfully.",
                "time_in": current_time.strftime('%H:%M:%S'),
                "in_status": in_status
            }, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            time_out = datetime.now().strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                hr=hr,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(
                    hr=hr,
                    date=today,
                    status='approved'
                ).exists()
                if reset_approved:
                    last_attendance = Attendance.objects.filter(
                        hr=hr,
                        date=today
                    ).first()
                else:
                    return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

            if not last_attendance:
                return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(today, current_time) - datetime.combine(today, time_in)

            break_start = time(13, 0, 0)
            break_end = time(14, 0, 0)
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({
                "message": "Checked out successfully.",
                "time_out": time_out,
                "out_status": out_status
            }, status=status.HTTP_200_OK)

    except Hr.DoesNotExist:
        return Response({'error': 'HR not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
@api_view(['GET'])
def hr_attendance_history(request, user_id):
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')

    attendance_query = Attendance.objects.filter(hr__hr_id=user_id)
    leave_query = HrLeaveRequest.objects.filter(hr__hr_id=user_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare attendance records with reset request status
    attendance_records = []
    for record in attendance_query.select_related('shift', 'location'):
        reset_request = ResetRequest.objects.filter(hr=record.hr, date=record.date).order_by('-created_at').first()
        attendance_records.append({
            'date': record.date,
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': record.total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request"
        })

    # Prepare leave records
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'date': leave_date,
                'type': 'leave'
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    # Convert date objects to string format for JSON response
    for record in all_records:
        if isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        elif isinstance(record['date'], date):
            record['date'] = record['date'].strftime('%Y-%m-%d')


    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
@api_view(['GET', 'POST'])  # Allow GET requests for fetching requests
def hr_request_check_out_reset(request,user_id):
    if request.method == 'GET':
        requests = ResetRequest.objects.all().values()
        return Response(list(requests), status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # user_id = request.data.get('user_id')
        today = datetime.today()

        try:
            hr = Hr.objects.get(hr_id=user_id)
        except Hr.DoesNotExist:
            return Response({"detail": "Hr not found."}, status=status.HTTP_404_NOT_FOUND)

        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        reset_request = ResetRequest(
            hr=hr,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)                        

@api_view(['GET'])
def hr_weekly_attendance_chart(request):
    user_id = request.session.get('user_id')  # Assuming employee ID is stored in session
    
    try:
        # Get the current week offset from GET parameters (how many weeks to move forward/backward)
        week_offset = int(request.GET.get('week_offset', 0))
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Adjust the week by the offset
        end_of_week = start_of_week + timedelta(days=6)

        # Initialize a dictionary to store total hours per day with the date
        weekly_hours = {}
        labels = []
        
        # Variables to store total hours for the week and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Populate the days of the week (Monday to Saturday)
        for i in range(6):  # Monday to Saturday
            day_date = start_of_week + timedelta(days=i)
            day_label = day_date.strftime('%a %b %d')  # Format: "Mon Sep 11"
            labels.append(day_label)
            weekly_hours[day_label] = 0  # Initialize the hours for each day as 0

        # Get all attendance entries for the selected week
        attendance_records = Attendance.objects.filter(
            hr__hr_id=user_id,
            date__range=[start_of_week, end_of_week]
        )

        # Get all approved leave requests for the selected week
        approved_leaves = HrLeaveRequest.objects.filter(
            hr__hr_id=user_id,
            start_date__lte=end_of_week,
            end_date__gte=start_of_week,
            status='approved'
        )

        leave_days = set()
        for leave in approved_leaves:
            # Iterate through the leave days within the week
            leave_start = max(leave.start_date, start_of_week)
            leave_end = min(leave.end_date, end_of_week)
            for i in range((leave_end - leave_start).days + 1):
                leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
                leave_days.add(leave_day)

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                # Convert time_in and time_out to datetime and calculate work duration
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                day_label = record.date.strftime('%a %b %d')  # Ensure record.date is also handled as date
                if day_label in weekly_hours:
                    weekly_hours[day_label] += work_duration

                # Calculate total hours and overtime
                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Get the current month
        current_month = start_of_week.strftime('%B')

        work_data = list(weekly_hours.values())
        leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

        # Prepare the response data
        response_data = {
            'labels': labels,  # List of days with their respective dates
            'data': work_data,  # Corresponding hours worked
            'month': current_month,
            'leave_data': leave_data,  # Days where the employee was on leave
            'week_offset': week_offset,  # Current week offset for navigation
            'total_hours': total_hours,  # Total hours worked in the week
            'total_overtime': total_overtime,  # Total overtime worked in the week
        }

        # Return the success response with status 200
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError:
        # Handle errors related to invalid week_offset
        error_data = {
            'message': 'Invalid week_offset parameter. Please provide a valid integer value.'
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        error_data = {
            'message': 'An unexpected error occurred.',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def hr_monthly_attendance_chart(request):
    try:
        # Assuming manager ID is stored in the session
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Hr ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current month offset from GET parameters (how many months to move forward/backward)
        month_offset = int(request.GET.get('month_offset', 0))

        # Get today's date and adjust the month by the offset
        today = datetime.now()
        current_month = today.month + month_offset
        current_year = today.year

        # Handle year overflow/underflow when adjusting months
        if current_month < 1:
            current_month += 12
            current_year -= 1
        elif current_month > 12:
            current_month -= 12
            current_year += 1

        # Determine the first and last day of the month
        start_of_month = datetime(current_year, current_month, 1)
        last_day = monthrange(current_year, current_month)[1]  # Get the number of days in the month
        end_of_month = datetime(current_year, current_month, last_day)

        # Initialize data structures to store weekly hours and leave information
        weekly_hours = [0, 0, 0, 0]  # For 4 weeks
        working_days_per_week = [0, 0, 0, 0]  # To track the number of working days per week
        week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]  # Week labels
        
        # Variables to store total hours for the month and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Get all attendance entries for the selected month
        attendance_records = Attendance.objects.filter(
            hr__hr_id=user_id,
            date__range=[start_of_month, end_of_month]
        )

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = datetime.combine(datetime.today(), record.time_out) - datetime.combine(datetime.today(), record.time_in)
                hours_worked = work_duration.total_seconds() / 3600  # Convert seconds to hours

                # Determine which week the record falls into (1-7 = Week 1, etc.)
                week_num = (record.date.day - 1) // 7  # Get week number (0, 1, 2, or 3)
                if week_num < 4:  # Ensure we don't go beyond Week 4
                    weekly_hours[week_num] += hours_worked
                    working_days_per_week[week_num] += 1  # Increment the count of working days for this week

                # Calculate total hours and overtime
                total_hours += hours_worked
                if hours_worked > daily_working_hours:
                    total_overtime += hours_worked - daily_working_hours

        total_hours = round(total_hours, 3)
        total_overtime = round(total_overtime, 3)

        # Calculate the average hours per week by dividing the total hours by the number of working days
        average_hours_per_week = []
        for week_num in range(4):
            if working_days_per_week[week_num] > 0:
                avg_hours = weekly_hours[week_num] / working_days_per_week[week_num]
            else:
                avg_hours = 0
            average_hours_per_week.append(round(avg_hours, 2))

        # Zip the week labels with the average working hours to pass them together in the response
        week_avg_data = list(zip(week_labels, average_hours_per_week))

        # Get the month name for display
        current_month_name = start_of_month.strftime('%B')

        # Prepare response data
        response_data = {
            'month': current_month_name,  # Current month name
            'week_avg_data': week_avg_data,  # Pass the zipped week labels and average hours
            'total_hours': total_hours,  # Total hours worked in the month
            'total_overtime': total_overtime,  # Total overtime worked in the month
            'month_offset': month_offset,  # Pass the current month offset for navigation
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def admin_overall_employee_daily_chart(request):
    today = datetime.now().date()
    day_offset = int(request.query_params.get('day_offset', 0))
    
    target_date = today + timedelta(days=day_offset)
    start_date = target_date - timedelta(days=6)  # Get last 7 days

    labels = []
    daily_attendance = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        labels.append(current_date.strftime('%a %b %d'))

        # Count only employee attendance (Exclude manager, supervisor, and HR)
        attendance_count = Attendance.objects.filter(
            date=current_date,
            employee__isnull=False  # Ensures only employees are counted
        ).values('employee').annotate(
            first_time_in=Min('time_in')
        ).count()

        daily_attendance.append(attendance_count)

    return Response({
        'labels': labels,
        'data': daily_attendance,
        'dates': [start_date.strftime('%Y-%m-%d'), target_date.strftime('%Y-%m-%d')],
        'day_offset': day_offset,
    })


@api_view(['GET'])
def admin_overall_manager_daily_chart(request):
    today = datetime.now().date()
    day_offset = int(request.query_params.get('day_offset', 0))
    
    target_date = today + timedelta(days=day_offset)
    start_date = target_date - timedelta(days=6)  # Get last 7 days

    labels = []
    daily_attendance = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        labels.append(current_date.strftime('%a %b %d'))

        # Count only employee attendance (Exclude employee, supervisor, and HR)
        attendance_count = Attendance.objects.filter(
            date=current_date,
            manager__isnull=False  # Ensures only managers are counted
        ).values('manager').annotate(
            first_time_in=Min('time_in')
        ).count()

        daily_attendance.append(attendance_count)

    return Response({
        'labels': labels,
        'data': daily_attendance,
        'dates': [start_date.strftime('%Y-%m-%d'), target_date.strftime('%Y-%m-%d')],
        'day_offset': day_offset,
    })



@api_view(['GET'])
def admin_overall_supervisor_daily_chart(request):
    today = datetime.now().date()
    day_offset = int(request.query_params.get('day_offset', 0))
    
    target_date = today + timedelta(days=day_offset)
    start_date = target_date - timedelta(days=6)  # Get last 7 days

    labels = []
    daily_attendance = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        labels.append(current_date.strftime('%a %b %d'))

        # Count only employee attendance (Exclude manager, employee, and HR)
        attendance_count = Attendance.objects.filter(
            date=current_date,
            supervisor__isnull=False  # Ensures only supervisors are counted
        ).values('supervisor').annotate(
            first_time_in=Min('time_in')
        ).count()

        daily_attendance.append(attendance_count)

    return Response({
        'labels': labels,
        'data': daily_attendance,
        'dates': [start_date.strftime('%Y-%m-%d'), target_date.strftime('%Y-%m-%d')],
        'day_offset': day_offset,
    })


@api_view(['GET'])
def admin_overall_hr_daily_chart(request):
    today = datetime.now().date()
    day_offset = int(request.query_params.get('day_offset', 0))
    
    target_date = today + timedelta(days=day_offset)
    start_date = target_date - timedelta(days=6)  # Get last 7 days

    labels = []
    daily_attendance = []

    for i in range(7):
        current_date = start_date + timedelta(days=i)
        labels.append(current_date.strftime('%a %b %d'))

        # Count only employee attendance (Exclude manager, supervisor, and employee)
        attendance_count = Attendance.objects.filter(
            date=current_date,
            hr__isnull=False  # Ensures only hrs are counted
        ).values('hr').annotate(
            first_time_in=Min('time_in')
        ).count()

        daily_attendance.append(attendance_count)

    return Response({
        'labels': labels,
        'data': daily_attendance,
        'dates': [start_date.strftime('%Y-%m-%d'), target_date.strftime('%Y-%m-%d')],
        'day_offset': day_offset,
    })

# hr attendance all function code 
    # #############################################################################################################
    ##################################################################################################################
@api_view(['GET'])
def admin_ar_attendance_history(request):
    # Retrieve manager_id, from_date, and to_date from query parameters
    ar_id = request.query_params.get('ar_id')
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    if not ar_id:
        return Response({'error': 'Ar ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ar = Ar.objects.get(ar_id=ar_id)
    except Ar.DoesNotExist:
        return Response({"detail": "Ar not found."}, status=status.HTTP_404_NOT_FOUND)

    # Initialize attendance and leave queries
    attendance_query = Attendance.objects.filter(ar__ar_id=ar_id)
    leave_query = ArLeaveRequest.objects.filter(ar__ar_id=ar_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Serialize attendance records and add manager_name
    attendance_records = []
    for attendance in attendance_query:
        attendance_records.append({
            'id': attendance.id,
            'ar_name': ar.ar_name,  # Include manager name
            'date': attendance.date.strftime('%Y-%m-%d'),
            'time_in': attendance.time_in,
            'time_out': attendance.time_out,
            'in_status': attendance.in_status,
            'out_status': attendance.out_status,
            'overtime': attendance.overtime,
            'total_working_hours': attendance.total_working_hours,
            'type': 'attendance',
        })

    # Prepare leave records manually with manager_name
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'ar_name': ar.ar_name,  # Include manager name
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'on leave'
            })

    # Combine attendance and leave records, and sort by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
    
@api_view(['POST'])
def admin_ar_weekly_chart(request):
    ar_id = request.data.get('ar_id')
    if not ar_id:
        return Response({'error': 'ar ID is required.'}, status=400)

    week_offset = int(request.data.get('week_offset', 0))
    
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    weekly_hours = {}
    labels = []
    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8

    for i in range(6):
        day_date = start_of_week + timedelta(days=i)
        labels.append(day_date.strftime('%a %b %d'))
        weekly_hours[labels[-1]] = 0

    attendance_records = Attendance.objects.filter(
        ar__ar_id=ar_id,
        date__range=[start_of_week, end_of_week]
    )

    approved_leaves = ArLeaveRequest.objects.filter(
        ar__ar_id=ar_id,
        status='approved',
        start_date__lte=end_of_week,
        end_date__gte=start_of_week
    )

    leave_days = set()
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_week)
        leave_end = min(leave.end_date, end_of_week)
        for i in range((leave_end - leave_start).days + 1):
            leave_days.add((leave_start + timedelta(days=i)).strftime('%a %b %d'))

    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            day_label = record.date.strftime('%a %b %d')
            if day_label in weekly_hours:
                weekly_hours[day_label] += work_duration
            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    work_data = list(weekly_hours.values())
    leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

    return Response({
        'labels': labels,
        'data': work_data,
        'leave_data': leave_data,
        'month': start_of_week.strftime('%B'),
        'week_offset': week_offset,
        'total_hours': round(total_hours, 2),
        'total_overtime': round(total_overtime, 2),
        'ar_id': ar_id,
    })

@api_view(['POST'])
def admin_ar_monthly_chart(request):
    ar_id = request.data.get('hr_id')
    
    if not ar_id:
        return Response({"error": "ar ID is required."}, status=400)

    month_offset = int(request.GET.get('month_offset', 0))
    
    today = datetime.now().date()
    current_month = today.month + month_offset
    current_year = today.year

    if current_month < 1:
        current_month += 12
        current_year -= 1
    elif current_month > 12:
        current_month -= 12
        current_year += 1

    start_of_month = datetime(current_year, current_month, 1).date()
    last_day = monthrange(current_year, current_month)[1]
    end_of_month = datetime(current_year, current_month, last_day).date()

    weekly_hours = [0] * 4  # For 4 weeks in the month
    leave_weeks = [0] * 4   # To track leave days per week
    week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]

    total_hours = 0
    total_overtime = 0
    daily_working_hours = 8  

    # Get all attendance entries for the selected month
    attendance_records = Attendance.objects.filter(
        ar__ar_id=ar_id,
        date__range=[start_of_month, end_of_month]
    )

    # Get approved leave requests overlapping with the selected month
    approved_leaves = ArLeaveRequest.objects.filter(
        ar__ar_id=ar_id,
        status='approved',
        start_date__lte=end_of_month,
        end_date__gte=start_of_month
    )

    # Track leave days per week
    for leave in approved_leaves:
        leave_start = max(leave.start_date, start_of_month)
        leave_end = min(leave.end_date, end_of_month)
        for i in range((leave_end - leave_start).days + 1):
            leave_day = leave_start + timedelta(days=i)
            week_num = (leave_day.day - 1) // 7
            if week_num < 4:
                leave_weeks[week_num] += 1  # Increment leave count per week

    # Calculate total working hours and overtime for each week
    for record in attendance_records:
        if record.time_in and record.time_out:
            work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                             datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
            week_num = (record.date.day - 1) // 7
            if week_num < 4:
                weekly_hours[week_num] += work_duration

            total_hours += work_duration
            if work_duration > daily_working_hours:
                total_overtime += work_duration - daily_working_hours

    total_hours = round(total_hours, 2)
    total_overtime = round(total_overtime, 2)

    # Calculate weekly averages
    weekly_averages = [0] * 4
    for week_num in range(4):
        working_days = Attendance.objects.filter(
            ar__ar_id=ar_id,
            date__range=[start_of_month + timedelta(weeks=week_num),
                         start_of_month + timedelta(weeks=week_num + 1) - timedelta(days=1)],
            time_in__isnull=False,
            time_out__isnull=False
        ).count()
        if working_days > 0:
            weekly_averages[week_num] = round(weekly_hours[week_num] / working_days, 2)

    current_month_name = start_of_month.strftime('%B')

    # Prepare response data
    response_data = {
        'labels': week_labels,
        'work_data': weekly_hours,
        'leave_data': leave_weeks,  # Include leave data per week
        'month': current_month_name,
        'month_offset': month_offset,
        'total_hours': total_hours,
        'total_overtime': total_overtime,
        'ar_id': ar_id,
        'average_hours_per_week': total_hours / 4 if total_hours else 0,
        'weekly_averages': weekly_averages,
    }

    return Response(response_data)


@api_view(['GET'])
def admin_ar_reset_requests(request):
    # Fetch all pending reset requests
    reset_requests = ResetRequest.objects.filter(status='Pending', ar__isnull=False)

    reset_requests_list = []

    for reset_request in reset_requests:
        try:
            # Fetch the related attendance record
            ar_attendance = Attendance.objects.get(
                ar=reset_request.ar,
                date=reset_request.date
            )
            
            # Prepare the data to be returned as JSON
            reset_requests_list.append({
                'id': reset_request.id,
                'ar_id': reset_request.ar.ar_id,  
                'username': reset_request.ar.username,
                'request_type': reset_request.request_type,
                'request_description': reset_request.request_description,
                'date': reset_request.date,
                'shift': ar_attendance.shift.shift_number if ar_attendance.shift else None,  
                'time_in': ar_attendance.time_in,
                'time_out': ar_attendance.time_out,
                'in_status': ar_attendance.in_status,
                'out_status': ar_attendance.out_status,
                'notes': ar_attendance.notes,
                'status': reset_request.status
            })
        except Attendance.DoesNotExist:
            # Handle if attendance record doesn't exist (can log this error)
            continue

    # Return the data as a JSON response
    return Response({"reset_requests": reset_requests_list}, status=status.HTTP_200_OK)

@api_view(['POST'])
def admin_ar_approve_and_reset_checkout_time(request, id):
    # Step 1: Approve the reset request
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update the reset request's status to "Approved"
    reset_request.status = 'Approved'
    reset_request.save()

    # Step 2: Trigger reset checkout time for the corresponding employee and date
    ar_id = reset_request.ar.id
    date = reset_request.date

    try:
        # Get the attendance record
        attendance_record = Attendance.objects.get(ar_id=ar_id, date=date)

        clear_checkout = request.data.get('clear_checkout', False)
        checkout_time_str = request.data.get('checkout_time')

        if clear_checkout:
            # Clear the checkout time
            attendance_record.time_out = None
            attendance_record.out_status = None
            attendance_record.overtime = None
            attendance_record.total_working_hours = None
        else:
            # Set the new checkout time
            if checkout_time_str:
                # Validate and convert checkout time
                try:
                    checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
                except ValueError:
                    return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

                attendance_record.time_out = checkout_time
                attendance_record.out_status = 'Updated by Admin'

                # Calculate total working hours
                time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
                time_out = checkout_time

                # Convert to datetime for calculation
                today = datetime.today()
                time_in_datetime = datetime.combine(today, time_in)
                time_out_datetime = datetime.combine(today, time_out)

                total_working_time = time_out_datetime - time_in_datetime
                total_hours = total_working_time.seconds // 3600
                total_minutes = (total_working_time.seconds % 3600) // 60
                total_seconds = total_working_time.seconds % 60
                attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

                # Calculate overtime
                shift_end_time = attendance_record.shift.shift_end_time
                shift_end_datetime = datetime.combine(today, shift_end_time)
                overtime_start_time = shift_end_datetime + timedelta(minutes=10)

                if time_out_datetime > overtime_start_time:
                    overtime = time_out_datetime - overtime_start_time
                    overtime_hours = overtime.seconds // 3600
                    overtime_minutes = (overtime.seconds % 3600) // 60
                    overtime_seconds = overtime.seconds % 60
                    attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
                else:
                    attendance_record.overtime = "00:00:00"

        attendance_record.save()
        return Response({"detail": "ar Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)

    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def admin_ar_reject_manager_reset_request(request, id):
    try:
        # Find the reset request
        reset_request = ResetRequest.objects.get(id=id)
        
        # Update the reset request's status to "Rejected"
        reset_request.status = 'Rejected'
        reset_request.save()

        return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)

    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def ar_attendance_form(request, user_id):
    try:
        ar = Ar.objects.get(ar_id=user_id)

        locations = Location.objects.all()
        location_serializer = LocationSerializer(locations, many=True)

        shift = ar.shift
        shift_serializer = ShiftSerializer(shift)

        today = datetime.now().date()
        last_attendance = Attendance.objects.filter(ar=ar, date=today).first()

        show_checkout = False
        thank_you_message = ''

        if last_attendance:
            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                # 🔥 NEW: Check for approved ResetRequest
                approved_reset = ResetRequest.objects.filter(
                    ar=ar,
                    date=today,
                    status='Approved',
                    # request_type='reset_checkout'  # Optional: use a specific type
                ).exists()

                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    return Response({'message': 'You have already checked out for today.'},
                                    status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message
        }, status=status.HTTP_200_OK)

    except Ar.DoesNotExist:
        return Response({'error': 'ar not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def submit_ar_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "Ar ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        ar = Hr.objects.get(ar_id=user_id)

        # Check leave status
        leave_request = HrLeaveRequest.objects.filter(
            ar=ar,
            status='approved',
            start_date__lte=datetime.now().date(),
            end_date__gte=datetime.now().date()
        ).first()
        if leave_request:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            # Handle check-in
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            today = datetime.now().date()
            if Attendance.objects.filter(ar=ar, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                ar=ar,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            today = datetime.now().date()
            time_out = datetime.now().strftime('%H:%M:%S')

            # Try to get open attendance first
            last_attendance = Attendance.objects.filter(
                ar__ar_id=user_id,
                date=today,
                time_out=None
            ).first()

            # If already checked out, check if reset is approved
            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(
                    ar__ar_id=user_id,
                    date=today,
                    status='approved'
                ).exists()

                if reset_approved:
                    last_attendance = Attendance.objects.filter(
                        ar__ar_id=user_id,
                        date=today
                    ).first()
                else:
                    return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

            if not last_attendance:
                return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(datetime.today(), shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), time_in)

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            # Save updates
            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

    except Ar.DoesNotExist:
        return Response({'error': 'ar not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def ar_attendance_history(request, user_id):
    from_date = request.data.get('from_date')
    to_date = request.data.get('to_date')

    attendance_query = Attendance.objects.filter(ar__ar_id=user_id)
    leave_query = ArLeaveRequest.objects.filter(ar__ar_id=user_id, status='approved')

    # Filter by date range if provided
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()

            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)

            attendance_query = attendance_query.filter(date__range=[from_date, to_date])
            leave_query = leave_query.filter(
                Q(start_date__lte=to_date) & Q(end_date__gte=from_date)
            )
        except ValueError:
            return Response({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare attendance records with reset request status
    attendance_records = []
    for record in attendance_query.select_related('shift', 'location'):
        reset_request = ResetRequest.objects.filter(ar=record.ar, date=record.date).order_by('-created_at').first()
        attendance_records.append({
            'date': record.date,
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': record.total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request"
        })

    # Prepare leave records
    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            leave_records.append({
                'date': leave_date,
                'type': 'leave'
            })

    # Merge and sort all records by date
    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    # Convert date objects to string format for JSON response
    for record in all_records:
        if isinstance(record['date'], datetime):
            record['date'] = record['date'].strftime('%Y-%m-%d')
        elif isinstance(record['date'], date):
            record['date'] = record['date'].strftime('%Y-%m-%d')


    return Response({
        'all_records': all_records,
        'from_date': from_date,
        'to_date': to_date
    }, status=status.HTTP_200_OK)
    
@api_view(['GET', 'POST'])  # Allow GET requests for fetching requests
def ar_request_check_out_reset(request,user_id):
    if request.method == 'GET':
        requests = ResetRequest.objects.all().values()
        return Response(list(requests), status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # user_id = request.data.get('user_id')
        today = datetime.today()

        try:
            ar = Ar.objects.get(ar_id=user_id)
        except Ar.DoesNotExist:
            return Response({"detail": "ar not found."}, status=status.HTTP_404_NOT_FOUND)

        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        reset_request = ResetRequest(
            ar=ar,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)                        

@api_view(['GET'])
def ar_weekly_attendance_chart(request):
    user_id = request.session.get('user_id')  # Assuming employee ID is stored in session
    
    try:
        # Get the current week offset from GET parameters (how many weeks to move forward/backward)
        week_offset = int(request.GET.get('week_offset', 0))
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)  # Adjust the week by the offset
        end_of_week = start_of_week + timedelta(days=6)

        # Initialize a dictionary to store total hours per day with the date
        weekly_hours = {}
        labels = []
        
        # Variables to store total hours for the week and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Populate the days of the week (Monday to Saturday)
        for i in range(6):  # Monday to Saturday
            day_date = start_of_week + timedelta(days=i)
            day_label = day_date.strftime('%a %b %d')  # Format: "Mon Sep 11"
            labels.append(day_label)
            weekly_hours[day_label] = 0  # Initialize the hours for each day as 0

        # Get all attendance entries for the selected week
        attendance_records = Attendance.objects.filter(
            ar__ar_id=user_id,
            date__range=[start_of_week, end_of_week]
        )

        # Get all approved leave requests for the selected week
        approved_leaves = ArLeaveRequest.objects.filter(
            ar__ar_id=user_id,
            start_date__lte=end_of_week,
            end_date__gte=start_of_week,
            status='approved'
        )

        leave_days = set()
        for leave in approved_leaves:
            # Iterate through the leave days within the week
            leave_start = max(leave.start_date, start_of_week)
            leave_end = min(leave.end_date, end_of_week)
            for i in range((leave_end - leave_start).days + 1):
                leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
                leave_days.add(leave_day)

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                # Convert time_in and time_out to datetime and calculate work duration
                work_duration = (datetime.combine(datetime.today(), record.time_out) - 
                                 datetime.combine(datetime.today(), record.time_in)).total_seconds() / 3600
                day_label = record.date.strftime('%a %b %d')  # Ensure record.date is also handled as date
                if day_label in weekly_hours:
                    weekly_hours[day_label] += work_duration

                # Calculate total hours and overtime
                total_hours += work_duration
                if work_duration > daily_working_hours:
                    total_overtime += work_duration - daily_working_hours

        total_hours = round(total_hours, 2)
        total_overtime = round(total_overtime, 2)

        # Get the current month
        current_month = start_of_week.strftime('%B')

        work_data = list(weekly_hours.values())
        leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

        # Prepare the response data
        response_data = {
            'labels': labels,  # List of days with their respective dates
            'data': work_data,  # Corresponding hours worked
            'month': current_month,
            'leave_data': leave_data,  # Days where the employee was on leave
            'week_offset': week_offset,  # Current week offset for navigation
            'total_hours': total_hours,  # Total hours worked in the week
            'total_overtime': total_overtime,  # Total overtime worked in the week
        }

        # Return the success response with status 200
        return Response(response_data, status=status.HTTP_200_OK)
    
    except ValueError:
        # Handle errors related to invalid week_offset
        error_data = {
            'message': 'Invalid week_offset parameter. Please provide a valid integer value.'
        }
        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        error_data = {
            'message': 'An unexpected error occurred.',
            'error': str(e)
        }
        return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['GET'])
def ar_monthly_attendance_chart(request):
    try:
        # Assuming manager ID is stored in the session
        user_id = request.session.get('user_id')
        if not user_id:
            return Response({'error': 'Ar ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current month offset from GET parameters (how many months to move forward/backward)
        month_offset = int(request.GET.get('month_offset', 0))

        # Get today's date and adjust the month by the offset
        today = datetime.now()
        current_month = today.month + month_offset
        current_year = today.year

        # Handle year overflow/underflow when adjusting months
        if current_month < 1:
            current_month += 12
            current_year -= 1
        elif current_month > 12:
            current_month -= 12
            current_year += 1

        # Determine the first and last day of the month
        start_of_month = datetime(current_year, current_month, 1)
        last_day = monthrange(current_year, current_month)[1]  # Get the number of days in the month
        end_of_month = datetime(current_year, current_month, last_day)

        # Initialize data structures to store weekly hours and leave information
        weekly_hours = [0, 0, 0, 0]  # For 4 weeks
        working_days_per_week = [0, 0, 0, 0]  # To track the number of working days per week
        week_labels = ["Week 1", "Week 2", "Week 3", "Week 4"]  # Week labels
        
        # Variables to store total hours for the month and total overtime
        total_hours = 0
        total_overtime = 0
        daily_working_hours = 8  # Standard working hours per day

        # Get all attendance entries for the selected month
        attendance_records = Attendance.objects.filter(
            ar__ar_id=user_id,
            date__range=[start_of_month, end_of_month]
        )

        # Calculate total working hours and overtime for each day
        for record in attendance_records:
            if record.time_in and record.time_out:
                work_duration = datetime.combine(datetime.today(), record.time_out) - datetime.combine(datetime.today(), record.time_in)
                hours_worked = work_duration.total_seconds() / 3600  # Convert seconds to hours

                # Determine which week the record falls into (1-7 = Week 1, etc.)
                week_num = (record.date.day - 1) // 7  # Get week number (0, 1, 2, or 3)
                if week_num < 4:  # Ensure we don't go beyond Week 4
                    weekly_hours[week_num] += hours_worked
                    working_days_per_week[week_num] += 1  # Increment the count of working days for this week

                # Calculate total hours and overtime
                total_hours += hours_worked
                if hours_worked > daily_working_hours:
                    total_overtime += hours_worked - daily_working_hours

        total_hours = round(total_hours, 3)
        total_overtime = round(total_overtime, 3)

        # Calculate the average hours per week by dividing the total hours by the number of working days
        average_hours_per_week = []
        for week_num in range(4):
            if working_days_per_week[week_num] > 0:
                avg_hours = weekly_hours[week_num] / working_days_per_week[week_num]
            else:
                avg_hours = 0
            average_hours_per_week.append(round(avg_hours, 2))

        # Zip the week labels with the average working hours to pass them together in the response
        week_avg_data = list(zip(week_labels, average_hours_per_week))

        # Get the month name for display
        current_month_name = start_of_month.strftime('%B')

        # Prepare response data
        response_data = {
            'month': current_month_name,  # Current month name
            'week_avg_data': week_avg_data,  # Pass the zipped week labels and average hours
            'total_hours': total_hours,  # Total hours worked in the month
            'total_overtime': total_overtime,  # Total overtime worked in the month
            'month_offset': month_offset,  # Pass the current month offset for navigation
        }

        return Response(response_data, status=status.HTTP_200_OK)

    except ObjectDoesNotExist as e:
        return Response({'error': f'Record not found: {str(e)}'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def ar_attendance_request_reset(request):
    if request.method == 'POST':
        user_id = request.data.get('user_id')
        today = datetime.today()

        # Check if the manager exists
        try:
            ar = Ar.objects.get(ar_id=user_id)
        except Ar.DoesNotExist:
            return Response({"detail": "Hr not found."}, status=status.HTTP_404_NOT_FOUND)

        last_attendance = Attendance.objects.filter(
            ar=ar,
            date=today,
            time_in__isnull=False
        ).first()

        if not last_attendance:
            return Response({"detail": "You can't reset the checkout time before check-in."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the manager has already checked out
        if last_attendance.time_out is None:
            # Manager has not checked out yet
            return Response({"detail": "You can't reset the checkout time before checkout."}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if a reset request has already been made for today
        existing_request = ResetRequest.objects.filter(
            ar=ar,
            date=today,
            status='Pending'
        ).exists()

        if existing_request:
            return Response({"detail": "You have already sent the request. Please wait until the checkout time is reset."}, status=status.HTTP_400_BAD_REQUEST)

        # If the manager has checked in and no existing request, process the reset request
        request_type = request.data.get('request_type')
        request_description = request.data.get('request_description')

        # Insert the new reset request into the model
        reset_request = ResetRequest(
            ar=ar,
            date=today,
            request_type=request_type,
            request_description=request_description,
            status='Pending',
            created_at=datetime.now()
        )
        reset_request.save()

        return Response({"detail": "Your reset request has been submitted successfully."}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def check_in_with_auto_leave(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id or not operation:
        return Response({"error": "Supervisor ID and operation are required."}, status=status.HTTP_400_BAD_REQUEST)

    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        supervisor = Supervisor.objects.get(supervisor_id=user_id)

        # Check leave status
        today = datetime.now().date()
        leave_request = SupervisorLeaveRequest.objects.filter(
            supervisor=supervisor,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request and leave_request.is_auto_leave:
            late_login_reason = LateloginReason.objects.filter(
                leave_request=leave_request,
                status='approved'
            ).first()
            if late_login_reason:
                # Approved auto-leave: treat as normal day, remove leave
                leave_request.delete()
            else:
                return Response({
                    "error": f"Auto-leave reason is pending or rejected for {leave_request.start_date} to {leave_request.end_date}. Check-in is not allowed."
                }, status=status.HTTP_400_BAD_REQUEST)
        elif leave_request and not leave_request.is_auto_leave:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            today = datetime.now().date()
            if Attendance.objects.filter(supervisor=supervisor, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = datetime.now().time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            # Check if an approved late login reason exists for today to avoid re-creating auto-leave
            if not LateloginReason.objects.filter(
                supervisor=supervisor,
                date=today,
                status='approved'
            ).exists():
                if current_time > (datetime.combine(datetime.today(), shift.shift_start_time) + timedelta(hours=1)).time():
                    SupervisorLeaveRequest.objects.create(
                        user=supervisor.username,
                        user_id=supervisor.supervisor_id,
                        start_date=today,
                        end_date=today,
                        leave_type="personal",
                        reason="Auto Leave: Late or No Login",
                        status="pending",
                        supervisor=supervisor,
                        is_auto_leave=True
                    )
                    return Response({
                        "message": "Checked in successfully. Auto-leave created due to late login.",
                        "auto_leave_id": "pending"
                    }, status=status.HTTP_201_CREATED)

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                supervisor=supervisor,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = datetime.now().time()
            today = datetime.now().date()
            time_out = datetime.now().strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                supervisor__supervisor_id=user_id,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                return Response({"error": "No open attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(datetime.today(), shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = last_attendance.time_in
            total_working_time = datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), time_in)

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

    except Supervisor.DoesNotExist:
        return Response({'error': 'Supervisor not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def check_in_hr_with_auto_leave(request):
    """
    API endpoint to handle check-in with auto-leave creation for late HR check-ins or check-out.
    """
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id or not operation:
        return Response({"error": "HR ID and operation are required."}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        hr = Hr.objects.get(hr_id=user_id)

        # Check leave status
        today = timezone.localdate()
        leave_request = HrLeaveRequest.objects.filter(
            hr=hr,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request and leave_request.is_auto_leave:
            late_login_reason = HrLateLoginReason.objects.filter(
                late_request=leave_request,
                status='approved'
            ).first()
            if late_login_reason:
                # Approved auto-leave: treat as normal day, remove leave
                leave_request.delete()
            else:
                return Response({
                    "error": f"Auto-leave reason is pending or rejected for {leave_request.start_date} to {leave_request.end_date}. Check-in is not allowed."
                }, status=status.HTTP_400_BAD_REQUEST)
        elif leave_request and not leave_request.is_auto_leave:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                shift = Shift.objects.get(id=shift_number)
                location = Location.objects.get(location_name=location_name)
            except (Shift.DoesNotExist, Location.DoesNotExist):
                return Response({"error": "Shift or location not found."}, status=status.HTTP_400_BAD_REQUEST)

            if Attendance.objects.filter(hr=hr, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = timezone.localtime(timezone.now()).time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            # Check if an approved late login reason exists for today to avoid re-creating auto-leave
            if not HrLateLoginReason.objects.filter(
                hr=hr,
                date=today,
                status='approved'
            ).exists():
                if current_time > (datetime.combine(today, shift.shift_start_time) + timedelta(hours=1)).time():
                    HrLeaveRequest.objects.create(
                        user=hr.username,
                        user_id=hr.hr_id,
                        start_date=today,
                        end_date=today,
                        leave_type="personal",
                        reason="Auto Leave: Late or No Login",
                        status="pending",
                        hr=hr,
                        is_auto_leave=True,
                        email=hr.email
                    )
                    return Response({
                        "message": "Checked in successfully. Auto-leave created due to late login.",
                        "auto_leave_id": "pending"
                    }, status=status.HTTP_201_CREATED)

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                hr=hr,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = timezone.localtime(timezone.now()).time()
            today = timezone.localdate()
            time_out = current_time.strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                hr=hr,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                return Response({"error": "No open attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = time.strptime(last_attendance.time_in, '%H:%M:%S')
            time_in = datetime.combine(today, time(time_in.tm_hour, time_in.tm_min, time_in.tm_sec))
            total_working_time = datetime.combine(today, current_time) - time_in

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in.time() <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid operation. Use 'check_in' or 'check_out'."}, status=status.HTTP_400_BAD_REQUEST)

    except Hr.DoesNotExist:
        return Response({'error': 'HR not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def check_in_manager_with_auto_leave(request):
    """
    API endpoint to handle check-in with auto-leave creation for late Manager check-ins or check-out.
    """
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id or not operation:
        return Response({"error": "Manager ID and operation are required."}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(manager_id=user_id)

        # Check leave status
        today = timezone.localdate()
        leave_request = ManagerLeaveRequest.objects.filter(
            manager=manager,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request and leave_request.is_auto_leave:
            late_login_reason = ManagerLateLoginReason.objects.filter(
                leave_request=leave_request,
                status='approved'
            ).first()
            if late_login_reason:
                # Approved auto-leave: treat as normal day, remove leave
                leave_request.delete()
            else:
                return Response({
                    "error": f"Auto-leave reason is pending or rejected for {leave_request.start_date} to {leave_request.end_date}. Check-in is not allowed."
                }, status=status.HTTP_400_BAD_REQUEST)
        elif leave_request and not leave_request.is_auto_leave:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                shift = Shift.objects.get(id=shift_number)
                location = Location.objects.get(location_name=location_name)
            except (Shift.DoesNotExist, Location.DoesNotExist):
                return Response({"error": "Shift or location not found."}, status=status.HTTP_400_BAD_REQUEST)

            if Attendance.objects.filter(manager=manager, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = timezone.localtime(timezone.now()).time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            # Check if an approved late login reason exists for today to avoid re-creating auto-leave
            if not ManagerLateLoginReason.objects.filter(
                manager=manager,
                date=today,
                status='approved'
            ).exists():
                if current_time > (datetime.combine(today, shift.shift_start_time) + timedelta(hours=1)).time():
                    leave_request = ManagerLeaveRequest.objects.create(
                        user=manager.username,
                        user_id=manager.manager_id,
                        start_date=today,
                        end_date=today,
                        leave_type="personal",
                        reason="Auto Leave: Late or No Login",
                        status="pending",
                        manager=manager,
                        is_auto_leave=True,
                        email=manager.email
                    )
                    return Response({
                        "message": "Checked in successfully. Auto-leave created due to late login.",
                        "auto_leave_id": leave_request.id
                    }, status=status.HTTP_201_CREATED)

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                manager=manager,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = timezone.localtime(timezone.now()).time()
            today = timezone.localdate()
            time_out = current_time.strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                manager=manager,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                return Response({"error": "No open attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = time.strptime(last_attendance.time_in, '%H:%M:%S')
            time_in = datetime.combine(today, time(time_in.tm_hour, time_in.tm_min, time_in.tm_sec))
            total_working_time = datetime.combine(today, current_time) - time_in

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in.time() <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid operation. Use 'check_in' or 'check_out'."}, status=status.HTTP_400_BAD_REQUEST)

    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(['POST'])
def check_in_employee_with_auto_leave(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id or not operation:
        return Response({"error": "Employee ID and operation are required."}, status=status.HTTP_400_BAD_REQUEST)

    if timezone.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = Employee.objects.get(employee_id=user_id)

        # Check leave status
        today = timezone.localdate()
        leave_request = LeaveRequest.objects.filter(
            employee=employee,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request and leave_request.is_auto_leave:
            late_login_reason = EmployeeLateLoginReason.objects.filter(
                leave_request=leave_request,
                status='approved'
            ).first()
            if late_login_reason:
                # Approved auto-leave: treat as normal day, remove leave
                leave_request.delete()
            else:
                return Response({
                    "error": f"Auto-leave reason is pending or rejected for {leave_request.start_date} to {leave_request.end_date}. Check-in is not allowed."
                }, status=status.HTTP_400_BAD_REQUEST)
        elif leave_request and not leave_request.is_auto_leave:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_number = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_number, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_number)
            location = Location.objects.get(location_name=location_name)

            if Attendance.objects.filter(employee=employee, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            current_time = timezone.localtime(timezone.now()).time()
            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            # Check if an approved late login reason exists for today to avoid re-creating auto-leave
            if not EmployeeLateLoginReason.objects.filter(
                employee=employee,
                date=today,
                status='approved'
            ).exists():
                shift_start_datetime = timezone.make_aware(datetime.combine(today, shift.shift_start_time))
                if current_time > (shift_start_datetime + timedelta(hours=1)).time():
                    LeaveRequest.objects.create(
                        user=employee.username,
                        user_id=employee.employee_id,
                        start_date=today,
                        end_date=today,
                        leave_type="personal",
                        reason="Auto Leave: Late or No Login",
                        status="pending",
                        employee=employee,
                        is_auto_leave=True
                    )
                    return Response({
                        "message": "Checked in successfully. Auto-leave created due to late login.",
                        "auto_leave_id": "pending"
                    }, status=status.HTTP_201_CREATED)

            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                employee=employee,
                latitude=latitude,
                longitude=longitude,
            )
            return Response({"message": "Checked in successfully."}, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            current_time = timezone.localtime(timezone.now()).time()
            today = timezone.localdate()
            time_out = timezone.localtime(timezone.now()).strftime('%H:%M:%S')

            last_attendance = Attendance.objects.filter(
                employee__employee_id=user_id,
                date=today,
                time_out=None
            ).first()

            if not last_attendance:
                return Response({"error": "No open attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            shift_end_datetime = timezone.make_aware(datetime.combine(today, shift_end_time))
            overtime_start_datetime = shift_end_datetime + timedelta(minutes=10)
            overtime_start_time = overtime_start_datetime.time()

            current_datetime = timezone.localtime(timezone.now())

            if current_time < shift_end_time:
                out_status = 'Early'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
                time_out = shift_end_time.strftime('%H:%M:%S')
            else:
                out_status = 'Overtime'
                overtime = current_datetime - overtime_start_datetime
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

            time_in = datetime.strptime(last_attendance.time_in, '%H:%M:%S').time()
            time_in_datetime = timezone.make_aware(datetime.combine(today, time_in))
            total_working_time = current_datetime - time_in_datetime

            # Break deduction logic
            break_start = time(13, 0, 0)  # 1 PM
            break_end = time(14, 0, 0)    # 2 PM
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            last_attendance.time_out = time_out
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({"message": "Checked out successfully."}, status=status.HTTP_200_OK)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


######################## New User VIEWS After the  change flow ###########################################




# August 22 before  New FE Superadmin Attendance 
# @api_view(['GET'])
# def all_user_attendance_history(request):
#     try:
#         from_date = request.query_params.get('from_date')
#         to_date = request.query_params.get('to_date')

#         if from_date and to_date:
#             try:
#                 from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
#                 to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
#                 if from_date > to_date:
#                     return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
#             except ValueError:
#                 return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             from_date = None
#             to_date = None

#         users = User.objects.all().select_related('shift')
#         all_records = []

#         for user in users:
#             shift = user.shift
#             shift_start = shift.shift_start_time if shift else None
#             shift_end = shift.shift_end_time if shift else None

#             attendance_query = Attendance.objects.filter(user=user).select_related('shift', 'location')

#             # Choose the right leave request model
#             if user.designation == 'Employee':
#                 leave_query = LeaveRequest.objects.filter(user=user, status='approved')
#             elif user.designation == 'Supervisor':
#                 leave_query = SupervisorLeaveRequest.objects.filter(user=user, status='approved')
#             elif user.designation == 'Human Resources':
#                 leave_query = HrLeaveRequest.objects.filter(user=user, status='approved')
#             else:
#                 leave_query = []

#             if from_date and to_date:
#                 attendance_query = attendance_query.filter(date__range=[from_date, to_date])
#                 leave_query = leave_query.filter(Q(start_date__lte=to_date) & Q(end_date__gte=from_date))

#             attendance_records = []
#             for record in attendance_query:
#                 reset_request = ResetRequest.objects.filter(user=user, date=record.date).order_by('-created_at').first()

#                 overtime = "N/A"
#                 if shift_end and record.time_out and record.time_in:
#                     shift_end_datetime = datetime.combine(record.date, shift_end)
#                     time_out_datetime = datetime.combine(record.date, record.time_out)
#                     if time_out_datetime > shift_end_datetime:
#                         overtime_delta = time_out_datetime - shift_end_datetime
#                         total_seconds = int(overtime_delta.total_seconds())
#                         hours = total_seconds // 3600
#                         minutes = (total_seconds % 3600) // 60
#                         seconds = total_seconds % 60
#                         overtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

#                 total_working_hours = record.total_working_hours
#                 if record.time_in and record.time_out:
#                     time_in_datetime = datetime.combine(record.date, record.time_in)
#                     time_out_datetime = datetime.combine(record.date, record.time_out)
#                     if time_out_datetime >= time_in_datetime:
#                         working_hours_delta = time_out_datetime - time_in_datetime
#                         total_seconds = int(working_hours_delta.total_seconds())
#                         hours = total_seconds // 3600
#                         minutes = (total_seconds % 3600) // 60
#                         seconds = total_seconds % 60
#                         total_working_hours = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

#                 attendance_records.append({
#                     'user_id': user.user_id,
#                     'user_name': user.user_name,
#                     'designation': user.designation,
#                     'date': record.date.strftime('%Y-%m-%d'),
#                     'type': 'attendance',
#                     'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
#                     'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
#                     'total_working_hours': total_working_hours,
#                     'reset_status': reset_request.status if reset_request else "No Request",
#                     'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
#                     'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
#                     'out_status': record.out_status,
#                     'overtime': overtime,
#                     'location': record.location.location_name if record.location else None
#                 })

#             leave_records = []
#             for leave in leave_query:
#                 leave_days = (leave.end_date - leave.start_date).days + 1
#                 for i in range(leave_days):
#                     leave_date = leave.start_date + timedelta(days=i)
#                     if from_date and to_date and not (from_date <= leave_date <= to_date):
#                         continue
#                     leave_records.append({
#                         'user_id': user.user_id,
#                         'user_name': user.user_name,
#                         'designation': user.designation,
#                         'date': leave_date.strftime('%Y-%m-%d'),
#                         'type': 'leave',
#                         'time_in': None,
#                         'time_out': None,
#                         'total_working_hours': "00:00:00",
#                         'reset_status': "No Request",
#                         'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
#                         'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
#                         'out_status': None,
#                         'overtime': None,
#                     })

#             all_records.extend(attendance_records + leave_records)

#         all_records.sort(key=lambda x: x['date'])

#         return Response({
#             'all_records': all_records,
#             'from_date': from_date.strftime('%Y-%m-%d') if from_date else None,
#             'to_date': to_date.strftime('%Y-%m-%d') if to_date else None
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
######################################################################################################

# August 22 after  New FE Superadmin Attendance 
# USER = EMPLOYEE

@api_view(['GET'])
def all_user_attendance_history(request):
    try:
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                if from_date > to_date:
                    return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            from_date = None
            to_date = None

        users = User.objects.all().select_related('shift')
        all_records = []

        # Initialize counters
        present_count = 0
        late_count = 0
        halfday_count = 0
        absent_count = 0

        for user in users:
            shift = user.shift
            shift_start = shift.shift_start_time if shift else None
            shift_end = shift.shift_end_time if shift else None

            attendance_query = Attendance.objects.filter(user=user).select_related('shift', 'location')
            if from_date and to_date:
                attendance_query = attendance_query.filter(date__range=[from_date, to_date])

            attendance_records = []
            attendance_dates = set()

            for record in attendance_query:
                attendance_dates.add(record.date)
                reset_request = ResetRequest.objects.filter(user=user, date=record.date).order_by('-created_at').first()

                total_working_hours = "00:00:00"
                overtime = "00:00:00"
                dynamic_status = 'Absent'  # default

                # Respect pre-set statuses first
                if record.status:
                    if record.status.lower() == 'late':
                        dynamic_status = 'Late'
                    elif record.status.lower() == 'absent':
                        dynamic_status = 'Absent'
                    elif record.status.lower() == 'on leave':
                        dynamic_status = 'On Leave'

                # Determine status based on actual check-in
                if record.time_in:
                    time_in_datetime = datetime.combine(record.date, record.time_in)

                    if shift_start:
                        shift_start_datetime = datetime.combine(record.date, shift_start)
                        late_threshold = shift_start_datetime + timedelta(hours=1)

                        if time_in_datetime <= late_threshold:
                            dynamic_status = 'Present'
                        else:
                            dynamic_status = 'Late'

                    # Calculate total working hours & overtime if time_out exists
                    if record.time_out and shift_end:
                        time_out_datetime = datetime.combine(record.date, record.time_out)
                        shift_end_datetime = datetime.combine(record.date, shift_end)

                        if dynamic_status == 'Present':
                            if time_out_datetime < shift_end_datetime:
                                dynamic_status = 'Half Day'
                                total_working_hours = str(time_out_datetime - time_in_datetime)
                                overtime = "00:00:00"
                            else:
                                total_working_hours = str(shift_end_datetime - time_in_datetime)
                                if time_out_datetime > shift_end_datetime:
                                    overtime_delta = time_out_datetime - shift_end_datetime
                                    total_seconds = int(overtime_delta.total_seconds())
                                    hours = total_seconds // 3600
                                    minutes = (total_seconds % 3600) // 60
                                    seconds = total_seconds % 60
                                    overtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

                # Increment counters
                if dynamic_status.lower() == 'present':
                    present_count += 1
                elif dynamic_status.lower() == 'late':
                    late_count += 1
                elif dynamic_status.lower() == 'half day':
                    halfday_count += 1
                else:
                    absent_count += 1

                attendance_records.append({
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'designation': user.designation,
                    'date': record.date.strftime('%Y-%m-%d'),
                    'type': 'attendance',
                    'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
                    'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
                    'total_working_hours': total_working_hours,
                    'reset_status': reset_request.status if reset_request else "No Request",
                    'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
                    'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
                    'out_status': record.out_status,
                    'overtime': overtime,
                    'status': dynamic_status,
                    'location': record.location.location_name if record.location else None
                })

            # -------------------------------
            # Absent Records for days with no attendance
            # -------------------------------
            if from_date and to_date:
                day_cursor = from_date
                while day_cursor <= to_date:
                    if day_cursor not in attendance_dates:
                        absent_count += 1
                        all_records.append({
                            'user_id': user.user_id,
                            'user_name': user.user_name,
                            'designation': user.designation,
                            'date': day_cursor.strftime('%Y-%m-%d'),
                            'type': 'absent',
                            'time_in': None,
                            'time_out': None,
                            'total_working_hours': "00:00:00",
                            'reset_status': "No Request",
                            'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
                            'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
                            'out_status': None,
                            'overtime': None,
                            'status': 'Absent',
                        })
                    day_cursor += timedelta(days=1)

            all_records.extend(attendance_records)

        all_records.sort(key=lambda x: (x['date'], x['user_id']))

        return Response({
            'all_records': all_records,
            'from_date': from_date.strftime('%Y-%m-%d') if from_date else None,
            'to_date': to_date.strftime('%Y-%m-%d') if to_date else None,
            'present_count': present_count,
            'late_count': late_count,
            'halfday_count': halfday_count,
            'absent_count': absent_count,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def admin_user_reset_requests(request):
    """
    Combined reset requests for all user types (Employee, HR, Supervisor)
    based on designation in User model.
    """
    # Fetch all pending reset requests that have a user linked
    reset_requests = ResetRequest.objects.filter(status='Pending', user__isnull=False)

    combined_requests = []

    for req in reset_requests:
        try:
            attendance = Attendance.objects.get(user=req.user, date=req.date)

            combined_requests.append({
                'id': req.id,
                'user_id': req.user.user_id,
                'username': req.user.username,
                'designation': req.user.designation,
                'request_type': req.request_type,
                'request_description': req.request_description,
                'date': req.date,
                'shift': attendance.shift.shift_number if attendance.shift else None,
                'time_in': attendance.time_in,
                'time_out': attendance.time_out,
                'in_status': attendance.in_status,
                'out_status': attendance.out_status,
                'notes': attendance.notes,
                'status': req.status,
            })
        except Attendance.DoesNotExist:
            # If no matching attendance, skip this request
            continue

    return Response({"reset_requests": combined_requests}, status=status.HTTP_200_OK)


@api_view(['POST'])
def admin_approve_and_reset_user_reset_request(request, id):
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Step 1: Approve the reset request
    reset_request.status = 'Approved'
    reset_request.save()

    user = reset_request.user
    date = reset_request.date

    if not user or not user.designation:
        return Response({"detail": "Invalid user or missing designation."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        attendance_record = Attendance.objects.get(user=user, date=date)
    except Attendance.DoesNotExist:
        return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)

    clear_checkout = request.data.get('clear_checkout', False)
    checkout_time_str = request.data.get('checkout_time')

    if clear_checkout:
        attendance_record.time_out = None
        attendance_record.out_status = None
        attendance_record.overtime = None
        attendance_record.total_working_hours = None
    else:
        if checkout_time_str:
            try:
                checkout_time = datetime.strptime(checkout_time_str, '%H:%M:%S').time()
            except ValueError:
                return Response({"detail": "Invalid time format. Please use HH:MM:SS."}, status=status.HTTP_400_BAD_REQUEST)

            attendance_record.time_out = checkout_time
            attendance_record.out_status = 'Updated by Admin'

            # Calculate total working hours
            time_in = datetime.strptime(str(attendance_record.time_in), '%H:%M:%S').time()
            time_out = checkout_time

            today = datetime.today()
            time_in_datetime = datetime.combine(today, time_in)
            time_out_datetime = datetime.combine(today, time_out)

            total_working_time = time_out_datetime - time_in_datetime
            total_hours = total_working_time.seconds // 3600
            total_minutes = (total_working_time.seconds % 3600) // 60
            total_seconds = total_working_time.seconds % 60
            attendance_record.total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

            # Calculate overtime
            shift_end_time = attendance_record.shift.shift_end_time
            shift_end_datetime = datetime.combine(today, shift_end_time)
            overtime_start_time = shift_end_datetime + timedelta(minutes=10)

            if time_out_datetime > overtime_start_time:
                overtime = time_out_datetime - overtime_start_time
                overtime_hours = overtime.seconds // 3600
                overtime_minutes = (overtime.seconds % 3600) // 60
                overtime_seconds = overtime.seconds % 60
                attendance_record.overtime = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"
            else:
                attendance_record.overtime = "00:00:00"

    attendance_record.save()
    return Response({"detail": "Reset request approved and checkout time updated successfully."}, status=status.HTTP_200_OK)



@api_view(['POST'])
def admin_reject_user_reset_request(request, id):
    try:
        reset_request = ResetRequest.objects.get(id=id)
    except ResetRequest.DoesNotExist:
        return Response({"detail": "Reset request not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate the user and designation
    user = reset_request.user
    if not user or not user.designation:
        return Response({"detail": "Invalid user or missing designation."}, status=status.HTTP_400_BAD_REQUEST)

    # Reject the reset request
    reset_request.status = 'Rejected'
    reset_request.save()

    return Response({"detail": "Reset request rejected successfully."}, status=status.HTTP_200_OK)


#######################################################################################################

#Aug 22 before changing the submit for new file

# @api_view(['POST'])
# def submit_user_attendance(request):
#     user_id = request.data.get('user_id')
#     operation = request.data.get('operation')

#     if not user_id:
#         return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#     # No attendance on Sundays
#     if datetime.now().weekday() == 6:
#         return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         user = User.objects.get(user_id=user_id)
#         today = datetime.now().date()
#         designation = user.designation.lower()

#         # Map designation to appropriate leave model
#         leave_model = {
#             'employee': LeaveRequest,
#             'supervisor': SupervisorLeaveRequest,
#             'hr': HrLeaveRequest
#         }.get(designation)

#         if not leave_model:
#             return Response({"error": f"Invalid user designation '{designation}'."}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if user is on approved leave today
#         leave_request = leave_model.objects.filter(
#             user=user,
#             start_date__lte=today,
#             end_date__gte=today,
#             status='approved'
#         ).first()

#         if leave_request:
#             return Response({
#                 "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         if operation == 'check_in':
#             shift_id = request.data.get('shift')
#             location_name = request.data.get('location')
#             notes = request.data.get('notes')
#             latitude = request.data.get('latitude')
#             longitude = request.data.get('longitude')

#             if not all([shift_id, location_name]):
#                 return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

#             shift = Shift.objects.get(id=shift_id)
#             location = Location.objects.get(location_name=location_name)

#             # Check if already checked in today
#             if Attendance.objects.filter(user=user, date=today).exists():
#                 return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

#             current_time = datetime.now().time()
#             shift_start_dt = datetime.combine(today, shift.shift_start_time)
#             one_hour_later = shift_start_dt + timedelta(hours=1)
#             current_dt = datetime.combine(today, current_time)

#             # Late check-in logic (> 1 hour after shift start)
#             if current_dt > one_hour_later:
#                 reset_approved = ResetRequest.objects.filter(
#                     user=user,
#                     date=today,
#                     status='approved'
#                 ).exists()
#                 if not reset_approved:
#                     return Response({
#                         "error": f"You are on leave today. Check-in is not allowed."
#                     }, status=status.HTTP_400_BAD_REQUEST)

#             in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

#             Attendance.objects.create(
#                 date=today,
#                 shift=shift,
#                 location=location,
#                 notes=notes,
#                 time_in=current_time.strftime('%H:%M:%S'),
#                 in_status=in_status,
#                 user=user,
#                 latitude=latitude,
#                 longitude=longitude,
#             )
#             return Response({
#                 "message": "Checked in successfully.",
#                 "time_in": current_time.strftime('%H:%M:%S'),
#                 "in_status": in_status
#             }, status=status.HTTP_201_CREATED)

#         elif operation == 'check_out':
#             current_time = datetime.now().time()
#             time_out_str = datetime.now().strftime('%H:%M:%S')

#             attendance_qs = Attendance.objects.filter(user=user, date=today, time_out=None)
#             last_attendance = attendance_qs.first()

#             if not last_attendance:
#                 reset_approved = ResetRequest.objects.filter(user=user, date=today, status='approved').exists()
#                 if reset_approved:
#                     last_attendance = Attendance.objects.filter(user=user, date=today).first()
#                 else:
#                     return Response({"error": "You have already checked out for today."}, status=status.HTTP_400_BAD_REQUEST)

#             if not last_attendance:
#                 return Response({"error": "No attendance record found for today."}, status=status.HTTP_400_BAD_REQUEST)

#             shift = last_attendance.shift
#             shift_end_time = shift.shift_end_time
#             overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

#             if current_time < shift_end_time:
#                 out_status = 'Early'
#                 overtime_str = '00:00:00'
#             elif shift_end_time <= current_time <= overtime_start_time:
#                 out_status = 'On time'
#                 overtime_str = '00:00:00'
#             else:
#                 out_status = 'Overtime'
#                 overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
#                 overtime_hours = overtime.seconds // 3600
#                 overtime_minutes = (overtime.seconds % 3600) // 60
#                 overtime_seconds = overtime.seconds % 60
#                 overtime_str = f"{overtime_hours:02}:{overtime_minutes:02}:{overtime_seconds:02}"

#             time_in = last_attendance.time_in
#             total_working_time = datetime.combine(today, current_time) - datetime.combine(today, time_in)

#             # Deduct 1 hour break if applicable
#             break_start = time(13, 0, 0)
#             break_end = time(14, 0, 0)
#             if time_in <= break_start and current_time >= break_end:
#                 total_working_time -= timedelta(hours=1)

#             total_hours = total_working_time.seconds // 3600
#             total_minutes = (total_working_time.seconds % 3600) // 60
#             total_seconds = total_working_time.seconds % 60
#             total_working_hours = f"{total_hours:02}:{total_minutes:02}:{total_seconds:02}"

#             last_attendance.time_out = time_out_str
#             last_attendance.out_status = out_status
#             last_attendance.overtime = overtime_str
#             last_attendance.total_working_hours = total_working_hours
#             last_attendance.save()

#             return Response({
#                 "message": "Checked out successfully.",
#                 "time_out": time_out_str,
#                 "out_status": out_status
#             }, status=status.HTTP_200_OK)

#         else:
#             return Response({"error": "Invalid operation. Use 'check_in' or 'check_out'."}, status=status.HTTP_400_BAD_REQUEST)

#     except User.DoesNotExist:
#         return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
#     except (Shift.DoesNotExist, Location.DoesNotExist):
#         return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#######################################################################################################################################

#Aug 22 after changing the submit for new file


@api_view(['POST'])
def submit_user_attendance(request):
    user_id = request.data.get('user_id')
    operation = request.data.get('operation')

    if not user_id:
        return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # No attendance on Sundays
    if datetime.now().weekday() == 6:
        return Response({"error": "Check-in is not allowed on Sundays."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(user_id=user_id)
        today = datetime.now().date()
        current_time = datetime.now().time()
        current_dt = datetime.combine(today, current_time)
        designation = user.designation.lower()

        # Map designation to leave model
        leave_model = {
            'employee': LeaveRequest,
            'supervisor': SupervisorLeaveRequest,
            'hr': HrLeaveRequest
        }.get(designation)

        if not leave_model:
            return Response({"error": f"Invalid user designation '{designation}'."}, status=status.HTTP_400_BAD_REQUEST)

        # Approved leave today
        leave_request = leave_model.objects.filter(
            user=user,
            start_date__lte=today,
            end_date__gte=today,
            status='approved'
        ).first()
        if leave_request:
            return Response({
                "error": f"You are on leave today ({leave_request.start_date} to {leave_request.end_date}). Check-in is not allowed."
            }, status=status.HTTP_400_BAD_REQUEST)

        if operation == 'check_in':
            shift_id = request.data.get('shift')
            location_name = request.data.get('location')
            notes = request.data.get('notes')
            latitude = request.data.get('latitude')
            longitude = request.data.get('longitude')

            if not all([shift_id, location_name]):
                return Response({"error": "Shift and location are required."}, status=status.HTTP_400_BAD_REQUEST)

            shift = Shift.objects.get(id=shift_id)
            location = Location.objects.get(location_name=location_name)

            # Block if already checked in today
            if Attendance.objects.filter(user=user, date=today).exists():
                return Response({"error": "You have already checked in for today."}, status=status.HTTP_200_OK)

            shift_start_dt = datetime.combine(today, shift.shift_start_time)
            one_hour_later = shift_start_dt + timedelta(hours=1)
            shift_end_dt = datetime.combine(today, shift.shift_end_time)

            # Block check-in after shift end
            if current_dt > shift_end_dt:
                return Response({"error": "Shift ended. Check-in not allowed."}, status=400)

            # Determine attendance status
            if current_dt <= one_hour_later:
                attendance_status = 'Present'
            else:
                # Needs admin approval to check-in late
                reset_approved = ResetRequest.objects.filter(user=user, date=today, status='approved').exists()
                if reset_approved:
                    attendance_status = 'Late'
                else:
                    return Response({
                        "error": "Check-in after 1 hour requires admin approval. You cannot check-in."
                    }, status=status.HTTP_400_BAD_REQUEST)

            in_status = 'Late' if current_time > shift.shift_start_time else 'On time'

            # Create attendance record
            Attendance.objects.create(
                date=today,
                shift=shift,
                location=location,
                notes=notes,
                time_in=current_time.strftime('%H:%M:%S'),
                in_status=in_status,
                status=attendance_status,
                user=user,
                latitude=latitude,
                longitude=longitude,
            )

            return Response({
                "message": "Checked in successfully.",
                "time_in": current_time.strftime('%H:%M:%S'),
                "in_status": in_status,
                "status": attendance_status
            }, status=status.HTTP_201_CREATED)

        elif operation == 'check_out':
            time_out_str = datetime.now().strftime('%H:%M:%S')
            attendance_qs = Attendance.objects.filter(user=user, date=today, time_out=None)
            last_attendance = attendance_qs.first()

            if not last_attendance:
                reset_approved = ResetRequest.objects.filter(user=user, date=today, status='approved').exists()
                if reset_approved:
                    last_attendance = Attendance.objects.filter(user=user, date=today).first()
                else:
                    return Response({"error": "You have not checked in today."}, status=status.HTTP_400_BAD_REQUEST)

            shift = last_attendance.shift
            shift_end_time = shift.shift_end_time
            overtime_start_time = (datetime.combine(today, shift_end_time) + timedelta(minutes=10)).time()

            # Determine out_status and overtime
            if current_time < shift_end_time:
                out_status = 'Early'
                last_attendance.status = 'Half Day'
                overtime_str = '00:00:00'
            elif shift_end_time <= current_time <= overtime_start_time:
                out_status = 'On time'
                overtime_str = '00:00:00'
            else:
                out_status = 'Overtime'
                overtime = datetime.combine(today, current_time) - datetime.combine(today, overtime_start_time)
                hours, remainder = divmod(overtime.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                overtime_str = f"{hours:02}:{minutes:02}:{seconds:02}"

            # Calculate total working hours
            time_in = datetime.strptime(str(last_attendance.time_in), '%H:%M:%S').time()
            total_working_time = datetime.combine(today, current_time) - datetime.combine(today, time_in)

            # Deduct 1-hour lunch break if applicable
            break_start = time(13, 0, 0)
            break_end = time(14, 0, 0)
            if time_in <= break_start and current_time >= break_end:
                total_working_time -= timedelta(hours=1)

            hours, remainder = divmod(total_working_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            total_working_hours = f"{hours:02}:{minutes:02}:{seconds:02}"

            # Update attendance
            last_attendance.time_out = time_out_str
            last_attendance.out_status = out_status
            last_attendance.overtime = overtime_str
            last_attendance.total_working_hours = total_working_hours
            last_attendance.save()

            return Response({
                "message": "Checked out successfully.",
                "time_out": time_out_str,
                "out_status": out_status,
                "status": last_attendance.status
            }, status=status.HTTP_200_OK)

        else:
            return Response({"error": "Invalid operation. Use 'check_in' or 'check_out'."}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except (Shift.DoesNotExist, Location.DoesNotExist):
        return Response({'error': 'Shift or location not found.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
















#######################################################################################################################################

@api_view(['POST'])
def user_attendance_form(request, user_id):
    try:
        user = User.objects.get(user_id=user_id)  

        designation = user.designation.lower()
        today = timezone.localdate()

        # Prepare default response values
        show_checkout = False
        thank_you_message = ''
        already_checked_out = False
        first_in_time = "--:--"
        last_out_time = "--:--"
        on_leave = False

        # Location & Shift from User model
        locations = [user.location] if user.location else []
        location_serializer = LocationSerializer(locations, many=True)
        shift = user.shift
        shift_serializer = ShiftSerializer(shift) if shift else None

        # Attendance filtered by user
        last_attendance = Attendance.objects.filter(user=user, date=today).first()

        # Determine leave based on designation and user
        leave_request = None
        if designation == "employee":
            leave_request = LeaveRequest.objects.filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
                status='approved'
            ).first()
        elif designation == "supervisor":
            leave_request = SupervisorLeaveRequest.objects.filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
                status='approved'
            ).first()
        elif designation == "hr":
            leave_request = HrLeaveRequest.objects.filter(
                user=user,
                start_date__lte=today,
                end_date__gte=today,
                status='approved'
            ).first()

        on_leave = bool(leave_request)

        if last_attendance:
            if last_attendance.time_in:
                first_in_time = last_attendance.time_in.strftime("%I:%M %p")
            if last_attendance.time_out:
                last_out_time = last_attendance.time_out.strftime("%I:%M %p")

            if last_attendance.time_out is None:
                show_checkout = True
                thank_you_message = 'Thanks for today'
            else:
                # Check approved reset requests by user and date
                approved_reset = ResetRequest.objects.filter(
                    user=user,
                    date=today,
                    status__iexact='approved'
                ).exists()
                if approved_reset:
                    show_checkout = True
                    thank_you_message = 'Reset approved — You may check out again'
                else:
                    already_checked_out = True
                    thank_you_message = 'You have already checked out for today.'
                    return Response({
                        'locations': location_serializer.data,
                        'shift': shift_serializer.data if shift_serializer else None,
                        'show_checkout': False,
                        'thank_you_message': thank_you_message,
                        'already_checked_out': already_checked_out,
                        'first_in_time': first_in_time,
                        'last_out_time': last_out_time,
                        'on_leave': on_leave,
                    }, status=status.HTTP_200_OK)

        if on_leave:
            return Response({
                'locations': location_serializer.data,
                'shift': shift_serializer.data if shift_serializer else None,
                'show_checkout': False,
                'thank_you_message': '',
                'already_checked_out': False,
                'first_in_time': first_in_time,
                'last_out_time': last_out_time,
                'on_leave': on_leave,
            }, status=status.HTTP_200_OK)

        return Response({
            'locations': location_serializer.data,
            'shift': shift_serializer.data if shift_serializer else None,
            'show_checkout': show_checkout,
            'thank_you_message': thank_you_message,
            'already_checked_out': already_checked_out,
            'first_in_time': first_in_time,
            'last_out_time': last_out_time,
            'on_leave': on_leave,
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def user_employee_attendance_history(request, user_id):
    from_date = request.query_params.get('from_date')
    to_date = request.query_params.get('to_date')

    # Validate and parse dates
    if from_date and to_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            if from_date > to_date:
                return Response({'error': 'From date cannot be after to date.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        from_date = None
        to_date = None

    # Get the user with designation "Employee"
    try:
        user = User.objects.get(user_id=user_id)
        if user.designation != "Employee":
            return Response({'error': 'This endpoint is only available for users with Employee designation.'}, status=status.HTTP_403_FORBIDDEN)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Assigned shift from user
    assigned_shift = user.shift

    # Filter attendance and leave for the user
    attendance_query = Attendance.objects.filter(user__user_id=user_id).select_related('shift', 'location')
    leave_query = LeaveRequest.objects.filter(user__user_id=user_id, status='approved')

    if from_date and to_date:
        attendance_query = attendance_query.filter(date__range=[from_date, to_date])
        leave_query = leave_query.filter(Q(start_date__lte=to_date) & Q(end_date__gte=from_date))

    attendance_records = []
    for record in attendance_query:
        reset_request = ResetRequest.objects.filter(user=record.user, date=record.date).order_by('-created_at').first()
        shift = user.shift
        shift_start = shift.shift_start_time if shift else None
        shift_end = shift.shift_end_time if shift else None

        # Overtime calculation
        overtime = "N/A"
        if shift_end and record.time_out and record.time_in:
            shift_end_datetime = datetime.combine(record.date, shift_end)
            time_out_datetime = datetime.combine(record.date, record.time_out)
            if time_out_datetime > shift_end_datetime:
                overtime_hours = (time_out_datetime - shift_end_datetime).total_seconds() / 3600
                overtime = round(overtime_hours, 2)

        # Working hours
        total_working_hours = record.total_working_hours
        if record.time_in and record.time_out:
            time_in_datetime = datetime.combine(record.date, record.time_in)
            time_out_datetime = datetime.combine(record.date, record.time_out)
            if time_out_datetime >= time_in_datetime:
                delta = time_out_datetime - time_in_datetime
                hours = delta.seconds // 3600
                minutes = (delta.seconds % 3600) // 60
                seconds = delta.seconds % 60
                total_working_hours = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        attendance_records.append({
            'employee_id': user.user_id,
            'employee_name': user.user_name,
            'date': record.date.strftime('%Y-%m-%d'),
            'type': 'attendance',
            'time_in': record.time_in.strftime('%H:%M:%S') if record.time_in else None,
            'time_out': record.time_out.strftime('%H:%M:%S') if record.time_out else None,
            'total_working_hours': total_working_hours,
            'reset_status': reset_request.status if reset_request else "No Request",
            'shift_start_time': shift_start.strftime('%H:%M:%S') if shift_start else None,
            'shift_end_time': shift_end.strftime('%H:%M:%S') if shift_end else None,
            'out_status': record.out_status,
            'overtime': overtime,
        })

    leave_records = []
    for leave in leave_query:
        leave_days = (leave.end_date - leave.start_date).days + 1
        for i in range(leave_days):
            leave_date = leave.start_date + timedelta(days=i)
            if from_date and to_date and not (from_date <= leave_date <= to_date):
                continue
            leave_records.append({
                'employee_id': user.user_id,
                'employee_name': user.user_name,
                'date': leave_date.strftime('%Y-%m-%d'),
                'type': 'leave',
                'time_in': None,
                'time_out': None,
                'total_working_hours': "00:00:00",
                'reset_status': "No Request",
                'shift_start_time': assigned_shift.shift_start_time.strftime('%H:%M:%S') if assigned_shift else None,
                'shift_end_time': assigned_shift.shift_end_time.strftime('%H:%M:%S') if assigned_shift else None,
                'out_status': None,
                'overtime': None,
            })

    all_records = attendance_records + leave_records
    all_records.sort(key=lambda x: x['date'])

    return Response({
        'all_records': all_records,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else None,
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else None
    }, status=status.HTTP_200_OK)
    

# @api_view(['GET'])
# def user_weekly_attendance_chart(request, user_id):
#     try:
#         # Validate user
#         try:
#             user = User.objects.get(user_id=user_id)
#         except User.DoesNotExist:
#             return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#         designation = user.designation

#         # Get week offset from query params
#         week_offset = int(request.query_params.get('week_offset', 0))

#         today = datetime.now().date()
#         start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
#         end_of_week = start_of_week + timedelta(days=5)

#         labels = []
#         weekly_hours = {}
#         total_hours = 0
#         total_overtime = 0
#         daily_working_hours = 8

#         for i in range(6):
#             day_date = start_of_week + timedelta(days=i)
#             day_label = day_date.strftime('%a %b %d')
#             labels.append(day_label)
#             weekly_hours[day_label] = 0

#         # Attendance
#         attendance_records = Attendance.objects.filter(
#             user=user,
#             date__range=[start_of_week, end_of_week]
#         )

#         # Permission Hours (for Employees only)
#         permission_hours = {label: 0 for label in labels}
#         if designation == 'Employee':
#             permission_records = PermissionHour.objects.filter(
#                 user=user,
#                 date__range=[start_of_week, end_of_week],
#                 status='Approved'
#             )
#             for permission in permission_records:
#                 duration = (
#                     datetime.combine(datetime.today(), permission.end_time) -
#                     datetime.combine(datetime.today(), permission.start_time)
#                 ).total_seconds() / 3600
#                 label = permission.date.strftime('%a %b %d')
#                 if label in permission_hours:
#                     permission_hours[label] += duration
#         permission_data = list(permission_hours.values())

#         # Leaves
#         if designation == 'Employee':
#             leave_model = LeaveRequest
#         elif designation == 'Supervisor':
#             leave_model = SupervisorLeaveRequest
#         else:
#             leave_model = HrLeaveRequest

#         approved_leaves = leave_model.objects.filter(
#             user=user,
#             status='approved',
#             start_date__lte=end_of_week,
#             end_date__gte=start_of_week
#         )

#         leave_days = set()
#         for leave in approved_leaves:
#             leave_start = max(leave.start_date, start_of_week)
#             leave_end = min(leave.end_date, end_of_week)
#             for i in range((leave_end - leave_start).days + 1):
#                 leave_day = (leave_start + timedelta(days=i)).strftime('%a %b %d')
#                 leave_days.add(leave_day)

#         # Process attendance
#         for record in attendance_records:
#             if record.time_in and record.time_out:
#                 hours = (
#                     datetime.combine(datetime.today(), record.time_out) -
#                     datetime.combine(datetime.today(), record.time_in)
#                 ).total_seconds() / 3600
#                 label = record.date.strftime('%a %b %d')
#                 if label in weekly_hours:
#                     weekly_hours[label] += hours
#                 total_hours += hours
#                 if hours > daily_working_hours:
#                     total_overtime += hours - daily_working_hours

#         # Final data
#         work_data = list(weekly_hours.values())
#         leave_data = [daily_working_hours if label in leave_days else 0 for label in labels]

#         response_data = {
#             'labels': labels,
#             'work_data': work_data,
#             'permission_data': permission_data if designation == 'Employee' else [0] * len(labels),
#             'leave_data': leave_data,
#             'month': start_of_week.strftime('%B'),
#             'week_offset': week_offset,
#             'total_hours': round(total_hours, 2),
#             'total_overtime': round(total_overtime, 2),
#             'designation': designation
#         }

#         return Response(response_data, status=status.HTTP_200_OK)

#     except ValueError:
#         return Response({"message": "Invalid week_offset parameter. Please provide a valid integer."},
#                         status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"message": "An unexpected error occurred.", "error": str(e)},
#                         status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from datetime import datetime
import calendar

# @api_view(['GET'])
# def all_user_monthly_summary(request):
#     try:
#         month = request.query_params.get('month', '').strip()
#         if not month:
#             return Response({"error": "Please provide month in YYYY-MM format"}, status=400)

#         # Safe parsing
#         try:
#             parts = month.split("-")
#             if len(parts) != 2:
#                 raise ValueError("Invalid month format")
#             year_str, month_str = parts
#             year = int(year_str)
#             month_num = int(month_str.lstrip("0") or "0")
#             if not (1 <= month_num <= 12):
#                 return Response({"error": "Month must be between 01 and 12"}, status=400)
#         except Exception:
#             return Response({"error": "Invalid month format. Use YYYY-MM"}, status=400)

#         start_date = datetime(year, month_num, 1).date()
#         days_in_month = calendar.monthrange(year, month_num)[1]
#         end_date = datetime(year, month_num, days_in_month).date()

#         today = datetime.now().date()
#         is_current_month = today.year == year and today.month == month_num
#         last_completed_day = min(today.day, days_in_month) if is_current_month else days_in_month

#         users = User.objects.all().select_related("department")
#         result = []

#         total_present = total_absent = total_late = total_half = total_on_leave = 0

#         for user in users:
#             attendance_qs = Attendance.objects.filter(user=user, date__range=[start_date, end_date])
#             if not attendance_qs.exists():
#                 continue

#             filtered_attendance = [rec for rec in attendance_qs if rec.date.day <= last_completed_day]

#             present_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "present")
#             late_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "late")
#             half_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "half day")
#             absent_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "absent")
#             leave_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "on leave")

#             total_present += present_days
#             total_absent += absent_days
#             total_late += late_days
#             total_half += half_days
#             total_on_leave += leave_days

#             # Overtime calculation
#             overtime_seconds = 0
#             for rec in attendance_qs:
#                 if rec.overtime:
#                     h, m, s = map(int, str(rec.overtime).split(":"))
#                     overtime_seconds += h*3600 + m*60 + s
#             overtime_hours = round(overtime_seconds / 3600, 1)

#             total_days_recorded = last_completed_day
#             attendance_rate = ((present_days + late_days + 0.5 * half_days) / total_days_recorded * 100) if total_days_recorded > 0 else 0


#             result.append({
#                 "employeeId": user.user_id,
#                 "name": user.user_name,
#                 "designation": user.designation,
#                 "department": user.department.department_name if user.department else "N/A",
#                 "totalDays": days_in_month,
#                 "presentDays": present_days,
#                 "absentDays": absent_days,
#                 "lateDays": late_days,
#                 "halfDays": half_days,
#                 "leaveDays": leave_days,
#                 "overtimeHours": overtime_hours,
#                 "attendanceRate": round(attendance_rate, 1),
#                 "avatar": "".join([p[0] for p in user.user_name.split()][:2]).upper()
#             })

#         total_employees = len(result)
#         total_days_recorded_for_all = total_employees * last_completed_day

#         # Overall attendance rate across all users
#         overall_attendance_rate = ((total_present + total_late + 0.5 * total_half) / total_days_recorded_for_all * 100) if total_days_recorded_for_all > 0 else 0

#         overall_attendance_rate = round(overall_attendance_rate, 1)

#         return Response({
#             "data": result,
#             "totals": {
#                 "totalEmployees": total_employees,
#                 "totalPresent": total_present,
#                 "totalAbsent": total_absent,
#                 "totalLate": total_late,
#                 "totalHalfDays": total_half,
#                 "totalOnLeave": total_on_leave,
#                 "overallAttendanceRate": overall_attendance_rate
#             }
#         }, status=200)

#     except Exception as e:
#         return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def all_user_monthly_summary(request):
    try:
        month = request.query_params.get('month', '').strip()
        if not month:
            return Response({"error": "Please provide month in YYYY-MM format"}, status=400)

        # Safe parsing
        try:
            parts = month.split("-")
            if len(parts) != 2:
                raise ValueError("Invalid month format")
            year_str, month_str = parts
            year = int(year_str)
            month_num = int(month_str.lstrip("0") or "0")
            if not (1 <= month_num <= 12):
                return Response({"error": "Month must be between 01 and 12"}, status=400)
        except Exception:
            return Response({"error": "Invalid month format. Use YYYY-MM"}, status=400)

        start_date = datetime(year, month_num, 1).date()
        days_in_month = calendar.monthrange(year, month_num)[1]
        end_date = datetime(year, month_num, days_in_month).date()

        today = datetime.now().date()
        is_current_month = today.year == year and today.month == month_num
        last_completed_day = min(today.day, days_in_month) if is_current_month else days_in_month

        users = User.objects.all().select_related("department")
        result = []

        total_present = total_absent = total_late = total_half = total_on_leave = 0

        for user in users:
            attendance_qs = Attendance.objects.filter(user=user, date__range=[start_date, end_date])
            if not attendance_qs.exists():
                continue

            # Only consider ended days
            filtered_attendance = [rec for rec in attendance_qs if rec.date.day <= last_completed_day]

            # --- Dynamic status calculation (like daily API) ---
            present_days = late_days = half_days = absent_days = leave_days = 0

            shift = user.shift
            shift_start = shift.shift_start_time if shift else None
            shift_end = shift.shift_end_time if shift else None

            for rec in filtered_attendance:
                dynamic_status = 'Absent'  # default

                # Respect pre-set statuses first
                if rec.status:
                    if rec.status.lower() == 'late':
                        dynamic_status = 'Late'
                    elif rec.status.lower() == 'absent':
                        dynamic_status = 'Absent'
                    elif rec.status.lower() == 'on leave':
                        dynamic_status = 'On Leave'

                if rec.time_in:
                    time_in_datetime = datetime.combine(rec.date, rec.time_in)
                    if shift_start:
                        shift_start_datetime = datetime.combine(rec.date, shift_start)
                        late_threshold = shift_start_datetime + timedelta(hours=1)
                        if time_in_datetime <= late_threshold:
                            dynamic_status = 'Present'
                        else:
                            dynamic_status = 'Late'

                if rec.time_out and rec.time_in and shift_end:
                    time_out_datetime = datetime.combine(rec.date, rec.time_out)
                    shift_end_datetime = datetime.combine(rec.date, shift_end)
                    if dynamic_status == 'Present' and time_out_datetime < shift_end_datetime:
                        dynamic_status = 'Half Day'

                # Increment counters
                if dynamic_status.lower() == 'present':
                    present_days += 1
                elif dynamic_status.lower() == 'late':
                    late_days += 1
                elif dynamic_status.lower() == 'half day':
                    half_days += 1
                elif dynamic_status.lower() == 'absent':
                    absent_days += 1
                elif dynamic_status.lower() == 'on leave':
                    leave_days += 1

            total_present += present_days
            total_absent += absent_days
            total_late += late_days
            total_half += half_days
            total_on_leave += leave_days

            # Overtime calculation
            overtime_seconds = 0
            for rec in attendance_qs:
                if rec.overtime:
                    h, m, s = map(int, str(rec.overtime).split(":"))
                    overtime_seconds += h*3600 + m*60 + s
            overtime_hours = round(overtime_seconds / 3600, 1)

            attendance_rate = ((present_days + late_days + 0.5 * half_days) / last_completed_day * 100) if last_completed_day > 0 else 0

            result.append({
                "employeeId": user.user_id,
                "name": user.user_name,
                "designation": user.designation,
                "department": user.department.department_name if user.department else "N/A",
                "totalDays": days_in_month,
                "presentDays": present_days,
                "absentDays": absent_days,
                "lateDays": late_days,
                "halfDays": half_days,
                "leaveDays": leave_days,
                "overtimeHours": overtime_hours,
                "attendanceRate": round(attendance_rate, 1),
                "avatar": "".join([p[0] for p in user.user_name.split()][:2]).upper()
            })

        total_employees = len(result)
        total_days_recorded_for_all = total_employees * last_completed_day

        overall_attendance_rate = ((total_present + total_late + 0.5 * total_half) / total_days_recorded_for_all * 100) if total_days_recorded_for_all > 0 else 0
        overall_attendance_rate = round(overall_attendance_rate, 1)

        return Response({
            "data": result,
            "totals": {
                "totalEmployees": total_employees,
                "totalPresent": total_present,
                "totalAbsent": total_absent,
                "totalLate": total_late,
                "totalHalfDays": total_half,
                "totalOnLeave": total_on_leave,
                "overallAttendanceRate": overall_attendance_rate
            }
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
    
@api_view(['GET'])
def all_user_department_summary(request):
    try:
        month = request.query_params.get('month', '').strip()
        if not month:
            return Response({"error": "Please provide month in YYYY-MM format"}, status=400)

        try:
            parts = month.split("-")
            if len(parts) != 2:
                raise ValueError("Invalid month format")
            year_str, month_str = parts
            year = int(year_str)
            month_num = int(month_str.lstrip("0") or "0")
            if not (1 <= month_num <= 12):
                return Response({"error": "Month must be between 01 and 12"}, status=400)
        except Exception:
            return Response({"error": "Invalid month format. Use YYYY-MM"}, status=400)

        start_date = datetime(year, month_num, 1).date()
        days_in_month = calendar.monthrange(year, month_num)[1]
        end_date = datetime(year, month_num, days_in_month).date()

        today = datetime.now().date()
        is_current_month = today.year == year and today.month == month_num
        last_completed_day = min(today.day, days_in_month) if is_current_month else days_in_month

        departments = Department.objects.all()
        summary = []

        total_present = total_absent = total_late = total_half = total_on_leave = total_employees = 0

        for dept in departments:
            employees = User.objects.filter(department=dept)
            if not employees.exists():
                continue

            dept_present = dept_absent = dept_late = dept_half = dept_leave = dept_count = 0

            for emp in employees:
                attendance_qs = Attendance.objects.filter(user=emp, date__range=[start_date, end_date])
                if not attendance_qs.exists():
                    continue

                filtered_attendance = [rec for rec in attendance_qs if rec.date.day <= last_completed_day]

                present_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "present")
                late_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "late")
                half_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "half day")
                absent_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "absent")
                leave_days = sum(1 for rec in filtered_attendance if rec.status.lower() == "on leave")

                dept_present += present_days
                dept_absent += absent_days
                dept_late += late_days
                dept_half += half_days
                dept_leave += leave_days
                dept_count += 1

            if dept_count == 0:
                continue

            total_present += dept_present
            total_absent += dept_absent
            total_late += dept_late
            total_half += dept_half
            total_on_leave += dept_leave
            total_employees += dept_count

            total_days_recorded = last_completed_day * dept_count
            avg_attendance = ((dept_present + dept_late + 0.5 * dept_half) / total_days_recorded * 100) if total_days_recorded > 0 else 0


            summary.append({
                "department": dept.department_name,
                "employees": dept_count,
                "avgAttendance": round(avg_attendance, 1),
                "totalPresent": dept_present,
                "totalAbsent": dept_absent,
                "totalLate": dept_late,
                "totalHalfDays": dept_half,
                "totalOnLeave": dept_leave
            })

        return Response({
            "data": summary,
            "totals": {
                "totalEmployees": total_employees,
                "totalPresent": total_present,
                "totalAbsent": total_absent,
                "totalLate": total_late,
                "totalHalfDays": total_half,
                "totalOnLeave": total_on_leave
            }
        }, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
