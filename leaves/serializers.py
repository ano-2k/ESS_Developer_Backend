from rest_framework import serializers
from .models import (
    ArApplyNotification, ArLeaveBalance, ArLeaveRequest, ArNotification, LeaveRequest, Notification, ApplyNotification, LeaveBalance, HrApplyNotification, HrLeaveBalance, HrLeaveRequest,HrNotification,
    ManagerLeaveRequest, ManagerNotification, ManagerApplyNotification, ManagerLeaveBalance,
    SupervisorLeaveRequest, SupervisorNotification, SupervisorApplyNotification, SupervisorLeaveBalance,LateloginReason,HrLateLoginReason,ManagerLateLoginReason,EmployeeLateLoginReason
)
from authentication.models import User
from authentication.serializers import UserSerializer,UserDashboardSerializer


class LeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = LeaveRequest
        fields = '__all__'
        
class SupervisorLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = SupervisorLeaveRequest
        fields = '__all__'        

class HrLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = HrLeaveRequest
        fields = '__all__'      
        
        
class HrLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrLeaveBalance
        fields = '__all__'
        
class HrApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrApplyNotification
        fields = '__all__'
        
class HrNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrNotification
        fields = '__all__'                          

class ArLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = ArLeaveRequest
        fields = '__all__'      
        
        
class ArLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArLeaveBalance
        fields = '__all__'
        
class ArApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArApplyNotification
        fields = '__all__'
        
class ArNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArNotification
        fields = '__all__'                          
                
        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class ApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplyNotification
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'

class ManagerLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = ManagerLeaveRequest
        fields = '__all__'

class ManagerNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerNotification
        fields = '__all__'

class ManagerApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerApplyNotification
        fields = '__all__'

class ManagerLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerLeaveBalance
        fields = '__all__'

class SupervisorLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = SupervisorLeaveRequest
        fields = ['id', 'start_date', 'end_date', 'leave_type', 'reason', 'status', 'user', 'user_id', 'supervisor', 'email', 'supervisor_notification_sent', 'is_auto_leave', 'total_days']    #added july1
		

class SupervisorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorNotification
        fields = '__all__'

class SupervisorApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorApplyNotification
        fields = '__all__'

class SupervisorLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorLeaveBalance
        fields = '__all__'

		 
class LateoginReasonSerializer(serializers.ModelSerializer):
    supervisor_id = serializers.CharField(source='supervisor.supervisor_id', read_only=True)
    supervisor_name = serializers.CharField(read_only=True)  # Use the model's supervisor_name field
    leave_request = SupervisorLeaveRequestSerializer(read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LateloginReason
        fields = ['id', 'supervisor', 'supervisor_id', 'supervisor_name', 'leave_request', 'date', 'reason', 'status', 'created_at']


class SubmitLateLoginReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    leave_id = serializers.IntegerField()



#################################july7####################################

class HrLateLoginReasonSerializer(serializers.ModelSerializer):
    hr_id = serializers.CharField(source='hr.hr_id', read_only=True)
    hr_name = serializers.CharField(read_only=True)  # Use the model's hr_name field
    leave_request = HrLeaveRequestSerializer(read_only=True)  # Assuming HrLateRequest uses HrLeaveRequestSerializer
    date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = HrLateLoginReason
        fields = ['id', 'hr', 'hr_id', 'hr_name', 'leave_request', 'date', 'reason', 'status', 'created_at']

class SubmitHrLateLoginReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    leave_id = serializers.IntegerField()



class ManagerLateLoginReasonSerializer(serializers.ModelSerializer):
    manager_id = serializers.CharField(source='manager.manager_id', read_only=True)
    manager_name = serializers.CharField(read_only=True)  # Use the model's manager_name field
    leave_request = ManagerLeaveRequestSerializer(read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ManagerLateLoginReason
        fields = ['id', 'manager', 'manager_id', 'manager_name', 'leave_request', 'date', 'reason', 'status', 'created_at']

class SubmitManagerLateLoginReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    leave_id = serializers.IntegerField()


class SubmitemployeeLateLoginReasonSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
    leave_id = serializers.IntegerField()

class EmployeeLateLoginReasonSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.CharField(read_only=True)  # Use the model's employee_name field
    leave_request = LeaveRequestSerializer(read_only=True)
    date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EmployeeLateLoginReason
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'leave_request', 'date', 'reason', 'status', 'created_at']




############################################## New Changes #################################################


from .models import UserLeaveRequest, UserLateLoginReason,UserApplyNotification,UserLeaveBalance,UserNotification


class UserLeaveRequestSerializer(serializers.ModelSerializer):
    total_days = serializers.ReadOnlyField()

    class Meta:
        model = UserLeaveRequest
        fields = '__all__'


class UserLateLoginReasonSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    leave_request = UserLeaveRequestSerializer(read_only=True)  # Nested info
    date = serializers.DateField(format="%Y-%m-%d")
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = UserLateLoginReason
        fields = [
            'id',
            'user',
            'user_id',
            'user_name',
            'leave_request',
            'date',
            'reason',
            'status',
            'created_at'
        ]
        

class UserLeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLeaveBalance
        fields = '__all__'


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotification
        fields = '__all__'


class UserApplyNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserApplyNotification
        fields = '__all__'