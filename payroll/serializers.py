from rest_framework import serializers
from .models import ArPayrollManagement, ArPayrollNotification, ArSalary, PayrollManagement, PayrollNotification, ManagerPayrollNotification, SupervisorPayrollManagement, SupervisorPayrollNotification, SupervisorSalary,UserSalary,UserPayrollManagement,UserPayrollNotification
from .models import Salary, BonusType,HrSalary,HrPayrollManagement,HrPayrollNotification

class PayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollManagement
        fields = [
            'id', 'user', 'user_id', 'month', 'email', 
            'base_salary', 'net_salary', 'total_working_hours', 
            'overtime_hours', 'overtime_pay', 'pdf_path'
        ]
        
class SupervisorPayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorPayrollManagement
        fields = [
            'id', 'user', 'user_id', 'month', 'email', 
            'base_salary', 'net_salary', 'total_working_hours', 
            'overtime_hours', 'overtime_pay', 'pdf_path'
        ]        


class PayrollNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollNotification
        fields = [
            'id', 'user', 'user_id', 'date', 'time', 'message'
        ]


class ManagerPayrollNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPayrollNotification
        fields = [
            'id', 'user', 'user_id', 'date', 'time', 'message'
        ]


class SupervisorPayrollNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorPayrollNotification
        fields = [
            'id', 'user', 'user_id', 'date', 'time', 'message'
        ]




class SalarySerializer(serializers.ModelSerializer):
    # Additional read-only fields if required
    total_salary = serializers.CharField(read_only=True)
    monthly_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Salary
        fields = [
            'id', 'user_id', 'annual_salary', 'bonus', 
            'total_salary', 'monthly_salary', 
            'effective_date', 'updated_date'
        ]
        
class ManagerSalarySerializer(serializers.ModelSerializer):
    # Additional read-only fields if required
    total_salary = serializers.CharField(read_only=True)
    monthly_salary = serializers.CharField(read_only=True)

    class Meta:
        model = Salary
        fields = [
            'id', 'user_id', 'annual_salary', 'bonus', 
            'total_salary', 'monthly_salary', 
            'effective_date', 'updated_date'
        ]        


class SupervisorSalarySerializer(serializers.ModelSerializer):
    # Additional read-only fields if required
    total_salary = serializers.CharField(read_only=True)
    monthly_salary = serializers.CharField(read_only=True)

    class Meta:
        model = SupervisorSalary
        fields = [
            'id', 'user_id', 'annual_salary', 'bonus', 
            'total_salary', 'monthly_salary', 
            'effective_date', 'updated_date'
        ]        


class BonusTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusType
        fields = [
            'id', 'user_id', 'bonus_type', 'amount', 
            'due_date', 'paid_status', 'total_paid'
        ]
        
class HrSalarySerializer(serializers.ModelSerializer):
    # Additional read-only fields if required
    total_salary = serializers.CharField(read_only=True)
    monthly_salary = serializers.CharField(read_only=True)

    class Meta:
        model = HrSalary
        fields = [
            'id', 'user_id', 'annual_salary', 'bonus', 
            'total_salary', 'monthly_salary', 
            'effective_date', 'updated_date'
        ]         
        
class HrPayrollNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrPayrollNotification
        fields = [
            'id', 'user', 'user_id', 'date', 'time', 'message'
        ]        
        
class HrPayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HrPayrollManagement
        fields = [
            'id', 'user', 'user_id', 'month', 'email', 
            'base_salary', 'net_salary', 'total_working_hours', 
            'overtime_hours', 'overtime_pay', 'pdf_path'
        ]                
        
class ArSalarySerializer(serializers.ModelSerializer):
    # Additional read-only fields if required
    total_salary = serializers.CharField(read_only=True)
    monthly_salary = serializers.CharField(read_only=True)

    class Meta:
        model = ArSalary
        fields = [
            'id', 'user_id', 'annual_salary', 'bonus', 
            'total_salary', 'monthly_salary', 
            'effective_date', 'updated_date'
        ]         
        
class ArPayrollNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArPayrollNotification
        fields = [
            'id', 'user', 'user_id', 'date', 'time', 'message'
        ]        
        
class ArPayrollManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArPayrollManagement
        fields = [
            'id', 'user', 'user_id', 'month', 'email', 
            'base_salary', 'net_salary', 'total_working_hours', 
            'overtime_hours', 'overtime_pay', 'pdf_path'
        ]                        
        
        
############################# NEW CHANGES AFTER USER MODEL AND CONCEPT IMPEMENTED ####################################   

class UserSalarySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.user_name", read_only=True)
    designation = serializers.CharField(source="user.designation", read_only=True)

    class Meta:
        model = UserSalary
        fields = [
            "id", "user", "user_name", "designation",
            "annual_salary", "bonus", "total_salary", "monthly_salary",
            "effective_date", "updated_date"
        ]
        
class UserPayrollManagementSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.user_name", read_only=True)
    designation = serializers.CharField(source="user.designation", read_only=True)

    class Meta:
        model = UserPayrollManagement
        fields = [
            'id', 'user', 'user_id', 'user_name', 'designation',
            'month', 'email', 'base_salary', 'net_salary',
            'total_working_hours', 'overtime_hours',
            'overtime_pay', 'pdf_path'
        ]
        


class UserPayrollNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.user_name", read_only=True)
    designation = serializers.CharField(source="user.designation", read_only=True)

    class Meta:
        model = UserPayrollNotification
        fields = [
            'id', 'user', 'user_name', 'designation',
            'date', 'time', 'message'
        ]