from rest_framework import serializers

from authentication.models import Employee
from .models import TaskLog, Task, Team
from .models import employee_task
from .models import Project
from .models import Task, Manager
from .models import TrainingProgram
from .models import TrainingParticipation
from rest_framework import serializers
from .models import TrainingProgram, TrainingParticipation
from rest_framework import serializers
from .models import TrainingProgram
from rest_framework import serializers
from .models import   Manager
from kpi.models import  Goal
from .models import TrainingProgram, TrainingParticipation
from .models import Certification
from django.utils import timezone
from .models import Role
from .models import Team, Employee, Manager, Project
from authentication.serializers import ManagerSerializer,EmployeeSerializer
from authentication.models import User
from authentication.serializers import UserSerializer,UserDashboardSerializer


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = ['id', 'task', 'employee', 'manager', 'check_in_time', 'check_out_time', 'hours_worked']
        

class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """
    class Meta:
        model = Role
        fields = ['id', 'role_id', 'role_name']

    def validate(self, data):
        # Custom validation (if needed) can be added here
        return data

class EmployeeTaskSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.name', read_only=True)

    class Meta:
        model = employee_task
        fields = [
            'id',
            'emptask_id',
            'task_name',
            'task_description',
            'assigned_to',
            'deadline',
            'team_name',
            'team_project_name',
            'emp_taskstatus',
            'completion_date',
            'completion_reason',
            'manager',
            'manager_name',
        ]



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id','project_id', 'name', 'description', 'start_date', 'deadline', 'project_manager']



class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['manager_id', 'manager_name', 'shift']    

class TaskSerializer(serializers.ModelSerializer):
    # project_name = ProjectSerializer(read_only=True)
    manager = ManagerSerializer(read_only=True)
    class Meta:
        model = Task
        fields = ['id', 'task_id', 'task_name', 'description', 'priority', 'start_date', 'deadline', 
                  'project_name', 'status', 'manager', 'completion_date', 'completion_reason']

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id','manager_name','manager_id',]


# class TeamSerializer(serializers.ModelSerializer):
#     manager = ManagerSerializer()  # Nested serializer to get manager details
#     project = ProjectSerializer()  # Nested serializer to get project details
#     team_leader = UserSerializer()  # Nested serializer to get team leader details
#     members = UserSerializer(many=True)  # Nested serializer to get all team members

#     class Meta:
#         model = Team
#         fields = ['team_id', 'team_name', 'project', 'team_task', 'manager', 'team_leader', 'members']

class TrainingProgramSerializer(serializers.ModelSerializer):
    training_incharge = serializers.PrimaryKeyRelatedField(
        queryset=Manager.objects.all(),  # Replace with your Manager model
        required=True,  # Make this field required
    )
    # manager = ManagerSerializer(read_only=True)
    
    class Meta:
        model = TrainingProgram
        fields = [
            'program_id',
            'name',
            'start_date',
            'end_date',
            'description',
            'for_managers',
            'for_employees',
            'training_incharge'
        ]


class TrainingParticipationSerializer(serializers.ModelSerializer):
    program = serializers.PrimaryKeyRelatedField(
        queryset=TrainingProgram.objects.all(),  # Replace with your Manager model
        required=True,  # Make this field required
    )
    manager = serializers.PrimaryKeyRelatedField(
        queryset=Manager.objects.all(),  # Replace with your Manager model
        required=False,  # Make this field required
    )
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),  # Replace with your Manager model
        required=False,  # Make this field required
    )
    class Meta:
        model = TrainingParticipation
        fields = ['id','program','manager','employee','completion_status','completion_date']

class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingParticipation
        fields = '_all_'  # List all fields or specify them as needed


class CertificationSerializer(serializers.ModelSerializer):
    participation = serializers.PrimaryKeyRelatedField(
        queryset=TrainingParticipation.objects.all(),
        required=True,
    )

    class Meta:
        model = Certification
        fields = ['id', 'certification_file', 'certification_name', 'participation', 'certification_date']

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ['id', 'employee', 'goal_text', 'start_date', 'end_date']

    employee_name = serializers.CharField(source='employee.employee_name', read_only=True)

class TeamSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)  # Example for nested field
    manager_name = serializers.CharField(source="manager.name", read_only=True)  # Assuming Manager has a name field
    team_leader_name = serializers.CharField(source="team_leader.username", read_only=True)  # Assuming Employee has a name field
    members_names = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="username",  # Assuming Employee model has a name field
        source="members",
    )

    class Meta:
        model = Team
        fields = [
            "id",
            "team_id",
            "team_name",
            "project",
            "project_name",
            "team_task",
            "manager",
            "manager_name",
            "team_leader",
            "team_leader_name",
            "members",
            "members_names",
        ]
        read_only_fields = ["id", "project_name", "manager_name", "team_leader_name", "members_names"]

    def create(self, validated_data):
        """
        Override the create method to handle `members` ManyToManyField.
        """
        members = validated_data.pop("members", [])
        team = Team.objects.create(**validated_data)
        team.members.set(members)
        return team

    def update(self, instance, validated_data):
        """
        Override the update method to handle `members` ManyToManyField.
        """
        members = validated_data.pop("members", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if members is not None:
            instance.members.set(members)
        return instance
    

# New Serializer Created For Manpower Plannning 

from .models import PositionRequest, Vacancy
from authentication.models import Employee, Manager, Location, Hr  



class PositionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all(), required=True)
    requested_by_id = serializers.CharField(source='requested_by.employee_id', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.employee_name', read_only=True)  # New field for employee name
    hr_reviewer = serializers.SlugRelatedField(
        slug_field='hr_id',  # Use hr_id as the lookup field
        queryset=Hr.objects.all(),
        required=True
    )
    hr_reviewer_id = serializers.CharField(source='hr_reviewer.hr_id', read_only=True)
    hr_reviewer_name = serializers.CharField(source='hr_reviewer.hr_name', read_only=True)  # New field for HR name
    manager_approver = serializers.SlugRelatedField(
        slug_field='manager_id',  # Use manager_id as the lookup field
        queryset=Manager.objects.all(),
        required=False,
        allow_null=True
    )
    manager_approver_id = serializers.CharField(source='manager_approver.manager_id', read_only=True)
    manager_approver_name = serializers.CharField(source='manager_approver.manager_name', read_only=True)  # New field for manager name
    location_name = serializers.CharField(source='location.location_name', read_only=True)
    role_name = serializers.CharField(source='role.role_name', read_only=True)

    class Meta:
        model = PositionRequest
        fields = [
            'id', 'request_id', 'title', 'location', 'location_name', 'experience_level',
            'job_types', 'opening_roles', 'role', 'role_name', 'requested_by', 'requested_by_id', 
            'requested_by_name', 'status', 'created_at', 'hr_reviewer', 'hr_reviewer_id', 'hr_reviewer_name',
            'manager_approver', 'manager_approver_id', 'manager_approver_name', 'approval_date'
        ]
        read_only_fields = ['request_id', 'created_at', 'approval_date', 'requested_by_id', 'location_name', 'role_name', 'hr_reviewer_id', 'manager_approver_id']

    def validate_opening_roles(self, value):
        if value <= 0:
            raise serializers.ValidationError("Opening roles must be a positive integer.")
        return value

    def validate_title(self, value):
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_location(self, value):
        if not Location.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The specified location does not exist.")
        return value

    def validate_requested_by(self, value):
        if not Employee.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("The specified employee does not exist.")
        return value

    def validate_hr_reviewer(self, value):
        if not Hr.objects.filter(hr_id=value.hr_id).exists():
            raise serializers.ValidationError("The specified HR reviewer does not exist.")
        return value

    def validate_manager_approver(self, value):
        if value and not Manager.objects.filter(manager_id=value.manager_id).exists():
            raise serializers.ValidationError("The specified manager approver does not exist.")
        return value

    def validate(self, data):
        return data

class VacancySerializer(serializers.ModelSerializer):
    position_request = serializers.PrimaryKeyRelatedField(queryset=PositionRequest.objects.all(), required=True)

    class Meta:
        model = Vacancy
        fields = [
            'vacancy_id', 'position_request', 'title', 'location',
            'experience_level', 'job_types', 'opening_roles', 'created_at', 'status'
        ]
	
		