from rest_framework import serializers

from authentication.models import Employee, Manager
from .models import PerformanceReview, Goal, Feedback, ManagerPerformanceReview, ManagerGoal, ManagerFeedback, OverallFeedback

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id','employee_id', 'employee_name'] 
        
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id','manager_id', 'manager_name']               

class PerformanceReviewSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = PerformanceReview
        fields = ['id', 'employee', 'review_date', 'manager', 'comments', 'score']

class GoalSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = Goal
        fields = ['id', 'employee', 'goal_text', 'start_date', 'end_date', 'is_completed']

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'employee_name']

class FeedbackSerializer(serializers.ModelSerializer):
    from_manager = ManagerSerializer(read_only=True)
    to_employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'from_manager', 'to_employee', 'feedback_date', 'comments']
        
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id','manager_id', 'manager_name']          

class ManagerPerformanceReviewSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    # review_date = serializers.SerializerMethodField()  # Use custom method to format review_date

    class Meta:
        model = ManagerPerformanceReview
        fields = ['id', 'manager', 'review_date', 'comments', 'score']

    

class ManagerGoalSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    class Meta:
        model = ManagerGoal
        fields = ['id', 'manager', 'goal_text', 'start_date', 'end_date', 'is_completed']

class ManagerFeedbackSerializer(serializers.ModelSerializer):
    to_manager = ManagerSerializer(read_only=True)
    class Meta:
        model = ManagerFeedback
        fields = ['id', 'to_manager', 'feedback_date', 'comments']

class OverallFeedbackSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    employee = EmployeeSerializer(read_only=True)
    class Meta:
        model = OverallFeedback
        fields = ['id', 'employee', 'manager', 'feedback_date', 'comments', 'is_reviewed']

from rest_framework import serializers
from .models import ManagerPerformanceReview

class ManagerPerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerPerformanceReview
        fields = ['id', 'manager', 'review_date', 'comments', 'score']
        # Optionally, include related manager details
        depth = 1  # Uncomment this line to include nested manager details (optional)



# serializers.py


