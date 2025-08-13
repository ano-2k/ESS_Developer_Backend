from django.db import models
from authentication.models import Employee, Manager

# Create your models here.

class PerformanceReview(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    review_date = models.DateField()
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)  # Can be a manager or a peer
    comments = models.TextField()
    score = models.IntegerField()  # Score out of 10

    

class Goal(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    goal_text = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    

class Feedback(models.Model):
    from_manager = models.ForeignKey(Manager, related_name='from_manager', on_delete=models.CASCADE)
    to_employee = models.ForeignKey(Employee, related_name='to_employee', on_delete=models.CASCADE)
    feedback_date = models.DateField()
    comments = models.TextField()



class ManagerPerformanceReview(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    review_date = models.DateField()
    comments = models.TextField()
    score = models.IntegerField()  # Score out of 10

    

class ManagerGoal(models.Model):
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE)
    goal_text = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    is_completed = models.BooleanField(default=False)

    

class ManagerFeedback(models.Model):
    to_manager = models.ForeignKey(Manager, related_name='to_manager', on_delete=models.CASCADE)
    feedback_date = models.DateField()
    comments = models.TextField()


class OverallFeedback(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, null=True, blank=True)
    feedback_date = models.DateField(auto_now_add=True)
    comments = models.TextField()
    is_reviewed = models.CharField(max_length=3, choices=[('No', 'No'), ('Yes', 'Yes')], default='No')



    
    
