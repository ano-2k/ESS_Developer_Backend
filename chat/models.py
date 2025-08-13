from django.db import models
from pytz import timezone
from authentication.models import Admin, Employee, Manager, ManagingDirector,Supervisor

class Message(models.Model):
    sender_id = models.CharField(max_length=100)  # Employee ID or Manager ID
    receiver_id = models.CharField(max_length=100)  # ID of the user receiving the message
    sender_type = models.CharField(max_length=10)  
    receiver_type = models.CharField(max_length=10, null=True, blank=True)  
    content = models.TextField()
    is_read = models.BooleanField(default=False)  # Field to track if the message is read
    is_delivered = models.BooleanField(default=False) 
    chat_type = models.CharField(max_length=20, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_type} {self.sender_id} -> {self.sender_type} {self.receiver_id}: {self.content}"
    
class UnreadMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

class Group(models.Model):
    name = models.CharField(max_length=100, unique=True)
    employees = models.ManyToManyField(Employee, blank=True)
    managers = models.ManyToManyField(Manager, blank=True)
    supervisors = models.ManyToManyField(Supervisor, blank=True)
    admins = models.ManyToManyField(Admin, blank=True)
    mds = models.ManyToManyField(ManagingDirector, blank=True)

    def __str__(self):
        return self.name
    
class GroupChatMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender_id = models.CharField(max_length=100)
    sender_type = models.CharField(max_length=10)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender_type} {self.sender_id}: {self.message[:50]}"

    class Meta:
        ordering = ['timestamp']

class MessageStatus(models.Model):
    message = models.ForeignKey(GroupChatMessage, on_delete=models.CASCADE, related_name='statuses')
    user_id = models.CharField(max_length=100)  # ID of the user (employee, manager, or admin)
    is_read = models.BooleanField(default=False)  # Indicates if the user has read the message
    is_delivered = models.BooleanField(default=False)  # Indicates if the message has been delivered to the user
    timestamp = models.DateTimeField(auto_now_add=True)  # Time of status update

    class Meta:
        unique_together = ('message', 'user_id')  # Ensure unique status entries per message per user