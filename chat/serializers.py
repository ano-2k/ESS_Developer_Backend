from rest_framework import serializers
from .models import Message, UnreadMessage, Group, GroupChatMessage, MessageStatus
from authentication.models import Employee, Manager, Supervisor, Admin, ManagingDirector

# Serializers for the authentication models
class EmployeeSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    last_message_is_read = serializers.BooleanField(read_only=True)
    last_message_delivered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'name', 'email', 'unread_count', 'last_message', 
                  'last_message_sent_by_current_user', 'last_message_is_read', 'last_message_delivered']


class ManagerSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    last_message_is_read = serializers.BooleanField(read_only=True)
    last_message_delivered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Manager
        fields = ['id', 'name', 'email', 'unread_count', 'last_message', 
                  'last_message_sent_by_current_user', 'last_message_is_read', 'last_message_delivered']


class SupervisorSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    last_message_is_read = serializers.BooleanField(read_only=True)
    last_message_delivered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Supervisor
        fields = ['id', 'name', 'email', 'unread_count', 'last_message', 
                  'last_message_sent_by_current_user', 'last_message_is_read', 'last_message_delivered']


class AdminSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    last_message_is_read = serializers.BooleanField(read_only=True)
    last_message_delivered = serializers.BooleanField(read_only=True)

    class Meta:
        model = Admin
        fields = ['id', 'username', 'unread_count', 'last_message', 
                  'last_message_sent_by_current_user', 'last_message_is_read', 'last_message_delivered']


class ManagingDirectorSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    last_message_is_read = serializers.BooleanField(read_only=True)
    last_message_delivered = serializers.BooleanField(read_only=True)

    class Meta:
        model = ManagingDirector
        fields = ['id', 'username', 'unread_count', 'last_message', 
                  'last_message_sent_by_current_user', 'last_message_is_read', 'last_message_delivered']


# Serializers for the chat models
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender_id', 'receiver_id', 'sender_type', 'receiver_type', 
                  'content', 'is_read', 'is_delivered', 'chat_type', 'timestamp']


class UnreadMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnreadMessage
        fields = ['id', 'message', 'user_id', 'timestamp']


class GroupSerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True, read_only=True)
    managers = ManagerSerializer(many=True, read_only=True)
    supervisors = SupervisorSerializer(many=True, read_only=True)
    admins = AdminSerializer(many=True, read_only=True)
    mds = ManagingDirectorSerializer(many=True, read_only=True)
    last_message = serializers.CharField(read_only=True)
    last_message_sent_by_current_user = serializers.BooleanField(read_only=True)
    unread_group_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'employees', 'managers', 'supervisors', 
                  'admins', 'mds', 'last_message', 'last_message_sent_by_current_user', 'unread_group_count']


class GroupChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupChatMessage
        fields = ['id', 'group', 'sender_id', 'sender_type', 'message', 
                  'timestamp', 'is_read']


class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageStatus
        fields = ['id', 'message', 'user_id', 'is_read', 'is_delivered', 'timestamp']
