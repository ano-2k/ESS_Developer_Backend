from rest_framework import serializers
from authentication.models import Admin, Hr, Supervisor, Manager,Employee
from .models import AdministrativeTicket, HRTicket, SupervisorTicket, SystemTicket, OtherTicket, TicketReply,ManagerTicket,EmployeeTicket

class TicketReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketReply
        fields = ['id', 'reply_text', 'content_type', 'object_id']
        read_only_fields = ['id', 'content_type', 'object_id']
        
        
class AdministrativeTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    user_id = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)
    supervisor_id = serializers.CharField(allow_null=True, required=False)
    hr_id = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)
    

    class Meta:
        model = AdministrativeTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'user_id', 'manager_id', 'supervisor_id', 'hr_id', 'employee_id','replies']

    def validate_raise_to(self, value):
        if value:
            try:
                admin = Admin.objects.get(user_id=value)
                return admin
            except Admin.DoesNotExist:
                raise serializers.ValidationError(f"Admin with user_id {value} does not exist.")
        return None

    def validate_manager_id(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None

    def validate_supervisor_id(self, value):
        if value:
            try:
                supervisor = Supervisor.objects.get(supervisor_id=value)
                return supervisor
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError(f"Supervisor with supervisor_id {value} does not exist.")
        return None

    def validate_hr_id(self, value):
        if value:
            try:
                hr = Hr.objects.get(hr_id=value)
                return hr
            except Hr.DoesNotExist:
                raise serializers.ValidationError(f"Hr with hr_id {value} does not exist.")
        return None
    
    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None


    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if user_id:
            ticket.user_id = user_id
        if manager:
            ticket.manager = manager
        if supervisor:
            ticket.supervisor = supervisor
        if hr:
            ticket.hr = hr
        if employee:
            ticket.employee = employee
            
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        instance = super().update(instance, validated_data)
        if user_id:
            instance.user_id = user_id
        if manager:
            instance.manager = manager
        if supervisor:
            instance.supervisor = supervisor
        if hr:
            instance.hr = hr
        if employee:
            instance.employee = employee
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_id'] = instance.user_id
        representation['raise_to'] = instance.raise_to.username if instance.raise_to else None
        representation['manager_id'] = instance.manager.manager_id if instance.manager else None
        representation['manager_name'] = instance.manager.manager_name if instance.manager else None
        representation['supervisor_id'] = instance.supervisor.supervisor_id if instance.supervisor else None
        representation['supervisor_name'] = instance.supervisor.supervisor_name if instance.supervisor else None
        representation['hr_id'] = instance.hr.hr_id if instance.hr else None
        representation['hr_name'] = instance.hr.hr_name if instance.hr else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        return representation

class HRTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    hr_id = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)
    supervisor_id = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = HRTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'hr_id', 'manager_id', 'supervisor_id', 'employee_id','replies']

    def validate_raise_to(self, value):
        if value:
            try:
                hr = Hr.objects.get(hr_id=value)
                return hr
            except Hr.DoesNotExist:
                raise serializers.ValidationError(f"Hr with hr_id {value} does not exist.")
        return None

    def validate_manager_id(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None

    def validate_supervisor_id(self, value):
        if value:
            try:
                supervisor = Supervisor.objects.get(supervisor_id=value)
                return supervisor
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError(f"Supervisor with supervisor_id {value} does not exist.")
        return None
    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None

    def create(self, validated_data):
        hr_id = validated_data.pop('hr_id', None) or (validated_data.get('raise_to').hr_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if hr_id:
            ticket.hr_id = hr_id
        if manager:
            ticket.manager = manager
        if supervisor:
            ticket.supervisor = supervisor
        if employee:
            ticket.employee = employee
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        hr_id = validated_data.pop('hr_id', None) or (validated_data.get('raise_to').hr_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        employee = validated_data.pop('employee_id', None)
        instance = super().update(instance, validated_data)
        if hr_id:
            instance.hr_id = hr_id
        if manager:
            instance.manager = manager
        if supervisor:
            instance.supervisor = supervisor
        if employee:
            instance.employee = employee
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['hr_id'] = instance.hr_id
        representation['raise_to'] = instance.raise_to.hr_name if instance.raise_to else None
        representation['manager_id'] = instance.manager.manager_id if instance.manager else None
        representation['manager_name'] = instance.manager.manager_name if instance.manager else None
        representation['supervisor_id'] = instance.supervisor.supervisor_id if instance.supervisor else None
        representation['supervisor_name'] = instance.supervisor.supervisor_name if instance.supervisor else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        return representation

class SupervisorTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    supervisor_id = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)  # Add manager_id field
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = SupervisorTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'supervisor_id', 'manager_id','employee_id', 'replies']

    def validate_raise_to(self, value):
        if value:
            try:
                supervisor = Supervisor.objects.get(supervisor_id=value)
                return supervisor
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError(f"Supervisor with supervisor_id {value} does not exist.")
        return None

    def validate_manager_id(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None
    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None

    def create(self, validated_data):
        supervisor_id = validated_data.pop('supervisor_id', None) or (validated_data.get('raise_to').supervisor_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)  # Pop manager (validated as Manager instance)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if supervisor_id:
            ticket.supervisor_id = supervisor_id
        if manager:
            ticket.manager = manager  # Set manager ForeignKey
        if employee:
            ticket.employee = employee
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        supervisor_id = validated_data.pop('supervisor_id', None) or (validated_data.get('raise_to').supervisor_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)  # Pop manager (validated as Manager instance)
        employee = validated_data.pop('employee_id', None)
        instance = super().update(instance, validated_data)
        if supervisor_id:
            instance.supervisor_id = supervisor_id
        if manager:
            instance.manager = manager  # Update manager ForeignKey
        if employee:
            instance.employee = employee
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['supervisor_id'] = instance.supervisor_id
        representation['raise_to'] = instance.raise_to.supervisor_name if instance.raise_to else None
        representation['manager_id'] = instance.manager.manager_id if instance.manager else None  # Return manager_id
        representation['manager_name'] = instance.manager.manager_name if instance.manager else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        
        return representation

class SystemTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    user_id = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)
    supervisor_id = serializers.CharField(allow_null=True, required=False)
    hr_id = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = SystemTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'user_id', 'manager_id', 'supervisor_id', 'hr_id','employee_id', 'replies']

    def validate_raise_to(self, value):
        if value:
            try:
                admin = Admin.objects.get(user_id=value)
                return admin
            except Admin.DoesNotExist:
                raise serializers.ValidationError(f"Admin with user_id {value} does not exist.")
        return None

    def validate_manager_id(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None

    def validate_supervisor_id(self, value):
        if value:
            try:
                supervisor = Supervisor.objects.get(supervisor_id=value)
                return supervisor
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError(f"Supervisor with supervisor_id {value} does not exist.")
        return None

    def validate_hr_id(self, value):
        if value:
            try:
                hr = Hr.objects.get(hr_id=value)
                return hr
            except Hr.DoesNotExist:
                raise serializers.ValidationError(f"Hr with hr_id {value} does not exist.")
        return None
    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if user_id:
            ticket.user_id = user_id
        if manager:
            ticket.manager = manager
        if supervisor:
            ticket.supervisor = supervisor
        if hr:
            ticket.hr = hr
        if employee:
            ticket.employee = employee
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        instance = super().update(instance, validated_data)
        if user_id:
            instance.user_id = user_id
        if manager:
            instance.manager = manager
        if supervisor:
            instance.supervisor = supervisor
        if hr:
            instance.hr = hr
        if employee:
            instance.employee = employee
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_id'] = instance.user_id
        representation['raise_to'] = instance.raise_to.username if instance.raise_to else None
        representation['manager_id'] = instance.manager.manager_id if instance.manager else None
        representation['manager_name'] = instance.manager.manager_name if instance.manager else None
        representation['supervisor_id'] = instance.supervisor.supervisor_id if instance.supervisor else None
        representation['supervisor_name'] = instance.supervisor.supervisor_name if instance.supervisor else None
        representation['hr_id'] = instance.hr.hr_id if instance.hr else None
        representation['hr_name'] = instance.hr.hr_name if instance.hr else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        return representation

class OtherTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    user_id = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)
    supervisor_id = serializers.CharField(allow_null=True, required=False)
    hr_id = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = OtherTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'user_id', 'manager_id', 'supervisor_id', 'hr_id','employee_id', 'replies']

    def validate_raise_to(self, value):
        if value:
            try:
                admin = Admin.objects.get(user_id=value)
                return admin
            except Admin.DoesNotExist:
                raise serializers.ValidationError(f"Admin with user_id {value} does not exist.")
        return None

    def validate_manager_id(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None

    def validate_supervisor_id(self, value):
        if value:
            try:
                supervisor = Supervisor.objects.get(supervisor_id=value)
                return supervisor
            except Supervisor.DoesNotExist:
                raise serializers.ValidationError(f"Supervisor with supervisor_id {value} does not exist.")
        return None

    def validate_hr_id(self, value):
        if value:
            try:
                hr = Hr.objects.get(hr_id=value)
                return hr
            except Hr.DoesNotExist:
                raise serializers.ValidationError(f"Hr with hr_id {value} does not exist.")
        return None
    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None

    def create(self, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if user_id:
            ticket.user_id = user_id
        if manager:
            ticket.manager = manager
        if supervisor:
            ticket.supervisor = supervisor
        if hr:
            ticket.hr = hr
        if employee:
            ticket.employee = employee
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        user_id = validated_data.pop('user_id', None) or (validated_data.get('raise_to').user_id if validated_data.get('raise_to') else None)
        manager = validated_data.pop('manager_id', None)
        supervisor = validated_data.pop('supervisor_id', None)
        hr = validated_data.pop('hr_id', None)
        employee = validated_data.pop('employee_id', None)
        instance = super().update(instance, validated_data)
        if user_id:
            instance.user_id = user_id
        if manager:
            instance.manager = manager
        if supervisor:
            instance.supervisor = supervisor
        if hr:
            instance.hr = hr
        if employee:
            instance.employee = employee
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_id'] = instance.user_id
        representation['raise_to'] = instance.raise_to.username if instance.raise_to else None
        representation['manager_id'] = instance.manager.manager_id if instance.manager else None
        representation['manager_name'] = instance.manager.manager_name if instance.manager else None
        representation['supervisor_id'] = instance.supervisor.supervisor_id if instance.supervisor else None
        representation['supervisor_name'] = instance.supervisor.supervisor_name if instance.supervisor else None
        representation['hr_id'] = instance.hr.hr_id if instance.hr else None
        representation['hr_name'] = instance.hr.hr_name if instance.hr else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
        representation['service_type'] = instance.service_type if instance.service_type else 'Others'
        return representation
    
    

#---------------------------------------------------------------------------------------------------


       
        
class ManagerTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    manager_id = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)
    

    class Meta:
        model = ManagerTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'manager_id', 'employee_id', 'replies']

    def validate_raise_to(self, value):
        if value:
            try:
                manager = Manager.objects.get(manager_id=value)
                return manager
            except Manager.DoesNotExist:
                raise serializers.ValidationError(f"Manager with manager_id {value} does not exist.")
        return None

    def validate_employee_id(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None


    def create(self, validated_data):
        manager_id = validated_data.pop('manager_id', None) or (validated_data.get('raise_to').manager_id if validated_data.get('raise_to') else None)
        employee = validated_data.pop('employee_id', None)
        ticket = super().create(validated_data)
        if manager_id:
            ticket.manager_id = manager_id
        if employee:
            ticket.employee = employee
     
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        manager_id = validated_data.pop('manager_id', None) or (validated_data.get('raise_to').manager_id if validated_data.get('raise_to') else None)
        employee = validated_data.pop('employee_id', None)
       
        instance = super().update(instance, validated_data)
        if manager_id:
            instance.manager_id = manager_id
        if employee:
            instance.employee = employee
       
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['manager_id'] = instance.manager_id
        representation['raise_to'] = instance.raise_to.manager_name if instance.raise_to else None
        representation['employee_id'] = instance.employee.employee_id if instance.employee else None
        representation['employee_name'] = instance.employee.employee_name if instance.employee else None
       
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        return representation


#--------------------------------rough SERIALIZER for employee need to be changee after the system and other implementation ----------
class EmployeeTicketSerializer(serializers.ModelSerializer):
    raise_to = serializers.CharField(allow_null=True, required=False)
    employee_id = serializers.CharField(allow_null=True, required=False)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeTicket
        fields = ['ticket_id', 'subject', 'description', 'service_type', 'attachment', 'raise_to', 'created_on', 'last_updated', 'status', 'employee_id', 'replies']

    def validate_raise_to(self, value):
        if value:
            try:
                employee = Employee.objects.get(employee_id=value)
                return employee
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Employee with employee_id {value} does not exist.")
        return None

    def create(self, validated_data):
        employee_id = validated_data.pop('employee_id', None) or (validated_data.get('raise_to').employee_id if validated_data.get('raise_to') else None)
        ticket = super().create(validated_data)
        if employee_id:
            ticket.employee_id = employee_id
        ticket.save()
        return ticket

    def update(self, instance, validated_data):
        employee_id = validated_data.pop('employee_id', None) or (validated_data.get('raise_to').employee_id if validated_data.get('raise_to') else None)
        instance = super().update(instance, validated_data)
        if employee_id:
            instance.employee_id = employee_id
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['employee_id'] = instance.employee_id
        representation['raise_to'] = instance.raise_to.employee_name if instance.raise_to else None
        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'
        
        return representation







#-----------------------------------------------------------------------------------------------------------------------------------


class CombinedTicketSerializer(serializers.Serializer):
    ticket_id = serializers.CharField()
    subject = serializers.CharField()
    created_on = serializers.DateTimeField()
    last_updated = serializers.DateTimeField()
    status = serializers.CharField()
    raise_to = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    manager_id = serializers.SerializerMethodField()
    supervisor_id = serializers.SerializerMethodField()
    hr_id = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    latest_reply = serializers.SerializerMethodField()

    def get_raise_to(self, obj):
        if isinstance(obj, (AdministrativeTicket, SystemTicket, OtherTicket)):
            return obj.raise_to.username if obj.raise_to else "Unassigned"
        elif isinstance(obj, HRTicket):
            return obj.raise_to.hr_name if obj.raise_to else "Unassigned"
        elif isinstance(obj, SupervisorTicket):
            return obj.raise_to.supervisor_name if obj.raise_to else "Unassigned"
        elif isinstance(obj, ManagerTicket):
            return obj.raise_to.manager_name if obj.raise_to else "Unassigned"
        return "Unassigned"

    def get_manager_id(self, obj):
     if hasattr(obj, 'manager') and obj.manager:
        return obj.manager.manager_id
     elif hasattr(obj, 'manager_id'):
        return obj.manager_id
     return None


    def get_supervisor_id(self, obj):
        return obj.supervisor.supervisor_id if hasattr(obj, 'supervisor') and obj.supervisor else None
    
    def get_hr_id(self, obj):
        return obj.hr.hr_id if hasattr(obj, 'hr') and obj.hr else None
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id if hasattr(obj, 'employee') and obj.employee else None

    def get_service_type(self, obj):
        if isinstance(obj, OtherTicket):
            return obj.service_type if obj.service_type else ''
        return obj.get_service_type_display() if obj.service_type else "Others"
    

    def get_latest_reply(self, obj):
        replies = obj.replies.all().order_by('-id')
        return TicketReplySerializer(replies[0]).data if replies.exists() else None

class HelpdeskAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['user_id', 'username']

class HelpdeskHrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hr
        fields = ['hr_id', 'hr_name']

class HelpdeskSupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['supervisor_id', 'supervisor_name']
        
class HelpdeskManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['manager_id', 'manager_name']
        
        
        
