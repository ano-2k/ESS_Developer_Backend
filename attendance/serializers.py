from rest_framework import serializers

from authentication.serializers import ArSerializer, EmployeeSerializer, LocationSerializer, ManagerSerializer, ShiftSerializer, SupervisorSerializer ,HrSerializer,UserSerializer
from .models import Attendance, ResetRequest, PermissionHour


        



class ResetRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    manager = ManagerSerializer(read_only=True)
    supervisor = SupervisorSerializer(read_only=True)
    hr = HrSerializer(read_only=True)
    ar = ArSerializer(read_only=True)
    class Meta:
        model = ResetRequest
        fields = '__all__'


class PermissionHourSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    reviewed_by = ManagerSerializer(read_only=True)
    total_hours = serializers.ReadOnlyField()  # Include the `total_hours` property

    class Meta:
        model = PermissionHour
        fields = '__all__'
        
from rest_framework import serializers
from .models import Attendance, ResetRequest



class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = '__all__'


# serializers.py
from rest_framework import serializers
from .models import Shift, Location, Manager, Attendance, Supervisor

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['shift_number',  'shift_start_time', 'shift_end_time']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['location_id', 'location_name']
        extra_kwargs = {'location_id': {'required': True}}


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['manager_id', 'manager_name', 'shift']

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['supervisor_id', 'supervisor_name', 'shift']

class AttendanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    manager = ManagerSerializer(read_only=True)
    supervisor = SupervisorSerializer(read_only=True)# Explicitly declared
    hr = HrSerializer(read_only=True)
    ar = ArSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Attendance
        fields = [
            'id', 
            'user',  # Include the 'employee' field here
            # 'employee_id', 
            # 'employee_name', 
            'manager', 
            'supervisor', 
            'hr',
            'ar',
            'date', 
            'shift', 
            'location', 
            'notes', 
            'time_in', 
            'time_out', 
            'in_status', 
            'out_status', 
            'overtime', 
            'total_working_hours', 
            'total_present_days'
        ]

# attendance/serializers.py

from rest_framework import serializers
from .models import Attendance



# attendance/serializers.py

from rest_framework import serializers

class ApproveResetRequestResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    employee_id = serializers.IntegerField()
    date = serializers.DateField()
    redirect_url = serializers.URLField()

from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    request_type = serializers.CharField(required=True)
    request_description = serializers.CharField(required=False)

    class Meta:
        model = ResetRequest
        fields = ['request_type', 'request_description']


from rest_framework import serializers
from .models import ResetRequest, Attendance

class ManagerAttendanceSerializer(serializers.ModelSerializer):
    shift = serializers.CharField(source='shift.shift_number')

    class Meta:
        model = Attendance
        fields = [
            'shift',
            'time_in',
            'time_out',
            'in_status',
            'out_status',
            'notes',
        ]


class ResetRequestSerializer(serializers.ModelSerializer):
    manager_id = serializers.CharField(source='manager.manager_id')
    username = serializers.CharField(source='manager.username')
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = ResetRequest
        fields = [
            'id',
            'manager_id',
            'username',
            'request_type',
            'request_description',
            'date',
            'attendance',
            'status',
        ]

    def get_attendance(self, obj):
        try:
            attendance = Attendance.objects.get(manager=obj.manager, date=obj.date)
            return ManagerAttendanceSerializer(attendance).data
        except Attendance.DoesNotExist:
            return None


# serializers.py
from rest_framework import serializers
from .models import ResetRequest, Attendance, Employee



class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['employee_id', 'employee_name']

class ResetRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()
    attendance = AttendanceSerializer(source='employee.attendance_set.first', read_only=True)  # Adjust this to fit your model relations

    class Meta:
        model = ResetRequest
        fields = ['id', 'employee', 'request_type', 'request_description', 'date', 'status', 'attendance']

        # serializers.py
from rest_framework import serializers
from .models import Attendance

class AttendanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['date', 'shift', 'location', 'time_in', 'time_out', 'status']  # Include all relevant fields



# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status', 'employee', 'request_type', 'request_description', 'date']

# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status', 'employee', 'request_type', 'request_description', 'date']

# serializers.py
from rest_framework import serializers
from .models import Attendance

class AttendanceCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'time_in', 'time_out', 'out_status', 'overtime', 'total_working_hours']


# serializers.py
from rest_framework import serializers
from .models import ResetRequest, Attendance



class ResetRequestSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id')
    username = serializers.CharField(source='employee.username')
    shift = serializers.CharField(source='attendance.shift.shift_number')
    time_in = serializers.TimeField(source='attendance.time_in')
    time_out = serializers.TimeField(source='attendance.time_out')
    in_status = serializers.CharField(source='attendance.in_status')
    out_status = serializers.CharField(source='attendance.out_status')
    notes = serializers.CharField(source='attendance.notes')
    
    class Meta:
        model = ResetRequest
        fields = ['id', 'employee_id', 'username', 'request_type', 'request_description', 'date', 'shift', 'time_in', 'time_out', 'in_status', 'out_status', 'notes', 'status']

# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'employee', 'request_type', 'request_description', 'date', 'status']

# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'employee', 'request_type', 'request_description', 'date', 'status']

# serializers.py
from rest_framework import serializers
from .models import Attendance



# serializers.py
from rest_framework import serializers
from .models import ResetRequest, Attendance

class ResetRequestSerializer(serializers.ModelSerializer):
    manager_username = serializers.CharField(source='manager.username')
    manager_id = serializers.IntegerField(source='manager.manager_id')
    shift_number = serializers.IntegerField(source='attendance.shift.shift_number')
    time_in = serializers.TimeField(source='attendance.time_in')
    time_out = serializers.TimeField(source='attendance.time_out')
    in_status = serializers.CharField(source='attendance.in_status')
    out_status = serializers.CharField(source='attendance.out_status')
    notes = serializers.CharField(source='attendance.notes')

    class Meta:
        model = ResetRequest
        fields = ['id', 'manager_id', 'manager_username', 'request_type', 'request_description', 'date', 
                  'shift_number', 'time_in', 'time_out', 'in_status', 'out_status', 'notes', 'status']


# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status', 'manager', 'employee', 'date', 'request_type', 'request_description']


from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status']  # Only including fields that need to be updated

    def update(self, instance, validated_data):
        # Update the status to "Rejected" when this API is called
        instance.status = 'Rejected'
        instance.save()
        return instance

from rest_framework import serializers
from .models import Attendance


####
from rest_framework import serializers

class WeeklyAttendanceSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    month = serializers.CharField()
    week_offset = serializers.IntegerField()

from rest_framework import serializers

class ManagerWeeklyAttendanceSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    month = serializers.CharField()
    week_offset = serializers.IntegerField()

# serializers.py
from rest_framework import serializers
from .models import Attendance
from leaves.models import LeaveRequest



class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'status', 'employee']

# serializers.py
# serializers.py
from rest_framework import serializers



class MonthlyAttendanceChartSerializer(serializers.Serializer):
    month = serializers.CharField(max_length=20)
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    week_avg_data = serializers.ListField(child=serializers.DictField())
    month_offset = serializers.IntegerField()


# serializers.py

from rest_framework import serializers

class EmployeeMonthlyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    employee_id = serializers.CharField()

# serializers.py

from rest_framework import serializers

class SupervisorAttendanceSerializer(serializers.Serializer):
    locations = serializers.ListField(child=serializers.CharField())
    shift = serializers.CharField()
    show_checkout = serializers.BooleanField()
    thank_you_message = serializers.CharField()

# serializers.py

from rest_framework import serializers

class SupervisorAttendanceStatusSerializer(serializers.Serializer):
    message = serializers.CharField()
    status = serializers.CharField()
    overtime = serializers.CharField(allow_null=True)
    total_working_hours = serializers.CharField(allow_null=True)

# serializers.py
from rest_framework import serializers
from .models import Attendance



# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'supervisor', 'date', 'request_type', 'request_description', 'status', 'created_at']

# serializers.py
from rest_framework import serializers
from .models import ResetRequest, Attendance



class ResetRequestSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.CharField(source='supervisor.supervisor_id')
    username = serializers.CharField(source='supervisor.username')
    attendance = AttendanceSerializer(source='attendance', read_only=True)

    class Meta:
        model = ResetRequest
        fields = [
            'id', 'supervisor_id', 'username', 'request_type', 
            'request_description', 'date', 'status', 'attendance'
        ]

# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'supervisor', 'date', 'status', 'request_type', 'request_description']

# serializers.py
from rest_framework import serializers
from .models import ResetRequest

class ResetRequestRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'supervisor', 'date', 'status', 'request_type', 'request_description']

# serializers.py
from rest_framework import serializers
from .models import Attendance
from datetime import datetime, timedelta

class SupervisorCheckoutTimeSerializer(serializers.ModelSerializer):
    checkout_time = serializers.CharField(required=False)
    clear_checkout = serializers.BooleanField(required=False)

    class Meta:
        model = Attendance
        fields = ['checkout_time', 'clear_checkout']

    def validate_checkout_time(self, value):
        if value:
            try:
                # Validate the time format (HH:MM:SS)
                datetime.strptime(value, '%H:%M:%S')
            except ValueError:
                raise serializers.ValidationError("Invalid time format. Please use HH:MM:SS.")
        return value

# serializers.py
from rest_framework import serializers
from .models import ResetRequest, Attendance

class ResetRequestSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.IntegerField(source='supervisor.supervisor_id')
    username = serializers.CharField(source='supervisor.username')
    shift_number = serializers.IntegerField(source='attendance.shift.shift_number')
    time_in = serializers.TimeField(source='attendance.time_in')
    time_out = serializers.TimeField(source='attendance.time_out')
    in_status = serializers.CharField(source='attendance.in_status')
    out_status = serializers.CharField(source='attendance.out_status')
    notes = serializers.CharField(source='attendance.notes')

    class Meta:
        model = ResetRequest
        fields = [
            'id', 
            'supervisor_id', 
            'username', 
            'request_type', 
            'request_description', 
            'date', 
            'shift_number', 
            'time_in', 
            'time_out', 
            'in_status', 
            'out_status', 
            'notes', 
            'status'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            supervisor_attendance = Attendance.objects.get(supervisor=instance.supervisor, date=instance.date)
            representation.update({
                'shift_number': supervisor_attendance.shift.shift_number,
                'time_in': supervisor_attendance.time_in,
                'time_out': supervisor_attendance.time_out,
                'in_status': supervisor_attendance.in_status,
                'out_status': supervisor_attendance.out_status,
                'notes': supervisor_attendance.notes
            })
        except Attendance.DoesNotExist:
            pass  # Handle cases where attendance does not exist (if needed)
        return representation
    
    # serializers.py

from rest_framework import serializers
from .models import ResetRequest

class ResetRequestApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status']
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

# serializers.py

from rest_framework import serializers
from .models import ResetRequest

class ResetRequestRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['id', 'status']
    
    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

# serializers.py

from rest_framework import serializers
from .models import Attendance

class AttendanceCheckoutTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'time_out', 'out_status', 'total_working_hours', 'overtime']

    def update(self, instance, validated_data):
        instance.time_out = validated_data.get('time_out', instance.time_out)
        instance.out_status = validated_data.get('out_status', instance.out_status)
        instance.total_working_hours = validated_data.get('total_working_hours', instance.total_working_hours)
        instance.overtime = validated_data.get('overtime', instance.overtime)
        instance.save()
        return instance

# serializers.py

from rest_framework import serializers
from .models import Attendance
from leaves.models import SupervisorLeaveRequest

class SupervisorWeeklyAttendanceChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())  # Days with date
    data = serializers.ListField(child=serializers.FloatField())  # Total working hours per day
    leave_data = serializers.ListField(child=serializers.FloatField())  # Leave data for each day
    total_hours = serializers.FloatField()  # Total working hours for the week
    total_overtime = serializers.FloatField()  # Total overtime for the week
    month = serializers.CharField()  # Current month
    week_offset = serializers.IntegerField()  # Week offset for navigation

    def create(self, validated_data):
        # Implement creation logic if needed (not required for this specific case)
        pass

    def update(self, instance, validated_data):
        # Implement update logic if needed (not required for this specific case)
        pass

# serializers.py
from rest_framework import serializers

class SupervisorMonthlyAttendanceChartSerializer(serializers.Serializer):
    month = serializers.CharField(max_length=255)
    week_avg_data = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField()
        )
    )
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    month_offset = serializers.IntegerField()

from rest_framework import serializers
from attendance.models import Attendance, Manager

class ManagerAttendanceSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.name', read_only=True)  # Adjust 'name' based on your Manager model fields

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time_in', 'time_out', 'manager', 'manager_name', 'shift', 'location']

from rest_framework import serializers
from attendance.models import Attendance, Supervisor  # Assuming you have a Supervisor model

class SupervisorAttendanceSerializer(serializers.ModelSerializer):
    supervisor_name = serializers.CharField(source='supervisor.name', read_only=True)  # Adjust 'name' based on your Supervisor model fields

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time_in', 'time_out', 'supervisor', 'supervisor_name', 'shift', 'location']

from rest_framework import serializers
from attendance.models import Attendance, Employee  # Assuming you have an Employee model

class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)  # Adjust 'name' based on your Employee model fields

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time_in', 'time_out', 'employee', 'employee_name', 'shift', 'location']

from rest_framework import serializers

class AdminManagerWeeklyChartSerializer(serializers.Serializer):
    manager_id = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    week_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()

from rest_framework import serializers
from leaves.models import SupervisorLeaveRequest



class SupervisorLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorLeaveRequest
        fields = ['start_date', 'end_date', 'status']

from rest_framework import serializers

class ManagerMonthlyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    manager_id = serializers.CharField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())

# serializers.py
from rest_framework import serializers

class SupervisorMonthlyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    supervisor_id = serializers.CharField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())

    # serializers.py
from rest_framework import serializers

class ManagerAttendanceSerializer(serializers.Serializer):
    manager_id = serializers.CharField(max_length=100)
    month = serializers.CharField(max_length=50)
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    weekly_hours = serializers.ListField(child=serializers.FloatField())
    weekly_averages = serializers.ListField(child=serializers.FloatField())
    week_labels = serializers.ListField(child=serializers.CharField(max_length=10))
    average_hours_per_week = serializers.FloatField()

# serializers.py
from rest_framework import serializers

class WeeklyAttendanceSerializer(serializers.Serializer):
    day_label = serializers.CharField()  # Day of the week (e.g., "Mon Sep 11")
    hours_worked = serializers.FloatField()  # Total hours worked on that day
    overtime_hours = serializers.FloatField()  # Overtime hours for that day
    is_leave = serializers.BooleanField()  # Whether the day is a leave day or not

class WeeklyChartDataSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    weekly_data = WeeklyAttendanceSerializer(many=True)  # List of daily attendance data
    month = serializers.CharField()
    week_offset = serializers.IntegerField()

from rest_framework import serializers

class EmployeeMonthlyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    employee_id = serializers.CharField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())

from rest_framework import serializers
from .models import ResetRequest

class ResetRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetRequest
        fields = ['employee', 'date', 'request_type', 'request_description', 'status', 'created_at']

from rest_framework import serializers
from .models import Attendance



from rest_framework import serializers
from .models import Attendance



from rest_framework import serializers
from .models import Attendance



from rest_framework import serializers

class ManagerWeeklyChartSerializer(serializers.Serializer):
    manager_id = serializers.CharField()
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    week_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()

# serializers.py

from rest_framework import serializers

class SupervisorWeeklyChartSerializer(serializers.Serializer):
    supervisor_id = serializers.CharField(max_length=100)
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField(max_length=20)
    week_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()

from rest_framework import serializers

class ManagerMonthlyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    manager_id = serializers.CharField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())

from rest_framework import serializers

class SupervisorMonthlyChartSerializer(serializers.Serializer):
    week_labels = serializers.ListField(child=serializers.CharField())
    work_data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    month_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    supervisor_id = serializers.CharField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())

# serializers.py

from rest_framework import serializers
from .models import Attendance
from django.utils.timezone import now
from leaves.models import LeaveRequest



class LeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'status', 'employee_id']

class EmployeeWeeklyChartSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    leave_data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    week_offset = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    employee_id = serializers.CharField()

from rest_framework import serializers

class EmployeeMonthlyChartSerializer(serializers.Serializer):
    employee_id = serializers.CharField(required=True)
    month_offset = serializers.IntegerField(default=0)
    total_hours = serializers.FloatField()
    total_overtime = serializers.FloatField()
    average_hours_per_week = serializers.FloatField()
    weekly_averages = serializers.ListField(child=serializers.FloatField())
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())
    month = serializers.CharField()
    
from rest_framework import serializers
from .models import (
    AttendanceOverview,
    Schedule,
    DepartmentActiveJob,
    CalendarEvent,
    Offer,
    Employee_attendance,
    Shift_attendance,
    Holiday,
    ProFeedback,
)

class AttendanceOverviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceOverview
        fields = [
            'id', 
            'employee', 
            'role', 
            'department', 
            'date', 
            'status', 
            'check_in', 
            'check_out', 
            'work_hours'
        ]


class ScheduleSerializer(serializers.ModelSerializer):
    interviewer_name = serializers.CharField(source='interviewer.manager_name', read_only=True)
    class Meta:
        model = Schedule
        fields = ['id', 'participant', 'interviewer', 'interviewer_name', 'date', 'time', 'duration', 'role', 'email']
          # Ensure total_time is calculated automatically



class DepartmentActiveJobSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = DepartmentActiveJob
        fields = [
            'id', 
            'title',
            'role', 
            'experience_level', 
            'location', 
            'job_type', 
            'openings'
        ]


class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        fields = [
            'id', 
            'title', 
            'description', 
            'date', 
            'start_time', 
            'end_time'
        ]












class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'id', 
            'name', 
            'position', 
            'status', 
            'date'
        ]


class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_attendance
        fields = [
            'id', 
            'username', 
            'position'
        ]


# class ShiftAttendanceSerializer(serializers.ModelSerializer):
#     duration = serializers.SerializerMethodField()

#     class Meta:
#         model = Shift_attendance
#         fields = [
#             'id', 
#             'employee', 
#             'date', 
#             'start_time', 
#             'end_time', 
#             'break_time', 
#             'shift_number', 
#             'duration'
#         ]

#     def get_duration(self, obj):
#         # Calculate the duration dynamically if start_time and end_time are available
#         if obj.start_time and obj.end_time:
#             total_time = datetime.combine(now().date(), obj.end_time) - datetime.combine(now().date(), obj.start_time)
#             return total_time - timedelta(minutes=obj.break_time)
#         return None

from rest_framework import serializers
from .models import Shift_attendance

class ShiftAttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.employee_name', read_only=True)
    class Meta:
        model = Shift_attendance
        fields = ['id', 'employee', 'employee_name', 'start_time', 'end_time', 'total_time', 'working_day']
        read_only_fields = ['total_time']  # Ensure total_time is calculated automatically

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = [
            'id', 
            'date', 
            'description'
        ]

class ProFeedbackSerializer(serializers.ModelSerializer):
    from_manager = ManagerSerializer(read_only=True)
    to_employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = ProFeedback
        fields = ['id', 'from_manager', 'to_employee', 'feedback_date', 'comments']

# class ShiftAttendanceSerializer(serializers.ModelSerializer):
#     duration = serializers.SerializerMethodField()

#     class Meta:
#         model = Shift_attendance
#         fields = [
#             'id', 
#             'employee', 
#             'date', 
#             'start_time', 
#             'end_time', 
#             'break_time', 
#             'shift_number', 
#             'duration'
#         ]

#     def get_duration(self, obj):
#         # Calculate the duration dynamically if start_time and end_time are available
#         if obj.start_time and obj.end_time:
#             total_time = datetime.combine(now().date(), obj.end_time) - datetime.combine(now().date(), obj.start_time)
#             return total_time - timedelta(minutes=obj.break_time)
#         return None


from rest_framework import serializers
from .models import OnboardingTask

class OnboardingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingTask
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['user_name', 'role', 'date', 'time_in', 'location_name']

    def get_user_name(self, obj):
        """Fetch user name from Employee, Manager, Supervisor, or HR"""
        user = obj.employee or obj.manager or obj.supervisor or obj.hr
        return user.username if user else "Unknown"

    def get_role(self, obj):
        """Return 'Employee' as role for everyone"""
        return "Employee"

    def get_location_name(self, obj):
        """Get location name if available"""
        return obj.location.location_name if obj.location else "Unknown"

    

   




        
