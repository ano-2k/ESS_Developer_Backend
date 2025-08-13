from django.db import DatabaseError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from attendance import models
from authentication.models import Manager
from projectmanagement.models import Team
from .models import PerformanceReview, Employee
from .serializers import PerformanceReviewSerializer, ManagerPerformanceReviewSerializer
from django.utils import timezone
from .models import PerformanceReview
from .models import Goal, Employee
from .serializers import GoalSerializer
from .models import Goal
from .serializers import GoalSerializer
from django.utils import timezone
from .models import Feedback
from .serializers import FeedbackSerializer
from authentication.models import Manager, Employee
from .models import Feedback
from .models import PerformanceReview
from .serializers import FeedbackSerializer
from authentication.models import Employee
from projectmanagement.models import Task 
from projectmanagement.models import Task  # Assuming you have task-related data
from authentication.models import Manager 
from .models import PerformanceReview, Goal, Feedback
from .serializers import PerformanceReviewSerializer, GoalSerializer, FeedbackSerializer,ManagerPerformanceReviewSerializer
from .models import Manager, ManagerPerformanceReview
from .models import ManagerGoal
from .serializers import ManagerGoalSerializer,ManagerFeedbackSerializer
from authentication.models import Manager
from .models import ManagerPerformanceReview,ManagerFeedback
from .models import OverallFeedback
from .serializers import OverallFeedbackSerializer
from .models import Manager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Manager, ManagerPerformanceReview
from .serializers import ManagerPerformanceReviewSerializer
from django.shortcuts import get_object_or_404
from datetime import date, datetime

@api_view(['POST'])
def create_performance_review(request):
    try:
        employee_name = request.data.get('employee_name')
        manager_username = request.session.get('user')  # Assumes session-based authentication
        comments = request.data.get('comments')
        score = request.data.get('score')

        employee = Employee.objects.get(employee_name=employee_name)
        manager = Manager.objects.get(username=manager_username)

        performance_review = PerformanceReview.objects.create(
            employee=employee,
            review_date=date.today(),
            manager=manager,
            comments=comments,
            score=score,
        )

        serializer = PerformanceReviewSerializer(performance_review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.response import Response

@api_view(['GET'])
def performance_review_list(request):
    """
    Retrieve a list of all performance reviews.
    """
    try:
        # Attempt to fetch all performance reviews
        review = PerformanceReview.objects.all()
        serializer = PerformanceReviewSerializer(review, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except PerformanceReview.DoesNotExist:
        # Handle case where the PerformanceReview model does not exist
        return Response(
            {"error": "No performance reviews found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        # Handle any other unexpected exceptions
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['DELETE'])
def delete_performance_review(request, id):
    try:
        review = PerformanceReview.objects.get(id=id)
        review.delete()
        return Response({'message': 'Performance review deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except PerformanceReview.DoesNotExist:
        return Response({'error': 'Performance review not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def performance_review_detail(request, review_id):
    try:
        review = PerformanceReview.objects.get(id=review_id)
        serializer = PerformanceReviewSerializer(review)
        return Response(serializer.data)
    except PerformanceReview.DoesNotExist:
        return Response({'error': 'Performance review not found'}, status=status.HTTP_404_NOT_FOUND)

# Update a specific performance review by ID
@api_view(['PUT'])
def update_performance_review(request, review_id):
    try:
        review = PerformanceReview.objects.get(id=review_id)
        data = request.data
        serializer = PerformanceReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except PerformanceReview.DoesNotExist:
        return Response({'error': 'Performance review not found'}, status=status.HTTP_404_NOT_FOUND)

# Delete a specific performance review by ID

    
#################################




@api_view(['POST'])
def create_goal(request):
    """
    Create a new goal for an employee.
    """
    employee_id = request.data.get('employee_id')
    goal_text = request.data.get('goal_text')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')

    # Validate employee existence
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    # Create the goal
    goal = Goal.objects.create(
        employee=employee,
        goal_text=goal_text,
        start_date=start_date,
        end_date=end_date
    )

    serializer = GoalSerializer(goal)
    return Response(serializer.data, status=status.HTTP_201_CREATED)




@api_view(['GET'])
def goal_list(request):
    """
    Retrieve a list of all goals.
    """
    try:
        # Attempt to fetch all performance reviews
        goal = Goal.objects.all()
        serializer = GoalSerializer(goal, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Goal.DoesNotExist:
        # Handle case where the PerformanceReview model does not exist
        return Response(
            {"error": "No GOALS found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        # Handle any other unexpected exceptions
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Retrieve a specific goal by ID
@api_view(['GET'])
def goal_detail(request, goal_id):
    """
    Retrieve a specific goal by its ID.
    """
    try:
        goal = Goal.objects.get(id=goal_id)
        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Goal.DoesNotExist:
        return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

# Update a specific goal by ID
@api_view(['PUT'])
def update_goal(request, goal_id):
    """
    Update a specific goal by its ID.
    """
    try:
        goal = Goal.objects.get(id=goal_id)
        data = request.data
        serializer = GoalSerializer(goal, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Goal.DoesNotExist:
        return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

# Delete a specific goal by ID
@api_view(['DELETE'])
def delete_goal(request, id):
    """
    Delete a specific goal by its ID.
    """
    try:
        goal = Goal.objects.get(id=id)
        goal.delete()
        return Response({"message": "Goal deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Goal.DoesNotExist:
        return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)


########################################################

@api_view(['POST'])
def create_feedback(request):
    """
    Create a new feedback entry.
    """
    from_manager_id = request.data.get('from_manager_id')
    to_employee_id = request.data.get('to_employee_id')
    comments = request.data.get('comments')

    try:
        from_manager = Manager.objects.get(manager_id=from_manager_id)
        to_employee = Employee.objects.get(employee_id=to_employee_id)

        feedback = Feedback.objects.create(
            from_manager=from_manager,
            to_employee=to_employee,
            feedback_date=date.today(),
            comments=comments
        )

        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found"}, status=status.HTTP_404_NOT_FOUND)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def feedback_list(request):
    """
    Retrieve a list of all feedbacks.
    """
    try:
        # Attempt to fetch all performance reviews
        feedback = Feedback.objects.all()
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Feedback.DoesNotExist:
        # Handle case where the PerformanceReview model does not exist
        return Response(
            {"error": "No feedback found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        # Handle any other unexpected exceptions
        return Response(
            {"error": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Retrieve a specific feedback by ID
@api_view(['GET'])
def feedback_detail(request, feedback_id):
    """
    Retrieve a specific feedback entry by its ID.
    """
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        serializer = FeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

# Update a specific feedback entry by ID
@api_view(['PUT'])
def employee_update_feedback(request, feedback_id):
    """
    Update a specific feedback entry by its ID.
    """
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        data = request.data
        serializer = FeedbackSerializer(feedback, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

# Delete a specific feedback entry by ID
@api_view(['DELETE'])
def admin_delete_employee_feedback(request,feedback_id):
    """
    Delete a specific feedback entry by its ID.
    """
    try:
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.delete()
        return Response({"message": "Feedback deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    except Feedback.DoesNotExist:
        return Response({"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND)

###################################################

@api_view(['GET'])
def kpi_dashboard(request):
    """
    Retrieve the KPI dashboard data.
    """
    # Example data that might be shown in the KPI dashboard
    kpi_data = {
        'total_tasks': 120,
        'completed_tasks': 85,
        'pending_tasks': 35,
        'employee_performance': [
            {'employee_id': 1, 'employee_name': 'John Doe', 'tasks_completed': 45},
            {'employee_id': 2, 'employee_name': 'Jane Smith', 'tasks_completed': 40},
            {'employee_id': 3, 'employee_name': 'Jim Beam', 'tasks_completed': 35}
        ],
        'average_score': 8.5
    }
    
    return Response(kpi_data)



@api_view(['GET']) #added
def kpi_dashboard_detail(request, employee_id):
    """
    Retrieve the KPI dashboard data for a specific employee by ID.
    """
    try:
        # Assuming Employee and Task models exist
        employee = Employee.objects.get(id=employee_id)

        # Example KPI data for the employee
        tasks_completed = Task.objects.filter(employee=employee, status='Completed').count()
        tasks_pending = Task.objects.filter(employee=employee, status='Pending').count()
        average_score = PerformanceReview.objects.filter(employee=employee).aggregate(avg_score=models.Avg('score'))['avg_score'] or 0

        kpi_data = {
            'employee_id': employee.id,
            'employee_name': employee.employee_name,
            'tasks_completed': tasks_completed,
            'tasks_pending': tasks_pending,
            'average_performance_score': average_score
        }

        return Response(kpi_data, status=200)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500) #added


 # Assuming you have task-related data



@api_view(['GET']) #added
def kpi_dashboard_employee_request(request):
    """
    Retrieve the KPI dashboard data for the logged-in employee.
    """
    try:
        # Assuming the user is authenticated and linked to an Employee object
        user = request.user
        if not hasattr(user, 'employee'):
            return Response({'error': 'No employee profile associated with this user'}, status=404)
        
        employee = user.employee

        # Example employee KPI data (replace with actual logic as needed)
        tasks_completed = Task.objects.filter(employee=employee, status='Completed').count()
        tasks_in_progress = Task.objects.filter(employee=employee, status='In Progress').count()

        kpi_data = {
            'employee_name': employee.employee_name,
            'tasks_completed': tasks_completed,
            'tasks_in_progress': tasks_in_progress,
            'average_performance_score': 8.5  # Placeholder score
        }
        
        return Response(kpi_data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500) #added




@api_view(['GET'])
def kpi_dashboard_employee(request, employee_id):
    """
    Retrieve the employee-specific KPI dashboard data.
    """
    try:
        employee = Employee.objects.get(employee_id=employee_id)

        # Example employee KPI data (replace with actual logic as needed)
        tasks_completed = Task.objects.filter(employee=employee, status='Completed').count()
        tasks_in_progress = Task.objects.filter(employee=employee, status='In Progress').count()

        kpi_data = {
            'employee_name': employee.employee_name,
            'tasks_completed': tasks_completed,
            'tasks_in_progress': tasks_in_progress,
            'average_performance_score': 8.5  # Placeholder score
        }
        
        return Response(kpi_data)

    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)  
    
 # Assuming you need manager data for the admin dashboard

@api_view(['GET'])
def kpi_dashboard_admin(request):
    """
    Retrieve the admin-specific KPI dashboard data.
    This can include aggregated data like task completion stats, active managers, etc.
    """
    try:
        # Example aggregated data (adjust logic based on actual requirements)
        total_tasks = Task.objects.count()
        total_completed_tasks = Task.objects.filter(status='Completed').count()
        total_active_managers = Manager.objects.filter(is_active=True).count()

        kpi_data = {
            'total_tasks': total_tasks,
            'total_completed_tasks': total_completed_tasks,
            'total_active_managers': total_active_managers,
            'average_task_completion_time': '2 days',  # Placeholder value
            'pending_tasks': total_tasks - total_completed_tasks
        }

        return Response(kpi_data)

    except Exception as e:
        return Response({'error': str(e)}, status=500)
    


@api_view(['GET']) #added
def kpi_detail_task(request, task_id):
    """
    Retrieve specific KPI details for a task by its ID.
    Path Parameter:
    - task_id (required): ID of the task to retrieve KPI data for.
    """
    try:
        task = Task.objects.get(id=task_id)
        kpi_data = {
            'task_id': task.id,
            'task_name': task.name,
            'status': task.status,
            'assigned_to': task.assigned_to.username if task.assigned_to else "Unassigned",
            'completion_time': task.completion_time,  # Assuming this is a field in the Task model
            'is_overdue': task.is_overdue(),  # Assuming this is a method in the Task model
        }

        return Response(kpi_data, status=200)

    except Task.DoesNotExist:
        return Response({'error': f'Task with ID {task_id} not found.'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500) #added



@api_view(['GET'])
def performance_review_list_employee(request, employee_name):
    # Filter reviews for the employee
    reviews = PerformanceReview.objects.filter(employee__username=employee_name)
    
    # Serialize the data
    serializer = PerformanceReviewSerializer(reviews, many=True)
    
    # Return serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET'])  #added
def performance_review_list_request(request):
    """
    Retrieve the performance reviews for the logged-in employee.
    """
    try:
        # Ensure the logged-in user is associated with an Employee profile
        user = request.user
        if not hasattr(user, 'employee'):
            return Response({'error': 'No employee profile associated with this user'}, status=404)
        
        # Get the logged-in employee's performance reviews
        employee = user.employee
        reviews = PerformanceReview.objects.filter(employee=employee)
        
        # Serialize the performance reviews
        serializer = PerformanceReviewSerializer(reviews, many=True)
        
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500) #added


@api_view(['GET'])
def view_goal_employee(request, employee_name):
    # Filter goals for the employee
    goals = Goal.objects.filter(employee__username=employee_name)
    
    # Serialize the data
    serializer = GoalSerializer(goals, many=True)
    
    # Return serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET']) #added
def view_goal_employee_request(request):
    """
    Retrieve the goals for the logged-in employee.
    """
    try:
        # Ensure the logged-in user is associated with an Employee profile
        user = request.user
        if not hasattr(user, 'employee'):
            return Response({'error': 'No employee profile associated with this user'}, status=404)
        
        # Get the logged-in employee's goals
        employee = user.employee
        goals = Goal.objects.filter(employee=employee)
        
        # Serialize the goals
        serializer = GoalSerializer(goals, many=True)
        
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500) #added

##########################################3
@api_view(['GET'])
def view_feedback_employee(request, id):
    # Filter feedbacks for the employee
    feedbacks = Feedback.objects.filter(to_employee__employee_id=id)
    
    # Serialize the data
    serializer = FeedbackSerializer(feedbacks, many=True)
    
    # Return serialized data as a JSON response
    return Response(serializer.data)

@api_view(['GET']) #added
def view_feedback_employee_request(request):
    """
    Retrieve the feedback for the logged-in employee.
    """
    try:
        # Ensure the logged-in user is associated with an Employee profile
        user = request.user
        if not hasattr(user, 'employee'):
            return Response({'error': 'No employee profile associated with this user'}, status=404)
        
        # Get the logged-in employee's feedback
        employee = user.employee
        feedbacks = Feedback.objects.filter(to_employee=employee)
        
        # Serialize the feedbacks
        serializer = FeedbackSerializer(feedbacks, many=True)
        
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500) #added




#admin




# Create performance review for a manager

#################################################

@api_view(['POST'])
def create_performance_review_manager(request):
    if request.method == 'POST':
        manager_id = request.data.get('manager')
        comments = request.data.get('comments')
        review_date = request.data.get('review_date')
        score = request.data.get('score')

        # Check if all required fields are provided
        if not manager_id or not comments or not review_date or not score:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the manager object
            manager = Manager.objects.get(manager_id=manager_id)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Create the performance review for the manager
            review = ManagerPerformanceReview(
                manager=manager,
                review_date=review_date,  # Automatically set the current datetime
                comments=comments,
                score=score
            )
            review.save()

            # Serialize the review data and return it as a response
            serializer = ManagerPerformanceReviewSerializer(review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


# Update a specific performance review by ID
@api_view(['PUT'])
def update_performance_review_manager(request, review_id):
    """
    Update a specific performance review for a manager by ID.
    """
    try:
        review = ManagerPerformanceReview.objects.get(id=review_id)
        data = request.data
        serializer = ManagerPerformanceReviewSerializer(review, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ManagerPerformanceReview.DoesNotExist:
        return Response({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_performance_reviews_for_manager(request, manager_id):
    """
    Get all performance reviews for a specific manager by manager ID.
    """
    try:
        # Get the manager object
        manager = Manager.objects.get(id=manager_id)
        
        # Get all performance reviews for this manager
        reviews = ManagerPerformanceReview.objects.filter(manager=manager)
        
        # Serialize the review data and return as a response
        serializer = ManagerPerformanceReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_performance_review_by_id(request, review_id):
    """
    Get a particular performance review by its unique ID.
    """
    try:
        # Get the performance review by ID
        review = ManagerPerformanceReview.objects.get(id=review_id)
        
        # Serialize the review data and return as a response
        serializer = ManagerPerformanceReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ManagerPerformanceReview.DoesNotExist:
        return Response({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_performance_review_all(request):
    """
    Retrieve a list of all manager performance reviews.
    """
    try:
        # Fetch all performance reviews
        reviews = ManagerPerformanceReview.objects.all()
        serializer = ManagerPerformanceReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DatabaseError as db_error:
        # Handle database-related errors
        return Response(
            {"error": "Database error occurred.", "details": str(db_error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        # Handle other general exceptions
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )   
    

@api_view(['GET'])#added
def performance_review_manager_request(request):
    """
    Retrieve the performance reviews for the logged-in manager.
    """
    try:
        # Ensure the logged-in user is associated with a Manager profile
        user = request.user
        if not hasattr(user, 'manager'):
            return Response({'error': 'No manager profile associated with this user'}, status=404)
        
        # Get the logged-in manager's performance reviews
        manager = user.manager
        reviews = ManagerPerformanceReview.objects.filter(manager=manager)
        
        # Serialize the reviews
        serializer = ManagerPerformanceReviewSerializer(reviews, many=True)
        
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({'error': str(e)}, status=500) #added
    

    


# Delete a specific performance review by ID
@api_view(['DELETE'])
def delete_performance_review_manager(request, id):
    """
    Delete a specific performance review for a manager by ID.
    """
    try:
        review = ManagerPerformanceReview.objects.get(id=id)
        review.delete()
        return Response({'message': 'Review deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
    except ManagerPerformanceReview.DoesNotExist:
        return Response({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    #####################################
    

@api_view(['GET'])
def view_manager_reviews(request):
    reviews = ManagerPerformanceReview.objects.all()
    if not reviews:
        return Response({"message": "No performance reviews found."}, status=status.HTTP_200_OK)

    serializer = ManagerPerformanceReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) #added
def get_manager_review_by_id(request, review_id):
    """
    Retrieve a specific performance review entry for a manager by review ID.
    Path Parameter:
    - review_id (required): ID of the manager's performance review to retrieve.
    """
    try:
        review = ManagerPerformanceReview.objects.get(id=review_id)
    except ManagerPerformanceReview.DoesNotExist:
        return Response({"message": f"Performance review with ID {review_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerPerformanceReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK) #added
    

##############################################################################

# Create goal setting for a manager
# views.py


@api_view(['POST'])
def create_goal_manager(request):
    if request.method == 'POST':
        serializer = ManagerGoalSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the manager exists
            try:
                manager = Manager.objects.get(id=request.data['manager'])
            except Manager.DoesNotExist:
                return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

            # Save the goal
            serializer.save(manager=manager)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PUT'])
def update_manager_goal(request, goal_id):
    """
    API endpoint to update an existing manager goal.
    """
    try:
        goal = ManagerGoal.objects.get(id=goal_id)
    except ManagerGoal.DoesNotExist:
        return Response({"error": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)

    # Convert `is_completed` from string to boolean if needed
    if "is_completed" in request.data:
        if isinstance(request.data["is_completed"], str):
            request.data["is_completed"] = request.data["is_completed"].lower() == "true"

    # Update fields with the provided data from the request
    serializer = ManagerGoalSerializer(goal, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_manager_goal(request,id):
    """
    API endpoint to delete a specific manager goal.
    """
    try:
        manager_goal = ManagerGoal.objects.get(id=id)
    except ManagerGoal.DoesNotExist:
        return Response({"error": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)

    manager_goal.delete()
    return Response({"message": "Goal deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_manager_goal(request, goal_id):
    """
    API endpoint to retrieve a specific manager goal by its ID.
    """
    try:
        manager_goal = ManagerGoal.objects.get(id=goal_id)
    except ManagerGoal.DoesNotExist:
        return Response({"error": "Goal not found."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the goal data
    serializer = ManagerGoalSerializer(manager_goal)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_manager_goals(request):
    """
    API endpoint to retrieve all goals for a specific manager.
    """
    manager_id = request.query_params.get('manager_id')

    if not manager_id:
        return Response({"error": "You must provide the manager_id as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(id=manager_id)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve all goals for the manager
    manager_goals = ManagerGoal.objects.filter(manager=manager)

    # Serialize the data
    serializer = ManagerGoalSerializer(manager_goals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_manager_goal_all(request):
    """
    Retrieve a list of all manager performance reviews.
    """
    try:
        # Fetch all performance reviews
        goal = ManagerGoal.objects.all()
        serializer = ManagerGoalSerializer(goal, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except DatabaseError as db_error:
        # Handle database-related errors
        return Response(
            {"error": "Database error occurred.", "details": str(db_error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        # Handle other general exceptions
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )   
    

# views.py

@api_view(['POST'])
def create_feedback_manager(request):
    if request.method == 'POST':
        to_manager = request.data.get('to_manager')
        comments = request.data.get('comments')
        feedback_date = request.data.get('feedback_date')

        # Check if all required fields are provided
        if not to_manager or not comments or not feedback_date:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get the manager object
            to_manager = Manager.objects.get(id=to_manager)
        except Manager.DoesNotExist:
            return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Create the performance review for the manager
            Feedback = ManagerFeedback(
                to_manager=to_manager,
                # Automatically set the current datetime
                comments=comments,
                feedback_date=feedback_date
            )
            Feedback.save()

            # Serialize the review data and return it as a response
            serializer = ManagerFeedbackSerializer(Feedback)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def view_manager_feedbacks(request):
    feedback = ManagerFeedback.objects.all()
    if not feedback:
        return Response({"message": "No feedback found."}, status=status.HTTP_200_OK)

    serializer = ManagerFeedbackSerializer(feedback, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)    
    
@api_view(['PUT'])
def update_manager_feedback(request, id):
    """
    API endpoint to update an existing manager feedback.
    """
    try:
        feedback = ManagerFeedback.objects.get(id=id)
    except ManagerFeedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_200_OK)

    # Update fields with the provided data from the request
    serializer = ManagerFeedbackSerializer(feedback, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_manager_feedback(request, id):
    """
    API endpoint to delete a specific manager feedback.
    """
    try:
        feedback = ManagerFeedback.objects.get(id=id)
    except ManagerFeedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    feedback.delete()
    return Response({"message": "Feedback deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['DELETE'])
def delete_admin_feedback(request, id):
    """
    API endpoint to delete a specific manager feedback.
    """
    try:
        feedback = OverallFeedback.objects.get(id=id)
    except OverallFeedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    feedback.delete()
    return Response({"message": "Feedback deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_manager_feedback(request, feedback_id):
    """
    API endpoint to retrieve a specific manager feedback by its ID.
    """
    try:
        feedback = ManagerFeedback.objects.get(id=feedback_id)
    except ManagerFeedback.DoesNotExist:
        return Response({"error": "Feedback not found."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the feedback data
    serializer = ManagerFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_all_manager_feedback(request):
    """
    API endpoint to retrieve all feedback for a specific manager.
    """
    manager_id = request.query_params.get('manager_id')

    if not manager_id:
        return Response({"error": "You must provide the manager_id as a query parameter."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(id=manager_id)
    except Manager.DoesNotExist:
        return Response({"error": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)

    # Retrieve all feedback for the manager
    feedback_list = ManagerFeedback.objects.filter(to_manager=manager)

    # Serialize the data
    serializer = ManagerFeedbackSerializer(feedback_list, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

     

# View for displaying Manager Performance Reviews
# views.py

# views.py

@api_view(['GET'])
def view_manager_goals(request):
    goals = ManagerGoal.objects.all()
    if not goals:
        return Response({"message": "No goals found."}, status=status.HTTP_200_OK)

    serializer = ManagerGoalSerializer(goals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) #added
def get_manager_goal_by_id(request, id):
    """
    Retrieve a specific goal entry for a manager by goal ID.
    Path Parameter:
    - goal_id (required): ID of the manager's goal to retrieve.
    """
    try:
        goal = ManagerGoal.objects.get(id=id)
    except ManagerGoal.DoesNotExist:
        return Response({"message": f"Goal with ID {id} not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerGoalSerializer(goal)
    return Response(serializer.data, status=status.HTTP_200_OK) #added
# views.py



# @api_view(['GET']) #added
# def get_manager_feedback_by_id(request, feedback_id):
#     """
#     Retrieve a specific feedback entry for a manager by feedback ID.
#     Path Parameter:
#     - feedback_id (required): ID of the manager's feedback to retrieve.
#     """
#     try:
#         feedback = ManagerFeedback.objects.get(id=feedback_id)
#     except ManagerFeedback.DoesNotExist:
#         return Response({"message": f"Feedback with ID {feedback_id} not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = ManagerFeedbackSerializer(feedback)
#     return Response(serializer.data, status=status.HTTP_200_OK) #added
# # views.py

@api_view(['GET'])
def view_create_performance_review_manager(request, manager_name):
    reviews = ManagerPerformanceReview.objects.filter(manager__username=manager_name)
    if not reviews:
        return Response({"message": f"No performance reviews found for manager {manager_name}."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerPerformanceReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) #added
def get_manager_performance_review_by_id(request, review_id):
    """
    Retrieve a specific performance review entry for a manager by review ID.
    Path Parameter:
    - review_id (required): ID of the manager's performance review to retrieve.
    """
    try:
        review = ManagerPerformanceReview.objects.get(id=review_id)
    except ManagerPerformanceReview.DoesNotExist:
        return Response({"message": f"Performance review with ID {review_id} not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerPerformanceReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK) #added
#############
# views.py

@api_view(['GET'])
def view_create_goal_manager(request, manager_name):
    goals = ManagerGoal.objects.filter(manager__username=manager_name)
    if not goals:
        return Response({"message": f"No goals found for manager {manager_name}."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerGoalSerializer(goals, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET']) #aaded
# def get_manager_goal_by_id(request, goal_id):
#     """
#     Retrieve a specific goal entry for a manager by goal ID.
#     Path Parameter:
#     - goal_id (required): ID of the manager's goal to retrieve.
#     """
#     try:
#         goal = ManagerGoal.objects.get(id=goal_id)
#     except ManagerGoal.DoesNotExist:
#         return Response({"message": f"Goal with ID {goal_id} not found."}, status=status.HTTP_404_NOT_FOUND)

#     serializer = ManagerGoalSerializer(goal)
#     return Response(serializer.data, status=status.HTTP_200_OK) #added
##################
# views.py

@api_view(['GET'])
def view_create_feedback_manager(request, manager_name):
    feedbacks = ManagerFeedback.objects.filter(to_manager__username=manager_name)
    if not feedbacks:
        return Response({"message": f"No feedback found for manager {manager_name}."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET']) #added
def get_manager_feedback_by_id(request, id):
    """
    Retrieve a specific feedback entry for a manager by feedback ID.
    Path Parameter:
    - feedback_id (required): ID of the feedback to retrieve.
    """
    try:
        feedback = ManagerFeedback.objects.get(id=id)
    except ManagerFeedback.DoesNotExist:
        return Response({"message": f"Feedback with ID {id} not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManagerFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_200_OK) #added



#feedback
# views.py


 # Assuming the `check_if_manager` function is placed in `utils.py`

@api_view(['GET'])
def feedback_form(request):
    # Check if the user is a manager or employee
    is_manager = check_if_manager(request.session.get('user'))  # You can replace with actual logic
    return Response({'is_manager': is_manager}, status=status.HTTP_200_OK)

@api_view(['GET']) #added
def get_feedback_form_by_id(request, user_id):
    """
    Retrieve feedback form details by user ID.
    This function checks if the user is a manager or employee and responds accordingly.
    Path Parameter:
    - user_id (required): ID of the user (manager or employee).
    """
    # Replace check_if_manager with your actual logic for identifying managers
    is_manager = check_if_manager(user_id)  # Custom function to check if the user is a manager

    if is_manager:
        feedback_data = {
            'user_type': 'manager',
            'message': 'Feedback form for managers.',
        }
    else:
        # Assume user is an employee if not a manager
        feedback_data = {
            'user_type': 'employee',
            'message': 'Feedback form for employees.',
        }

    return Response(feedback_data, status=status.HTTP_200_OK) #added

######################################

@api_view(['POST'])
def submit_feedback(request):

    # if not isinstance(request, HttpRequest):
    #     return Response({'error': 'Invalid request type!'}, status=status.HTTP_400_BAD_REQUEST)
    
    comments = request.data.get('comments')
    if not comments:
        return Response({'error': 'Please provide feedback before submitting!'}, status=status.HTTP_400_BAD_REQUEST)

    username = request.data.get('name')  # Get the session user
    if not username:
        return Response({'error': 'User not authenticated!'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        if check_if_manager(username):
            manager = Manager.objects.get(username=username)
            feedback = OverallFeedback(manager=manager, comments=comments)
        else:
            employee = Employee.objects.get(username=username)
            feedback = OverallFeedback(employee=employee, comments=comments)

        feedback.save()
        return Response({'message': 'Feedback submitted successfully!'}, status=status.HTTP_201_CREATED)

    except (Manager.DoesNotExist, Employee.DoesNotExist):
        return Response({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
def update_feedback(request, feedback_id):
    """
    API endpoint to update an existing feedback's details (e.g., comments and review status).
    """
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)

    # Get updated data from the request
    comments = request.data.get('comments')
    is_reviewed = request.data.get('is_reviewed')

    # Update feedback details if provided
    if comments:
        feedback.comments = comments
    if is_reviewed is not None:
        feedback.is_reviewed = is_reviewed

    feedback.save()

    return Response({'message': 'Feedback updated successfully.'}, status=status.HTTP_200_OK)

# @api_view(['DELETE'])
# def delete_feedback(request, feedback_id):
#     """
#     API endpoint to delete a specific feedback by its ID.
#     """
#     feedback = get_object_or_404(OverallFeedback, id=feedback_id)
#     feedback.delete()

#     return Response({'message': 'Feedback deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_feedback_by_id(request, feedback_id):
    """
    API endpoint to retrieve a specific feedback by its ID.
    """
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)

    # Prepare the feedback data
    feedback_data = {
        'employee_id': feedback.employee.id if feedback.employee else None,
        'manager_id': feedback.manager.id if feedback.manager else None,
        'feedback_date': feedback.feedback_date,
        'comments': feedback.comments,
        'is_reviewed': feedback.is_reviewed,
    }

    return Response({'feedback': feedback_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_feedback_for_person(request):
    """
    API endpoint to retrieve all feedback for a specific employee or manager.
    """
    employee_id = request.query_params.get('employee_id')
    manager_id = request.query_params.get('manager_id')

    if not employee_id and not manager_id:
        return Response({'error': 'You must provide either employee_id or manager_id.'}, status=status.HTTP_400_BAD_REQUEST)

    feedbacks = None
    if employee_id:
        feedbacks = OverallFeedback.objects.filter(employee_id=employee_id)
    elif manager_id:
        feedbacks = OverallFeedback.objects.filter(manager_id=manager_id)

    if not feedbacks.exists():
        return Response({'error': 'No feedback found for the specified person.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare feedback data to be returned
    feedbacks_data = []
    for feedback in feedbacks:
        feedbacks_data.append({
            'employee_id': feedback.employee.id if feedback.employee else None,
            'manager_id': feedback.manager.id if feedback.manager else None,
            'feedback_date': feedback.feedback_date,
            'comments': feedback.comments,
            'is_reviewed': feedback.is_reviewed,
        })

    return Response({'feedbacks': feedbacks_data}, status=status.HTTP_200_OK)

###################################

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import OverallFeedback
from .serializers import OverallFeedbackSerializer
from django.db import DatabaseError
from rest_framework.serializers import ValidationError

@api_view(['GET'])
def admin_feedback_dashboard(request):
    try:
        # Fetch all feedbacks
        feedback = OverallFeedback.objects.all()
        
        # Check if feedbacks exist
        if not feedback:
            return Response({'message': 'No feedback found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize feedbacks
        serializer = OverallFeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except DatabaseError as db_error:
        # Handle database errors
        return Response(
            {'message': 'A database error occurred.', 'error': str(db_error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except ValidationError as validation_error:
        # Handle serialization or validation errors
        return Response(
            {'message': 'Data validation failed.', 'error': validation_error.detail},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        # Catch-all for any other unexpected errors
        return Response(
            {'message': 'An unexpected error occurred.', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])  #added
def get_feedback_by_id(request, feedback_id):
    """
    Retrieve a single feedback entry by its ID.
    URL Parameter:
    - feedback_id (required): ID of the feedback to retrieve.
    """
    try:
        feedback = OverallFeedback.objects.get(id=feedback_id)
    except OverallFeedback.DoesNotExist:
        return Response({'message': 'Feedback not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = OverallFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_200_OK)  #added

############################################

@api_view(['POST'])
def update_feedback_status(request, feedback_id):
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)
    feedback.is_reviewed = True
    feedback.save()
    return Response({'message': 'Feedback status updated to reviewed.'}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_feedback(request, feedback_id):
    """
    API endpoint to update an existing feedback's details (e.g., comments and review status).
    """
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)

    # Update feedback details from the request data
    comments = request.data.get('comments')
    is_reviewed = request.data.get('is_reviewed')

    # If provided, update comments and the review status
    if comments:
        feedback.comments = comments
    if is_reviewed is not None:
        feedback.is_reviewed = is_reviewed

    feedback.save()

    return Response({'message': 'Feedback updated successfully.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_overall_feedback(request, feedback_id):
    """
    API endpoint to delete a specific feedback by its ID.
    """
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)
    feedback.delete()

    return Response({'message': 'Feedback deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_feedback_by_id(request, feedback_id):
    """
    API endpoint to retrieve a specific feedback by its ID.
    """
    feedback = get_object_or_404(OverallFeedback, id=feedback_id)

    # Prepare the feedback data
    feedback_data = {
        'employee_id': feedback.employee.id if feedback.employee else None,
        'manager_id': feedback.manager.id if feedback.manager else None,
        'feedback_date': feedback.feedback_date,
        'comments': feedback.comments,
        'is_reviewed': feedback.is_reviewed,
    }

    return Response({'feedback': feedback_data}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_feedback_for_person(request):
    """
    API endpoint to retrieve all feedback for a specific employee or manager.
    """
    employee_id = request.query_params.get('employee_id')
    manager_id = request.query_params.get('manager_id')

    if not employee_id and not manager_id:
        return Response({'error': 'You must provide either employee_id or manager_id.'}, status=status.HTTP_400_BAD_REQUEST)

    feedbacks = None
    if employee_id:
        feedbacks = OverallFeedback.objects.filter(employee_id=employee_id)
    elif manager_id:
        feedbacks = OverallFeedback.objects.filter(manager_id=manager_id)

    if not feedbacks.exists():
        return Response({'error': 'No feedback found for the specified person.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare feedback data to be returned
    feedbacks_data = []
    for feedback in feedbacks:
        feedbacks_data.append({
            'employee_id': feedback.employee.id if feedback.employee else None,
            'manager_id': feedback.manager.id if feedback.manager else None,
            'feedback_date': feedback.feedback_date,
            'comments': feedback.comments,
            'is_reviewed': feedback.is_reviewed,
        })

    return Response({'feedbacks': feedbacks_data}, status=status.HTTP_200_OK)


###############################################

@api_view(['POST'])
def update_employee_goal(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    goal.is_completed = True  # Mark goal as completed
    goal.save()
    return Response({'message': 'Goal marked as completed.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_employee_goal(request, goal_id):
    """
    API endpoint to retrieve a specific employee's goal by its ID.
    """
    try:
        # Retrieve the goal by its ID
        goal = Goal.objects.get(id=goal_id)
    except Goal.DoesNotExist:
        return Response({'error': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the goal data to be returned
    goal_data = {
        'goal_text': goal.goal_text,
        'start_date': goal.start_date,
        'end_date': goal.end_date,
        'is_completed': goal.is_completed,
    }

    return Response({'goal': goal_data}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_employee_goal(request, goal_id):
    """
    API endpoint to update an employee's goal.
    """
    try:
        goal = Goal.objects.get(id=goal_id)
    except Goal.DoesNotExist:
        return Response({'error': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Get updated data from the request
    goal_text = request.data.get('goal_text')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    is_completed = request.data.get('is_completed')

    # Update the goal if new data is provided
    if goal_text:
        goal.goal_text = goal_text
    if start_date:
        goal.start_date = start_date
    if end_date:
        goal.end_date = end_date
    if is_completed is not None:  # Checking if `is_completed` is provided
        goal.is_completed = is_completed

    goal.save()

    return Response({'message': 'Goal updated successfully.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_employee_goal(request, goal_id):
    """
    API endpoint to delete an employee's goal by its ID.
    """
    try:
        goal = Goal.objects.get(id=goal_id)
    except Goal.DoesNotExist:
        return Response({'error': 'Goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    goal.delete()

    return Response({'message': 'Goal deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_all_employee_goals(request, employee_id):
    """
    API endpoint to retrieve all goals for a specific employee by their employee_id.
    """
    # Retrieve all goals for the specified employee
    employee_goals = Goal.objects.filter(employee_id=employee_id)

    if not employee_goals.exists():
        return Response({'error': 'No goals found for this employee.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the goal data to be returned
    goals_data = []
    for goal in employee_goals:
        goals_data.append({
            'goal_text': goal.goal_text,
            'start_date': goal.start_date,
            'end_date': goal.end_date,
            'is_completed': goal.is_completed,
        })

    return Response({'employee_goals': goals_data}, status=status.HTTP_200_OK)


#####################################

@api_view(['POST'])
def update_manager_goal(request, goal_id):
    manager_goal = get_object_or_404(ManagerGoal, id=goal_id)
    manager_goal.is_completed = True  # Mark goal as completed
    manager_goal.save()
    return Response({'message': 'Manager goal marked as completed.'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_goal(request, goal_id):
    """
    API endpoint to retrieve a manager goal by its ID.
    """
    try:
        manager_goal = ManagerGoal.objects.get(id=goal_id)
    except ManagerGoal.DoesNotExist:
        return Response({'error': 'Manager goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    goal_data = {
        'goal_text': manager_goal.goal_text,
        'start_date': manager_goal.start_date,
        'end_date': manager_goal.end_date,
        'is_completed': manager_goal.is_completed
    }

    return Response({'manager_goal': goal_data}, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_manager_goal(request, goal_id):
    """
    API endpoint to update an existing manager goal.
    """
    try:
        manager_goal = ManagerGoal.objects.get(id=goal_id)
    except ManagerGoal.DoesNotExist:
        return Response({'error': 'Manager goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    goal_text = request.data.get('goal_text')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    is_completed = request.data.get('is_completed')

    if goal_text:
        manager_goal.goal_text = goal_text
    if start_date:
        manager_goal.start_date = start_date
    if end_date:
        manager_goal.end_date = end_date
    if is_completed is not None:  # Checking if `is_completed` is provided
        manager_goal.is_completed = is_completed

    manager_goal.save()

    return Response({'message': 'Manager goal updated successfully.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_manager_goal(request, goal_id):
    """
    API endpoint to delete a manager goal by its ID.
    """
    try:
        manager_goal = ManagerGoal.objects.get(id=goal_id)
    except ManagerGoal.DoesNotExist:
        return Response({'error': 'Manager goal not found.'}, status=status.HTTP_404_NOT_FOUND)

    manager_goal.delete()

    return Response({'message': 'Manager goal deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_all_manager_goals(request, manager_id):
    """
    API endpoint to retrieve all goals for a specific manager by manager_id.
    """
    try:
        # Retrieve all goals for the specified manager
        manager_goals = ManagerGoal.objects.filter(manager_id=manager_id)
    except ManagerGoal.DoesNotExist:
        return Response({'error': 'No goals found for this manager.'}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the goal data to be returned
    goals_data = []
    for goal in manager_goals:
        goals_data.append({
            'goal_text': goal.goal_text,
            'start_date': goal.start_date,
            'end_date': goal.end_date,
            'is_completed': goal.is_completed,
        })

    return Response({'manager_goals': goals_data}, status=status.HTTP_200_OK)


################################################

def check_if_manager(username):
    """Helper function to check if a user is a manager."""
    return Manager.objects.filter(username=username).exists()

    
@api_view(['PUT'])
def update_manager(request, manager_id):
    """
    API endpoint to update a manager's details.
    """
    try:
        manager = Manager.objects.get(id=manager_id)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

    username = request.data.get('username')
    if username:
        manager.username = username

    # Add additional fields you want to update, like email, name, etc.
    manager.save()

    return Response({'message': 'Manager updated successfully.'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_manager(request, manager_id):
    """
    API endpoint to delete a manager.
    """
    try:
        manager = Manager.objects.get(id=manager_id)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

    manager.delete()
    return Response({'message': 'Manager deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def get_manager(request, manager_id):
    """
    API endpoint to get a manager's details.
    """
    try:
        manager = Manager.objects.get(id=manager_id)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found.'}, status=status.HTTP_404_NOT_FOUND)

    manager_data = {
        'id': manager.id,
        'username': manager.username,
        # Add additional manager fields as needed
    }

    return Response({'manager': manager_data}, status=status.HTTP_200_OK)


