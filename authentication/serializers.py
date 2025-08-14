from rest_framework import serializers

from attendance.models import Attendance
from documents.models import Document
from kpi.models import PerformanceReview
from projectmanagement.models import employee_task
from authentication.models import Manager, Employee, Department, Shift, Location, Skill, Supervisor
import bcrypt
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from authentication.models import Admin, ManagingDirector, Manager, Employee, Supervisor,Hr,Ar
from django.contrib.auth.hashers import make_password

from .models import SuperAdmin
class SuperAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = SuperAdmin
        fields = ['id', 'username', 'user_id', 'email', 'password','features']

    def validate_username(self, value):
        if self.instance:
            if SuperAdmin.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A super admin with this username already exists.")
        else:
            if SuperAdmin.objects.filter(username=value).exists():
                raise serializers.ValidationError("A super admin with this username already exists.")
        return value

    def validate_email(self, value):
        if self.instance:
            if SuperAdmin.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A super admin with this email already exists.")
        else:
            if SuperAdmin.objects.filter(email=value).exists():
                raise serializers.ValidationError("A super admin with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        self.validate_password(raw_password)
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password
        return SuperAdmin.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    

class AdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Admin
        fields = ['id', 'user_id', 'username', 'email', 'password', 'features', 'reset_token', 'token_expiration']
        read_only_fields = ['user_id']

    def validate_username(self, value):
        if self.instance:
            if Admin.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("An admin with this username already exists.")
        else:
            if Admin.objects.filter(username=value).exists():
                raise serializers.ValidationError("An admin with this username already exists.")
        return value

    def validate_email(self, value):
        if self.instance:
            if Admin.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("An admin with this email already exists.")
        else:
            if Admin.objects.filter(email=value).exists():
                raise serializers.ValidationError("An admin with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        try:
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e
        
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        return super().update(instance, validated_data)

class ArSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = Ar
        fields = [
            'id', 'ar_id', 'ar_name', 'department_name', 'department',
            'email', 'gender', 'ar_image', 'shift', 'dob', 'hired_date',
            'username', 'password', 'role','location'
        ]
        read_only_fields = ['ar_id']

    def validate_username(self, value):
        """
        Ensure username is unique across ars.
        """
        if self.instance:
            if Ar.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A ar with this username already exists.")
        else:
            if Ar.objects.filter(username=value).exists():
                raise serializers.ValidationError("A ar with this username already exists.")
        return value

    def validate_email(self, value):
        """
        Ensure email is unique across ars.
        """
        if self.instance:
            if Ar.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A ar with this email already exists.")
        else:
            if Ar.objects.filter(email=value).exists():
                raise serializers.ValidationError("A ar with this email already exists.")
        return value

    def validate_password(self, value):
        """
        Validate password using Django's built-in validation.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        """
        Overridden create method to hash the password before saving the ar.
        """
        raw_password = validated_data.pop('password')  # Remove password from validated data
        try:
            # Ensure password meets complexity requirements
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e  # Propagate the error if validation fails
        
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password  # Store the hashed password
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        If the password is being updated, hash the new password before saving.
        """
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        
        return super().update(instance, validated_data) 

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = [
            'id', 'manager_id', 'manager_name', 'department_name', 'department',
            'email', 'gender', 'manager_image', 'shift', 'dob', 'hired_date',
            'username', 'password', 'role', 'location', 'streams'
        ]
        read_only_fields = ['manager_id']

    def validate_username(self, value):
        if self.instance:
            if Manager.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A manager with this username already exists.")
        else:
            if Manager.objects.filter(username=value).exists():
                raise serializers.ValidationError("A manager with this username already exists.")
        return value

    def validate_email(self, value):
        if self.instance:
            if Manager.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A manager with this email already exists.")
        else:
            if Manager.objects.filter(email=value).exists():
                raise serializers.ValidationError("A manager with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        return super().update(instance, validated_data)

        
    
class HrSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)
 
    class Meta:
        model = Hr
        fields = ['id', 'hr_id', 'hr_name', 'department_name', 'department', 'email',
                  'gender', 'hr_image', 'shift', 'dob', 'hired_date', 'username',
                  'password', 'role','location','streams']
        read_only_fields = ['hr_id']  # Prevent manual input of hr_id
 

    def validate_username(self, value):
        if self.instance:
            if Hr.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("An HR with this username already exists.")
        else:
            if Hr.objects.filter(username=value).exists():
                raise serializers.ValidationError("An HR with this username already exists.")
        return value
 
    def validate_email(self, value):
        """
        Ensure email is unique across HRs.
        """
        if self.instance:
            if Hr.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("An HR with this email already exists.")
        else:
            if Hr.objects.filter(email=value).exists():
                raise serializers.ValidationError("An HR with this email already exists.")
        return value
   
    def validate_password(self, value):
        """
        Custom password validator using Django's built-in validation.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
 
    def create(self, validated_data):
        """
        Overridden create method to hash the password before saving the manager.
        """
        raw_password = validated_data.pop('password')  # Remove password from validated data
        try:
            # Ensure password meets complexity requirements
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e  # Propagate the error if validation fails
        
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password  # Store the hashed password
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        If the password is being updated, hash the new password before saving.
        """
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        
        return super().update(instance, validated_data)

    
    

class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = [
            'id', 'supervisor_id', 'supervisor_name', 'department_name', 'department', 'email',
            'gender', 'supervisor_image', 'shift', 'dob', 'hired_date', 'username', 'password',
            'role', 'location', 'phone_number', 'address', 'city', 'country', 'pincode',
            'linkedin_profile_link','state','streams'
        ]
        read_only_fields = ['supervisor_id']

    def validate_username(self, value):
        if self.instance:
            if Supervisor.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A Supervisor with this username already exists.")
        else:
            if Supervisor.objects.filter(username=value).exists():
                raise serializers.ValidationError("A Supervisor with this username already exists.")
        return value

    def validate_email(self, value):
        if self.instance:
            if Supervisor.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A Supervisor with this email already exists.")
        else:
            if Supervisor.objects.filter(email=value).exists():
                raise serializers.ValidationError("A Supervisor with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        try:
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e
        
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        
        return super().update(instance, validated_data)
	    

class EmployeeSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'employee_name', 'department_name', 'department',
            'email', 'gender', 'employee_image', 'shift', 'dob', 'hired_date',
            'username', 'password', 'role' ,'location','streams'
        ]
        read_only_fields = ['employee_id']

    def validate_username(self, value):
        """
        Ensure username is unique across employees.
        """
        if self.instance:
            if Employee.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("An employee with this username already exists.")
        else:
            if Employee.objects.filter(username=value).exists():
                raise serializers.ValidationError("An employee with this username already exists.")
        return value

    def validate_password(self, value):
        """
        Custom password validator using Django's built-in validation.
        """
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        """
        Ensure email is unique across employees.
        """
        if self.instance:
            if Employee.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("An employee with this email already exists.")
        else:
            if Employee.objects.filter(email=value).exists():
                raise serializers.ValidationError("An employee with this email already exists.")
        return value

    def create(self, validated_data):
        """
        Overridden create method to hash the password before saving the employee.
        """
        raw_password = validated_data.pop('password')  # Remove password from validated data
        try:
            # Ensure password meets complexity requirements
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e  # Propagate the error if validation fails
        
        # Hash password using bcrypt
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password  # Store the hashed password
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        If the password is being updated, hash the new password before saving.
        """
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        
        return super().update(instance, validated_data)

    

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id','department_id', 'department_name']

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id','shift_number', 'shift_start_time', 'shift_end_time']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id','location_id', 'location_name']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    user_id = serializers.CharField(max_length=100)
    password = serializers.CharField(max_length=255, write_only=True)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, write_only=True)
    
from rest_framework import serializers
from .models import Ar, Todo, News, Ticket, Req, Requests

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'created_on']

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'created_date']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            'id', 'title', 'description', 'created_on', 'last_updated',
            'created_by', 'Reciver', 'assigned_to', 'status', 'proof'
        ]

class ReqSerializer(serializers.ModelSerializer):
    class Meta:
        model = Req
        fields = ['id', 'title', 'description']

class RequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requests
        fields = [
            'id', 'employee', 'supervisor', 'admin', 'title', 'request_ticket_id',
            'description', 'status', 'admin_status', 'created_on', 'updated_on'
        ]
    



class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class ManagingDirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagingDirector
        fields = '__all__'






from rest_framework import serializers
from authentication.models import Manager, Employee, Skill
from attendance.models import Attendance
from kpi.models import PerformanceReview
from documents.models import Document, ManagerDocument
from projectmanagement.models import Task, employee_task


# ----------------------------------
# Manager-Related Serializers
# ----------------------------------




class ManagerAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['date', 'status']


class ManagerPerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = ['review_date', 'score', 'comments']


class ManagerSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill_name', 'proficiency_level']


class ManagerTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['task_name', 'completion_date']


class ManagerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerDocument
        fields = ['description', 'aadhar_card', 'pan_card', 'bank_details', 
                  'previous_payslip', 'experience_certificate', 'degree_certificate']


# ----------------------------------
# Employee-Related Serializers
# ----------------------------------




class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['date', 'status']


class EmployeePerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = ['review_date', 'score', 'comments']


class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['skill_name', 'proficiency_level']


class EmployeeTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = employee_task
        fields = ['task_name', 'completion_date']


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['description', 'aadhar_card', 'pan_card', 'bank_details', 
                  'previous_payslip', 'experience_certificate', 'degree_certificate']
        

from rest_framework import serializers
from .models import Hiring

class HiringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hiring
        fields = '__all__'

    def validate_no_requirement(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Number of requirements must be a number.")
        return value

#Job Alert Hr Flow 

from .models import JobAlert

class JobAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAlert
        fields = [
            'job_id',
            'title',
            'department',
            'location',
            'type',
            'posted',
            'applications',
            'status'
        ]


#Candidate  Hr Flow
from .models import Candidate
class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            'c_id',
            'name',
            'phone',
            'jobTitle',
            'resume',
            'status'
        ]


######################## New User Serializer After the  change flow ###########################################


from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'user_id', 'user_name', 'department', 'email', 'gender', 'user_image',
            'shift', 'dob', 'hired_date', 'username', 'password', 'designation',
            'location', 'streams'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'user_id': {'read_only': True},
            'reset_token': {'read_only': True},
            'token_expiration': {'read_only': True}
        }

    def validate_email(self, value):
        if self.instance:
            if User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        else:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if self.instance:
            if User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
                raise serializers.ValidationError("A user with this username already exists.")
        else:
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_streams(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("Streams must be a valid JSON object.")
        return value

    def validate_designation(self, value):
        valid_designations = ['Employee', 'Supervisor', 'Human Resources']
        if value not in valid_designations:
            raise serializers.ValidationError(f"Designation must be one of: {', '.join(valid_designations)}.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def create(self, validated_data):
        raw_password = validated_data.pop('password')
        try:
            self.validate_password(raw_password)
        except serializers.ValidationError as e:
            raise e

        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        validated_data['password'] = hashed_password
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            raw_password = validated_data.pop('password')
            try:
                self.validate_password(raw_password)
            except serializers.ValidationError as e:
                raise e
            hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            validated_data['password'] = hashed_password
        return super().update(instance, validated_data)
    

class UserDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'username']
