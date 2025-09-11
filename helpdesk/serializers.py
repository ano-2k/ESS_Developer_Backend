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







#---------------------------------------------OLD WORKING VERSION FOR INDIVIDUAL LOGINS --------------------------------------------------------------------------------------


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
        
        
    
################################################# New Changes Sep 8 ###############################################################################
    
from .models import UserTicket, User

class UserTicketSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(required=True)
    raise_to = serializers.CharField(required=False, allow_null=True)
    replies = TicketReplySerializer(many=True, read_only=True)

    class Meta:
        model = UserTicket
        fields = [
            'ticket_id', 'subject', 'description', 'service_type', 'attachment',
            'created_by', 'raise_to', 'status', 'created_on', 'last_updated', 'replies'
        ]

    def validate_created_by(self, value):
        """
        Validate created_by user and store their designation
        for service_type validation later.
        """
        try:
            user = User.objects.get(user_id=value)
            self.user_designation = user.designation  # Save designation for later
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with user_id {value} does not exist.")

    def validate_raise_to(self, value):
        """
        Validate raise_to user.
        """
        if value:
            try:
                return User.objects.get(user_id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError(f"User with user_id {value} does not exist.")
        return None

    def validate_service_type(self, value):
        """
        Restrict service_type choices based on the creator's designation.
        """
        if hasattr(self, 'user_designation'):
            designation = self.user_designation
            if designation == 'Employee':
                allowed = [
                    'task_late_submission','project_materials','risk_management',
                    'project_deadline','project_plan','resource_allocation','others'
                ]
            elif designation == 'Supervisor':
                allowed = [
                    'reports_of_project','reports_of_tasks','team_conflicts',
                    'communication_issue','performance_related','others'
                ]
            elif designation == 'Human Resources':
                allowed = [
                    'leave_policy','leave_request_related','login_issue','salary_related',
                    'attendance_related','training_conflicts','others'
                ]
            else:
                allowed = ['others']

            if value not in allowed:
                raise serializers.ValidationError(
                    f"Service type '{value}' is not allowed for {designation}."
                )
        return value

    def create(self, validated_data):
        """
        Create ticket and assign created_by and raise_to.
        """
        created_by = validated_data.pop('created_by')
        raise_to = validated_data.pop('raise_to', None)

        ticket = UserTicket.objects.create(
            created_by=created_by,
            raise_to=raise_to,
            **validated_data
        )
        return ticket

    def update(self, instance, validated_data):
        """
        Update ticket fields.
        """
        if 'created_by' in validated_data:
            instance.created_by = validated_data.pop('created_by')
        if 'raise_to' in validated_data:
            instance.raise_to = validated_data.pop('raise_to')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Represent the ticket with full details.
        """
        representation = super().to_representation(instance)

        representation['created_by'] = {
            "user_id": instance.created_by.user_id,
            "name": instance.created_by.user_name,
            "designation": instance.created_by.designation
        } if instance.created_by else None

        representation['raise_to'] = {
            "user_id": instance.raise_to.user_id,
            "name": instance.raise_to.user_name,
            "designation": instance.raise_to.designation
        } if instance.raise_to else None

        representation['service_type'] = instance.get_service_type_display() if instance.service_type else 'Others'

        return representation
    
    
######################################## SEP 11 NEW VERSION UNIFIED VERSION ################################


class UserCombinedTicketSerializer(serializers.Serializer):
    ticket_id = serializers.CharField()
    subject = serializers.CharField()
    created_on = serializers.DateTimeField()
    last_updated = serializers.DateTimeField()
    status = serializers.CharField()
    raise_to = serializers.SerializerMethodField()
    service_type = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    manager_id = serializers.SerializerMethodField()
    latest_reply = serializers.SerializerMethodField()

    def get_raise_to(self, obj):
        # Works for UserTicket and legacy tickets
        if hasattr(obj, 'raise_to') and obj.raise_to:
            return {
                "user_id": obj.raise_to.user_id,
                "name": obj.raise_to.user_name,
                "designation": obj.raise_to.designation
            }
        return "Unassigned"

    def get_created_by(self, obj):
        # Replaces old employee/hr/supervisor fields
        if hasattr(obj, 'created_by') and obj.created_by:
            return {
                "user_id": obj.created_by.user_id,
                "name": obj.created_by.user_name,
                "designation": obj.created_by.designation
            }
        return None

    def get_manager_id(self, obj):
        # Keeps legacy ManagerTicket handling intact
        if hasattr(obj, 'manager') and obj.manager:
            return obj.manager.manager_id
        elif hasattr(obj, 'manager_id'):
            return obj.manager_id
        return None

    def get_service_type(self, obj):
        if isinstance(obj, OtherTicket):
            return obj.service_type if obj.service_type else ''
        return obj.get_service_type_display() if obj.service_type else "Others"

    def get_latest_reply(self, obj):
        if hasattr(obj, 'replies'):
            replies = obj.replies.all().order_by('-id')
            return TicketReplySerializer(replies[0]).data if replies.exists() else None
        return None
    
    

from authentication.models import User

class HelpdeskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'user_name', 'designation']
