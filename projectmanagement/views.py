import datetime
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from ess import settings
from projectmanagement.models import Project, Task, Role, TaskDocument,Team,employee_task,TaskEmpDocument,TaskLog
from authentication.models import Admin, Manager, Department, Shift, Employee, Location
from django.db.models import Sum,Count
from django.core.files.storage import FileSystemStorage
from .models import TrainingProgram, TrainingParticipation, Certification
from .forms import CertificationForm, TrainingProgramForm, ParticipationForm
from django.core.mail import send_mail
from django.utils import timezone  # Import timezone from django.utils
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import render
from .models import employee_task
import json
from django.contrib import messages 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TaskLog
from .serializers import TaskLogSerializer
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import employee_task
from .serializers import EmployeeTaskSerializer 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project, Task, employee_task
from .serializers import ProjectSerializer, TaskSerializer, EmployeeTaskSerializer 
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task, Manager
from .serializers import TaskSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task, Manager
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task, Manager
from .serializers import TaskSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Role
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Role
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Team, Project, Manager, Employee
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Team
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Team, Project, Manager, Employee
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Manager, Team
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import employee_task, Team, Manager
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import employee_task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import employee_task, Employee
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import employee_task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Manager, Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Task, TaskDocument
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import employee_task, TaskEmpDocument
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TaskDocument, TaskEmpDocument, employee_task, Task
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingProgram
from .serializers import TrainingProgramSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingParticipation
from .serializers import ParticipationSerializer  # Ensure you have this serializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TrainingProgram, TrainingParticipation
from .serializers import TrainingProgramSerializer, TrainingParticipationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingProgram
from .serializers import TrainingProgramSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingParticipation
from .serializers import TrainingParticipationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CertificationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Certification
from .serializers import CertificationSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import TrainingProgram, TrainingParticipation, Manager, Employee
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.utils.timezone import now
from datetime import timedelta
from .models import TaskLog
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from .models import TaskLog, Employee, Manager, Task, employee_task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Project, Task, employee_task, Manager
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Task, Project, Manager
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Role
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Team, Project, Manager, Employee
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Project
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TaskDocument, TaskEmpDocument
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import employee_task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TrainingProgram
from .serializers import TrainingProgramSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TrainingParticipation
from .serializers import TrainingParticipationSerializer
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Certification
from .serializers import CertificationSerializer
from .serializers import RoleSerializer
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count
from django.utils.timezone import now
from .models import TaskLog, Employee, Manager
from datetime import timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Employee, Manager
from django.utils import timezone
from authentication.models import Employee, Manager ,Supervisor
from kpi.models import PerformanceReview,Goal, Feedback,ManagerPerformanceReview,ManagerGoal,ManagerFeedback,OverallFeedback

@api_view(['POST'])
def emp_check_in(request):
    """
    Check-in an employee to a task.
    """
    # Check if there's already an active task without check-out time
    active_task = TaskLog.objects.filter(check_out_time__isnull=True).exists()
    if active_task:
        return Response({"detail": "You have already checked in to a task. Please check out before starting a new task."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Create a new TaskLog entry with the current check-in time
    task_log = TaskLog.objects.create(check_in_time=now())
    
    # Serialize the TaskLog object and return the response
    serializer = TaskLogSerializer(task_log)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def emp_check_out(request):
    """
    Check-out an employee from a task.
    """
    try:
        # Get the TaskLog with no check-out time
        task_log = TaskLog.objects.get(check_out_time__isnull=True)
    except ObjectDoesNotExist:
        return Response({"detail": "This task has already been checked out or was never checked in."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Set check-out time and calculate worked hours
    task_log.check_out_time = now()
    task_log.calculate_hours_worked()  # Calculate hours worked and update the entry
    task_log.save()

    # Serialize the TaskLog object and return the response
    serializer = TaskLogSerializer(task_log)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
def assigned_task(request):
    if request.method == 'GET':
        # Fetch tasks grouped by status
        statuses = ['not started', 'in progress', 'in review', 'completed']
        tasks_by_status = {}

        for status_name in statuses:
            tasks = employee_task.objects.filter(emp_taskstatus=status_name)
            serialized_tasks = EmployeeTaskSerializer(tasks, many=True)
            tasks_by_status[status_name.replace(' ', '_')] = serialized_tasks.data

        return Response(tasks_by_status, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update task status
        task_id = request.data.get('task_id')
        new_status = request.data.get('status')

        if not task_id or not new_status:
            return Response(
                {'success': False, 'error': 'Task ID and status are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = employee_task.objects.get(emptask_id=task_id)
            task.emp_taskstatus = new_status
            task.save()
            return Response(
                {'success': True, 'message': 'Task status updated successfully.'},
                status=status.HTTP_200_OK
            )
        except employee_task.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Task not found.'},
                status=status.HTTP_404_NOT_FOUND
            )




@api_view(['GET'])
def assigned_task_by_id(request, task_id):
    """
    GET request to fetch a specific task by its ID.
    """
    try:
        # Fetch the task by its ID
        task = employee_task.objects.get(id=task_id)

        # Serialize the task data
        task_serializer = EmployeeTaskSerializer(task)

        # Return the task as JSON
        return Response(task_serializer.data, status=200)

    except employee_task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)



@api_view(['POST', 'GET'])
def assigned_manager_task(request):
    if request.method == 'POST':
        # Handle POST request to update task status
        data = request.data
        ptask_id = data.get('task_id')
        new_status = data.get('status')

        try:
            task = Task.objects.get(id=ptask_id)
            task.status = new_status
            task.save()
            return Response({'success': True})
        except Task.DoesNotExist:
            return Response({'success': False, 'error': 'Task not found'}, status=404)
    
    elif request.method == 'GET':
        # Handle GET request to fetch tasks by status
        not_started_projects = Task.objects.filter(status='not started')
        in_progress_projects = Task.objects.filter(status='in progress')
        in_review_projects = Task.objects.filter(status='in review')
        completed_projects = Task.objects.filter(status='completed')

        # Serialize the task data
        not_started_serializer = TaskSerializer(not_started_projects, many=True)
        in_progress_serializer = TaskSerializer(in_progress_projects, many=True)
        in_review_serializer = TaskSerializer(in_review_projects, many=True)
        completed_serializer = TaskSerializer(completed_projects, many=True)

        # Return the tasks as JSON
        return Response({
            'not_started_tasks': not_started_serializer.data,
            'in_progress_tasks': in_progress_serializer.data,
            'in_review_tasks': in_review_serializer.data,
            'completed_tasks': completed_serializer.data,
        })

@api_view(['PUT'])
def update_task_status(request):
    # Handle PUT request to update task status
    data = request.data
    task_id = data.get('task_id')
    new_status = data.get('status')

    # try:
    task = Task.objects.get(task_id=task_id)
    task.status = new_status
    task.save()
    return Response({'success': True, 'message': 'Task status updated successfully'})
    # except Task.DoesNotExist:
    #     return Response({'success': False, 'error': 'Task not found'}, status=404) 


@api_view(['PUT'])
def update_employeetask_status(request):
    # Handle PUT request to update task status
    data = request.data
    emptask_id = data.get('emptask_id')
    new_status = data.get('emp_taskstatus')

    # try:
    task = employee_task.objects.get(id=emptask_id)
    task.emp_taskstatus = new_status
    task.save()
    return Response({'success': True, 'message': 'Task status updated successfully'})


@api_view(['PUT'])
def update_project_status(request):
    # Handle PUT request to update task status
    data = request.data
    project_id = data.get('project_id')
    new_status = data.get('project_status')

    # try:
    task = Project.objects.get(project_id=project_id)
    task.project_status = new_status
    task.save()
    return Response({'success': True, 'message': 'Task status updated successfully'})


@api_view(['GET'])
def get_tasks(request):
    # Get all projects with selected fields
    tasks = Task.objects.all().values('task_id', 'manager', 'start_date', 'deadline', 'status','project_name',' priority','description','task_name')
    task_list = list(task_list)  # Convert QuerySet to list
    
    return Response(task_list)

@api_view(['GET'])
def assigned_manager_task_by_id(request, task_id):
    """
    GET request to fetch a specific task by its ID for the manager.
    """
    try:
        # Fetch the task by its ID
        task = Task.objects.get(id=task_id)

        # Serialize the task data
        task_serializer = TaskSerializer(task)

        # Return the task as JSON
        return Response(task_serializer.data, status=200)

    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=404)
    
# @api_view(['POST'])
# def create_project(request):
#     if request.method == 'POST':
#         # Extract project data from the request body
#         project_data = request.data
        
#         # Create a new Project instance and populate fields
#         serializer = ProjectSerializer(data=project_data)
        
#         if serializer.is_valid():
#             serializer.save()  # Save the project instance
#             return Response({'success': True, 'message': 'Project created successfully!'}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_project(request):
    if request.method == 'POST':
        project_data = request.data.copy()

        # Remove project_id from incoming data if present
        project_data.pop('project_id', None)  # Let the model generate it

        serializer = ProjectSerializer(data=project_data)

        if serializer.is_valid():
            serializer.save()  # project_id will be set automatically in model.save()
            return Response({'success': True, 'message': 'Project created successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_project(request, id):
    try:
        project = Project.objects.get(project_id=id)
    except Project.DoesNotExist:
        return Response({'success': False, 'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update project with data from the request
    if request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data)

        if serializer.is_valid():
            serializer.save()  # Save the updated project instance
            return Response({'success': True, 'message': 'Project updated successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def show_project_status(request, project_id):
    try:
        project = Project.objects.get(project_id=project_id)
    except Project.DoesNotExist:
        return Response({'success': False, 'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    tasks = Task.objects.filter(project_name=project.name)
    emptasks = employee_task.objects.filter(team_project_name=project.name)
    
    # Serialize the data
    project_serializer = ProjectSerializer(project)
    tasks_serializer = TaskSerializer(tasks, many=True)
    emptasks_serializer = EmployeeTaskSerializer(emptasks, many=True)
    
    return Response({
        'project': project_serializer.data,
        'tasks': tasks_serializer.data,
        'emptasks': emptasks_serializer.data
    }, status=status.HTTP_200_OK)
    
    #NEW FUNCTION
    
from rest_framework.exceptions import APIException
from django.db import DatabaseError

@api_view(['GET'])
def get_project_by_id(request, project_id):
    """
    Retrieve details of a specific project by its ID.
    Includes exception handling for invalid or non-existent IDs.
    """
    try:
        # Retrieve the project from the database by its ID
        project = Project.objects.get(project_id=project_id)

        # Serialize the project data
        project_serializer = ProjectSerializer(project)

        # Return a successful response with the project details
        return Response({
            'success': True,
            'project': project_serializer.data
        }, status=status.HTTP_200_OK)

    except ObjectDoesNotExist:
        # Handle case when the project with the given ID does not exist
        return Response({
            'success': False,
            'error': f'Project with ID {project_id} does not exist.'
        }, status=status.HTTP_404_NOT_FOUND)

    except APIException as api_error:
        # Handle API-related exceptions
        return Response({
            'success': False,
            'error': 'An API error occurred.',
            'details': api_error.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Handle any other unexpected errors
        return Response({
            'success': False,
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def list_all_projects(request):
    """
    Retrieve a list of all projects with their details.
    Includes exception handling for unexpected errors.
    """
    try:
        # Retrieve all projects from the database
        projects = Project.objects.all()

        # Serialize the projects data
        projects_serializer = ProjectSerializer(projects, many=True)
        
        # Return a successful response
        return Response({
            'success': True,
            'projects': projects_serializer.data
        }, status=status.HTTP_200_OK)
    
    except DatabaseError as db_error:
        # Handle database-related errors
        return Response({
            'success': False,
            'error': 'A database error occurred.',
            'details': str(db_error)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except APIException as api_error:
        # Handle API-related exceptions
        return Response({
            'success': False,
            'error': 'An API error occurred.',
            'details': api_error.detail
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        return Response({
            'success': False,
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['DELETE'])
def delete_project(request, id):
    try:
        # Try to retrieve the project by its ID
        project = Project.objects.get(project_id=id)
        project.delete()  # Delete the project
        return Response({'success': True, 'message': 'Project deleted successfully!'}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'success': False, 'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        try:
            # Get the manager field from the request
            manager_id = request.data.get('manager')
            
            # Convert manager_id to integer if it is a string
            if isinstance(manager_id, str):
                try:
                    manager_id = int(manager_id)
                except ValueError:
                    return Response(
                        {'success': False, 'errors': {'manager': ['Manager must be an integer.']}},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Validate that the manager exists
            manager = Manager.objects.get(id=manager_id)
            
            # Save the task with the valid manager
            serializer.save(manager=manager)
            return Response({'success': True, 'message': 'Task created successfully!'}, status=status.HTTP_201_CREATED)
        
        except Manager.DoesNotExist:
            return Response(
                {'success': False, 'errors': {'manager': ['Manager does not exist.']}},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def list_all_task(request):
    """
    Retrieve a list of all task with their details.
    Includes exception handling for unexpected errors.
    """
    try:
        # Retrieve all projects from the database
        task = Task.objects.all()

        # Serialize the projects data
        task_serializer = TaskSerializer(task, many=True)
        
        # Return a successful response
        return Response({
            'success': True,
            'task': task_serializer.data
        }, status=status.HTTP_200_OK)
    
    except DatabaseError as db_error:
        # Handle database-related errors
        return Response({
            'success': False,
            'error': 'A database error occurred.',
            'details': str(db_error)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except APIException as api_error:
        # Handle API-related exceptions
        return Response({
            'success': False,
            'error': 'An API error occurred.',
            'details': api_error.detail
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Handle any other unexpected errors
        return Response({
            'success': False,
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    


@api_view(['DELETE'])
def delete_task(request, id):
    try:
        task = get_object_or_404(Task, task_id=id)
        task.delete()
        return Response({"success": True, "message": "Task deleted successfully!"}, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({"success": False, "error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def edit_task(request, id):
    # Get the task object
    task = get_object_or_404(Task, task_id=id)

    # Create a serializer instance with the existing task data
    serializer = TaskSerializer(task, data=request.data, partial=True)  # partial=True allows partial updates

    if serializer.is_valid():
        # Save the updated task
        serializer.save()
        return Response({"success": True, "message": "Task updated successfully!"}, status=status.HTTP_200_OK)
    else:
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def show_my_tasks(request):
    # Get the manager's ID from the request body (assuming the manager's ID is passed in the request)
    user_id = request.data.get('user_id')  # Get the user_id from the POST request body

    if not user_id:
        return Response({"success": False, "error": "user_id is required"}, status=400)

    try:
        # Fetch the manager object based on the provided user_id
        manager = Manager.objects.get(manager_id=user_id)
    except Manager.DoesNotExist:
        return Response({"success": False, "error": "Manager not found"}, status=404)

    # Get tasks where this manager is assigned
    tasks = Task.objects.filter(manager=manager)

    # Serialize the tasks
    serializer = TaskSerializer(tasks, many=True)

    return Response({"success": True, "tasks": serializer.data}, status=200)

#NEW FUNCTION

@api_view(['GET'])
def get_task_details(request, task_id):
    """
    Retrieve details of a specific task by its ID.
    """
    try:
        task = Task.objects.get(task_id=task_id)
        serializer = TaskSerializer(task)
        return Response({"success": True, "task": serializer.data}, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({"success": False, "error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def create_role(request):
    # Check if role_id and role_name are present in the POST request body
    prole_id = request.data.get('role_id')
    prole_name = request.data.get('role_name')

    if not prole_id or not prole_name:
        return Response({"success": False, "error": "role_id and role_name are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Create and save the new Role object
    role = Role(role_id=prole_id, role_name=prole_name)
    role.save()

    return Response({"success": True, "message": "Role created successfully!"}, status=status.HTTP_201_CREATED)

# Delete Role API View
@api_view(['DELETE'])
def delete_role(request, id):
    try:
        role = get_object_or_404(Role, id=id)
        role.delete()
        return Response({"success": True, "message": "Role deleted successfully!"}, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({"success": False, "error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

# Edit Role API View
@api_view(['PUT'])
def edit_role(request, id):
    try:
        role = get_object_or_404(Role, id=id)
        role.role_id = request.data.get('role_id', role.role_id)  # Use provided role_id or keep existing
        role.role_name = request.data.get('role_name', role.role_name)  # Use provided role_name or keep existing
        
        role.save()
        return Response({"success": True, "message": "Role updated successfully!"}, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({"success": False, "error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

from django.db import DatabaseError    
    
@api_view(['GET'])
def list_roles(request):
    """
    Retrieve a list of all roles with exception handling.
    """
    try:
        # Fetch all roles from the database
        roles = Role.objects.all()
        
        # Serialize the roles
        serializer = RoleSerializer(roles, many=True)
        
        # Return a successful response
        return Response({"success": True, "roles": serializer.data}, status=status.HTTP_200_OK)
    except DatabaseError as db_error:
        # Handle database-related exceptions
        return Response(
            {"success": False, "error": "Database error occurred", "details": str(db_error)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        # Handle unexpected exceptions
        return Response(
            {"success": False, "error": "An unexpected error occurred", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_role_by_id(request, id):
    """
    Retrieve a specific role by its ID.
    """
    try:
        role = Role.objects.get(id=id)
        serializer = RoleSerializer(role)  # Serialize the role
        return Response({"success": True, "role": serializer.data}, status=status.HTTP_200_OK)
    except Role.DoesNotExist:
        return Response({"success": False, "error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)




# @api_view(['POST'])
# def create_team(request):
#     try:
#         team_name = request.data['team_name']
#         project_name = request.data['project_name']
#         team_task = request.data['team_task']
#         manager_name = request.data['manager']
#         team_leader_username = request.data['team_leader']
#         members_usernames = request.data['members']

#         # Fetch related objects using correct models and fields
#         project = get_object_or_404(Project, name=project_name)
#         manager = get_object_or_404(Manager, manager_name=manager_name)
#         team_leader = get_object_or_404(User, username=team_leader_username)  # Changed to User model
        
#         print("team_leader type:", type(team_leader))  # Should be <class 'yourapp.models.User'>
#         print("team_leader instance:", team_leader)
#         print("team_leader is User instance?", isinstance(team_leader, User))

#         # Create the team
#         team = Team(
#             team_name=team_name,
#             project=project,
#             team_task=team_task,
#             manager=manager,
#             team_leader=team_leader,
#         )
#         team.save()

#         # Fetch member User instances by username
#         member_objects = User.objects.filter(username__in=members_usernames)
#         if len(member_objects) != len(members_usernames):
#             missing_members = set(members_usernames) - set(member.username for member in member_objects)
#             return Response(
#                 {"success": False, "error": f"Some members not found: {', '.join(missing_members)}"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
#         team.members.set(member_objects)

#         return Response({"success": True, "message": "Team created successfully!"}, status=status.HTTP_201_CREATED)

#     except KeyError as e:
#         return Response({"success": False, "error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# July 10 ---------------------------------------------------------------------

@api_view(['DELETE'])
def delete_team(request, team_id):
    try:
        team = get_object_or_404(Team, team_id=team_id)
        team.delete()
        return Response({"success": True, "message": "Team deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def edit_team(request, team_id):
    try:
        # Get the team object or return 404 if it doesn't exist
        team = get_object_or_404(Team, team_id=team_id)

        # Extract the updated data from the request body
        team_name = request.data['team_name']
        project_name = request.data['project_name']
        team_task = request.data['team_task']
        manager_name = request.data['manager']
        team_leader_name = request.data['team_leader']
        members = request.data['members']
        team_id = request.data['team_id']

        # Fetch related objects based on new values
        project = get_object_or_404(Project, name=project_name)
        manager = get_object_or_404(Manager, username=manager_name)
        team_leader = get_object_or_404(Employee, username=team_leader_name)

        # Update team details
        team.team_name = team_name
        team.project = project
        team.team_task = team_task
        team.manager = manager
        team.team_leader = team_leader
        team.team_id = team_id
        team.save()

         # Update members to the team using .set()
        member_objects = Employee.objects.filter(username__in=members)
        if len(member_objects) != len(members):
            missing_members = set(members) - set(member.username for member in member_objects)
            return Response(
                {"success": False, "error": f"Some members not found: {', '.join(missing_members)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        team.members.set(member_objects)

        # Return success response
        return Response({"success": True, "message": "Team updated successfully!"}, status=status.HTTP_200_OK)

    except KeyError as e:
        return Response({"success": False, "error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Team, Manager
from .serializers import TeamSerializer

# @api_view(['GET'])
# def view_my_teams(request):
#     # try:
#         # Retrieve the manager's username from the session
#         manager_username = request.session.get('user')

#         if not manager_username:
#             return Response({"success": False, "message": "Manager not found in session."}, status=status.HTTP_400_BAD_REQUEST)

#         # Retrieve the manager object based on their username
#         manager = Manager.objects.get(username=manager_username)

#         # Get all teams managed by this manager
#         teams = Team.objects.filter(manager=manager)

#         # Serialize the teams including team members and team leader
#         team_data = [
#             {
#                 "team_id": team.team_id,
#                 "team_name": team.team_name,
#                 "project_name": team.project.name,
#                 "team_task": team.team_task,
#                 "manager": team.manager.username,
#                 "team_leader":team.team_leader.username,
#                 "members": [
#                     {"id": member.id, "employee_id":member.employee_id,"name":member.employee_name}
#                     for member in team.members.all()
#                 ]
#             }
#             for team in teams
#         ]

#         # Return the team data as JSON
#         return Response({"success": True, "teams": team_data}, status=status.HTTP_200_OK)


#######################################################previously also below portion is commented ###################


    # except Manager.DoesNotExist:
    #     return Response({"success": False, "message": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)
    # except Exception as e:
    #     return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    
    
@api_view(['GET'])
def get_team_by_id(request, team_id):
    """
    Retrieve details of a specific team by its team_id.
    """
    try:
        # Retrieve the team by team_id
        team = get_object_or_404(Team, team_id=team_id)

        # Serialize the team data (Assuming you have a serializer for the Team model)
        team_data = {
            "team_id": team.team_id,
            "team_name": team.team_name,
            "project_name": team.project.name,
            "manager": team.manager.username,
            "team_leader": team.team_leader.username,
            "members": [member.username for member in team.members.all()],
            "team_task": team.team_task
        }

        # Return the team data as JSON
        return Response({"success": True, "team": team_data}, status=status.HTTP_200_OK)

    except Team.DoesNotExist:
        return Response({"success": False, "message": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_teams(request):
    """
    Retrieve details of all teams.
    """
    try:
        # Retrieve all teams
        teams = Team.objects.all()

        # Serialize the data for all teams
        teams_data = []
        for team in teams:
            team_info = {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "project_name": team.project.name,
                "manager": team.manager.manager_name,
                "team_leader": team.team_leader.username,
                "members": [member.username for member in team.members.all()],
                "team_task": team.team_task
            }
            teams_data.append(team_info)

        # Return the serialized data as JSON
        return Response({"success": True, "teams": teams_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def assign_task_to_team_member(request):
    try:
        # Extract data from the request
        member = request.data.get('team_members')
        task_name = request.data.get('task_name')
        task_description = request.data.get('task_description')
        deadline = request.data.get('deadline')
        emptask_id = request.data.get('task_id')
        team_name=request.data.get('team_name')
        team_project_name=request.data.get('project_name')
        manager_id=request.data.get('manager_id')
        

        manager=Manager.objects.get(manager_id=manager_id)

        if not member or not task_name or not task_description or not deadline:
            return Response({"success": False, "message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new task
        emp_task = employee_task(
            task_name=task_name,
            task_description=task_description,
            assigned_to=member,
            deadline=deadline,
            emptask_id=emptask_id,
            team_name=team_name,
            team_project_name=team_project_name,
            manager=manager,
        )
        emp_task.save()

        return Response({"success": True, "message": "Task assigned to team member successfully!"}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def show_employee_tasks(request, user):
    if request.method == 'POST' and request.content_type == 'application/json':
        data = request.data
        task_id = data.get('task_id')
        new_status = data.get('status')

        try:
            task = employee_task.objects.get(id=task_id)
            task.emp_taskstatus = new_status
            task.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        except employee_task.DoesNotExist:
            return Response({'success': False, 'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'GET':
        # Fetch tasks by their status for the employee
        not_started_projects = employee_task.objects.filter(emp_taskstatus='not started', assigned_to=user)
        in_progress_projects = employee_task.objects.filter(emp_taskstatus='in progress', assigned_to=user)
        in_review_projects = employee_task.objects.filter(emp_taskstatus='in review', assigned_to=user)
        completed_projects = employee_task.objects.filter(emp_taskstatus='completed', assigned_to=user)

        # Structure the response
        context = {
            'not_started_projects': not_started_projects,
            'in_progress_projects': in_progress_projects,
            'in_review_projects': in_review_projects,
            'completed_projects': completed_projects,
        }

        return Response(context, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_employeetasks(request):
    # Get all projects with selected fields
    tasks = employee_task.objects.all()#.values('task_id', 'manager', 'start_date', 'deadline', 'status','project_name',' priority','description','task_name')
    serializer = EmployeeTaskSerializer(tasks, many=True)
    # task_list = list(tasks)  # Convert QuerySet to list
    
    return Response(serializer.data)
    
@api_view(['GET'])
def show_employee_task_by_id(request, user, task_id):
    """
    GET request to fetch a specific task by its ID for the employee.
    """
    try:
        # Fetch the task assigned to the employee by task_id
        task = employee_task.objects.get(id=task_id, assigned_to=user)

        # Prepare the response data
        task_data = {
            'task_id': task.id,
            'task_name': task.task_name,
            'task_description': task.task_description,
            'deadline': task.deadline,
            'status': task.emp_taskstatus
        }

        return Response({'task': task_data}, status=status.HTTP_200_OK)

    except employee_task.DoesNotExist:
        return Response({'error': 'Task not found or not assigned to this employee'}, status=status.HTTP_404_NOT_FOUND)

    


@api_view(['GET', 'POST'])
def show_assigned_manager_task(request):
    if request.method == 'POST' and request.content_type == 'application/json':
        data = request.data
        ptask_id = data.get('task_id')
        new_status = data.get('status')

        try:
            task = Task.objects.get(id=ptask_id)
            task.status = new_status
            task.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'success': False, 'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'GET':
        # Fetch tasks by their status for the manager
        not_started_projects = Task.objects.filter(status='not started')
        in_progress_projects = Task.objects.filter(status='in progress')
        in_review_projects = Task.objects.filter(status='in review')
        completed_projects = Task.objects.filter(status='completed')

        # Structure the response
        context = {
            'not_started_projects': not_started_projects,
            'in_progress_projects': in_progress_projects,
            'in_review_projects': in_review_projects,
            'completed_projects': completed_projects,
        }

        return Response(context, status=status.HTTP_200_OK)

@api_view(['GET'])
def show_task_by_id(request, task_id):
    """
    GET request to fetch a specific task by its ID for the manager.
    """
    try:
        # Fetch the task by its ID
        task = Task.objects.get(id=task_id)

        # Prepare the response data
        task_data = {
            'task_id': task.id,
            'task_name': task.task_name,
            'task_description': task.task_description,
            'deadline': task.deadline,
            'status': task.status,
            'assigned_to': task.assigned_to.name,  # Assuming 'assigned_to' is a related field to Employee model
        }

        return Response({'task': task_data}, status=status.HTTP_200_OK)

    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def view_my_emptask(request):
    
    user_id = request.session.get('user_id')
    
    if not user_id:
        return Response({'error': 'User ID not found in session'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        employee = Employee.objects.get(employee_id=user_id)
        emptasks = employee_task.objects.filter(assigned_to=employee)

        task_data = [
            {
                'emptask_id': task.emptask_id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'deadline': task.deadline,
                'status': task.emp_taskstatus
            }
            for task in emptasks
        ]
        return Response({'tasks': task_data}, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def view_employee_emptask_by_id(request, employee_id):
    """
    GET request to fetch tasks assigned to a specific employee by their employee ID.
    """
    try:
        # Retrieve the employee object based on employee_id from URL parameter
        employee = Employee.objects.get(employee_id=employee_id)

        # Get all the tasks assigned to this employee
        emptasks = employee_task.objects.filter(assigned_to=employee)

        # Prepare the response data
        task_data = [
            {
                'task_id': task.id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'deadline': task.deadline,
                'status': task.emp_taskstatus
            }
            for task in emptasks
        ]
        
        return Response({'tasks': task_data}, status=status.HTTP_200_OK)
    
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_emptask(request, task_name):
    try:
        # Fetch the task based on task_name
        task = employee_task.objects.get(task_name=task_name)
        task.delete()
        return Response({'message': 'Task deleted successfully!'}, status=status.HTTP_200_OK)
    
    except employee_task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def project_manager_dashboard(request, user):
    try:
        # Fetch the manager based on the username
        manager = Manager.objects.get(username=user)
        
        # Fetch the projects associated with the manager
        projects = Project.objects.filter(project_manager=manager)
        
        # Prepare project data to send in the response
        project_data = []
        for project in projects:
            project_data.append({
                'project_id': project.project_id,
                'project_name': project.project_name,
                'project_description': project.project_description,
                # Add other relevant project fields here
            })
        
        # Send response with manager and project details
        return Response({
            'manager': {
                'manager_id': manager.manager_id,
                'manager_name': manager.manager_name,
                # Include other manager fields as necessary
            },
            'projects': project_data,
        }, status=status.HTTP_200_OK)
    
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
@api_view(['GET'])
def get_project_tasks(request, project_id):
    """
    Retrieve all tasks associated with a specific project.
    """
    try:
        # Get the project object or return 404 if not found
        project = get_object_or_404(Project, project_id=project_id)

        # Fetch all tasks associated with the project
        tasks = Task.objects.filter(project=project)

        # Serialize task data (custom or using a serializer)
        task_data = [
            {
                'task_id': task.task_id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'assigned_to': task.assigned_to.employee_name if task.assigned_to else None,
                'status': task.status,
                'deadline': task.deadline,
            }
            for task in tasks
        ]

        return Response({'project': project.project_name, 'tasks': task_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# GET: Retrieve all projects managed by a specific manager --------July 10-----------------

@api_view(['GET'])
def get_manager_projects(request, user_id):
    try:
        # Fetch the manager based on the manager_id
        manager = Manager.objects.get(manager_id=user_id)
        
        # Fetch the projects associated with the manager
        projects = Project.objects.filter(project_manager=user_id)
        
        # Prepare project data to send in the response
        project_data = []
        for project in projects:
            project_data.append({
                'project_id': project.project_id,
                'name': project.name,  
                'description': project.description,  
                'start_date': project.start_date.isoformat() if project.start_date else None,  
                'deadline': project.deadline.isoformat() if project.deadline else None,  
                'project_status': project.project_status, 
                'manager_name': manager.manager_name,
                
            })
        
        # Send response with manager and project details
        return Response({
            'manager': {
                'manager_id': manager.manager_id,
                'manager_name': manager.manager_name,
            },
            'projects': project_data,
        }, status=status.HTTP_200_OK)
    
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def update_managerproject_status(request, project_id):
    try:
        # Fetch the project using the provided project_id
        project = Project.objects.get(project_id=project_id)
        
        # Get the new status from the request body (JSON)
        new_status = request.data.get('project_status')

        # Update the project status
        project.project_status = new_status

        # If the status is "completed", mark the project as completed
        if new_status == 'completed':
            project.completion_date = timezone.now()  # Save current date as completion date

            # If the project is completed late, request a reason for the delay
            if project.is_late():  # Check if the project was completed after the deadline
                project.completion_reason = request.data.get('completion_reason', '')

        elif new_status == 'overdue':
            project.completion_reason = request.data.get('completion_reason', '')

        project.save()  # Save the updated project status

        # Return a success response with the updated project status
        return Response({'message': 'Project status updated successfully!'}, status=status.HTTP_200_OK)
    
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    

# GET: Fetch Project by ID
# @api_view(['GET'])
# def get_project_by_id(request, project_id):
#     try:
#         # Retrieve the project using the project_id
#         project = Project.objects.get(project_id=project_id)

#         # Prepare the project data to return in the response
#         project_data = {
#             'project_id': project.project_id,
#             'project_name': project.project_name,
#             'project_status': project.project_status,
#             'completion_date': project.completion_date,
#             'completion_reason': project.completion_reason,
#         }

#         return Response(project_data, status=status.HTTP_200_OK)

#     except Project.DoesNotExist:
#         return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

# GET: Fetch Projects by Status
@api_view(['GET'])
def get_projects_by_status(request, status_filter):
    try:
        # Fetch the projects by their status
        projects = Project.objects.filter(project_status=status_filter)

        if not projects:
            return Response({'message': f'No projects found with status: {status_filter}'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare the list of project data to return in the response
        projects_data = [
            {
                'project_id': project.project_id,
                'project_name': project.project_name,
                'project_status': project.project_status,
                'completion_date': project.completion_date,
                'completion_reason': project.completion_reason,
            }
            for project in projects
        ]

        return Response(projects_data, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Projects not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def kanban_dashboard(request):
    # Fetch projects categorized by their status
    not_started_projects = Project.objects.filter(project_status='not_started')
    in_progress_projects = Project.objects.filter(project_status='in_progress')
    completed_projects = Project.objects.filter(project_status='completed')

    # Prepare the data to be returned in the response
    projects_data = {
        'not_started_projects': [project.name for project in not_started_projects],
        'in_progress_projects': [project.name for project in in_progress_projects],
        'completed_projects': [project.name for project in completed_projects],
    }

    return Response(projects_data)


@api_view(['GET'])
def kanban_dashboard_all(request):
    """
    Retrieve all projects categorized by their status.
    """
    not_started_projects = Project.objects.filter(project_status='not_started')
    in_progress_projects = Project.objects.filter(project_status='in_progress')
    completed_projects = Project.objects.filter(project_status='completed')

    projects_data = {
        'not_started_projects': [project.name for project in not_started_projects],
        'in_progress_projects': [project.name for project in in_progress_projects],
        'completed_projects': [project.name for project in completed_projects],
    }

    return Response(projects_data)


@api_view(['GET'])
def kanban_dashboard_by_status(request, status_name):
    """
    Retrieve projects filtered by a specific status.
    """
    valid_statuses = ['not_started', 'in_progress', 'completed']

    if status_name not in valid_statuses:
        return Response(
            {"error": f"Invalid status name. Valid options are: {', '.join(valid_statuses)}."},
            status=400,
        )

    projects = Project.objects.filter(project_status=status_name)
    projects_data = [project.name for project in projects]

    return Response({f'{status_name}_projects': projects_data})



# @api_view(['POST'])
# def update_project_status(request):
#     project_id = request.data.get('project_id')
#     new_status = request.data.get('new_status')

#     try:
#         # Retrieve the project by its ID
#         project = Project.objects.get(id=project_id)
#         project.project_status = new_status
#         project.save()

#         return Response({'success': True}, status=status.HTTP_200_OK)
#     except Project.DoesNotExist:
#         return Response({'success': False, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_projects(request):
    # Get all projects with selected fields
    projects = Project.objects.all().values('project_id', 'name', 'start_date', 'deadline', 'project_status', 'description')
    project_list = list(projects)  # Convert QuerySet to list
    
    return Response(project_list)  # Return the list of projects as a JSON response


@api_view(['POST'])
def get_project_data(request):
    # Fetch all projects
    projects = Project.objects.all()
    
    # Prepare the project data as a list of dictionaries
    project_data = [
        {
            'id': project.project_id,
            'name': project.name,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'deadline': project.deadline.strftime('%Y-%m-%d'),
            'status': project.project_status
        }
        for project in projects
    ]
    
    return Response(project_data)  # Return the project data as a JSON response



@api_view(['GET'])
def get_project_details(request, project_id):
    """
    Retrieve details of a specific project by its ID.
    """
    try:
        project = get_object_or_404(Project, project_id=project_id)
        project_data = {
            'id': project.project_id,
            'name': project.name,
            'description': project.project_description,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'deadline': project.deadline.strftime('%Y-%m-%d'),
            'status': project.project_status,
        }
        return Response({'success': True, 'project': project_data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_active_projects(request):
    """
    Retrieve all active projects.
    """
    try:
        active_projects = Project.objects.filter(project_status="Active").values(
            'project_id', 'name', 'start_date', 'deadline'
        )
        project_list = list(active_projects)
        return Response({'success': True, 'active_projects': project_list}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def upload_document(request, task_id):
    # Ensure that file is in the request
    if 'document' not in request.FILES:
        return Response({'error': 'No document provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the task associated with the given task_id
    task = get_object_or_404(Task, task_id=task_id)

    # Extract the uploaded document
    document = request.FILES['document']

    # Create the TaskDocument object and save it
    TaskDocument.objects.create(
        task=task,
        uploaded_by=task.manager.username,  # Assuming 'manager' is a related field
        document=document
    )

    # Return a success response
    return Response({'message': 'Document uploaded successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def upload_document_emp(request, id):
    # Ensure that the document is provided in the request
    if 'document' not in request.FILES:
        return Response({'error': 'No document provided'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the employee_task associated with the given task id
    task = get_object_or_404(employee_task, id=id)

    # Extract the uploaded document
    document = request.FILES['document']
    uploaded_by = task.assigned_to  # Assuming 'assigned_to' is an Employee object

    # Create a TaskEmpDocument object and save it
    TaskEmpDocument.objects.create(
        employee_task=task,
        uploaded_by=uploaded_by,
        document=document
    )

    # Return a success response
    return Response({'message': 'Document uploaded successfully'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_task_documents(request, task_id):
    """
    Get all documents uploaded for a specific task.
    """
    try:
        # Get the task associated with the given task_id
        task = get_object_or_404(Task, task_id=task_id)
        
        # Retrieve all documents for the task
        documents = TaskDocument.objects.filter(task=task)
        
        # Prepare the response data
        document_data = [
            {
                'document_id': doc.id,
                'uploaded_by': doc.uploaded_by,
                'document_url': doc.document.url,  # Assuming the file field stores URL
                'upload_date': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for doc in documents
        ]

        return Response({'documents': document_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def get_employee_task_documents(request, id):
    """
    Get all documents uploaded for a specific employee's task.
    """
    try:
        # Get the employee_task associated with the given task id
        task = get_object_or_404(employee_task, id=id)
        
        # Retrieve all documents for the employee's task
        documents = TaskEmpDocument.objects.filter(employee_task=task)
        
        # Prepare the response data
        document_data = [
            {
                'document_id': doc.id,
                'uploaded_by': doc.uploaded_by.username,  # Assuming 'uploaded_by' is an Employee object
                'document_url': doc.document.url,
                'upload_date': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for doc in documents
        ]
        
        return Response({'documents': document_data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)






@api_view(['POST'])
def admin_view_documents(request):
    # Fetch documents from the database
    documents = TaskDocument.objects.all()
    empdocuments = TaskEmpDocument.objects.all()

    # Prepare the documents data
    documents_data = [
        {
            'id': doc.id,
            'task_id': doc.task.task_id,
            'uploaded_by': doc.uploaded_by,
            'document': doc.document.url  # Assuming the document is stored as a file URL
        } for doc in documents
    ]
    
    empdocuments_data = [
        {
            'id': emp_doc.id,
            'employee_task_id': emp_doc.employee_task.id,
            'uploaded_by': emp_doc.uploaded_by,
            'document': emp_doc.document.url
        } for emp_doc in empdocuments
    ]

    return Response({'documents': documents_data, 'empdocuments': empdocuments_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def employee_performance_view(request, username):
    try:
        performance_percentage = employee_task.calculate_employee_performance(username)
        return Response({'username': username, 'performance_percentage': performance_percentage}, status=status.HTTP_200_OK)
    except employee_task.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_employee_performance(request, username):
    """
    Get performance of a specific employee by username.
    """
    try:
        performance_percentage = employee_task.calculate_employee_performance(username)
        return Response({'username': username, 'performance_percentage': performance_percentage}, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_employees_performance(request):
    """
    Get performance of all employees.
    """
    employees = Employee.objects.all()
    performance_data = []
    for employee in employees:
        performance_percentage = employee_task.calculate_employee_performance(employee.username)
        performance_data.append({'username': employee.username, 'performance_percentage': performance_percentage})
    
    return Response({'employees': performance_data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def manager_performance_view(request, username):
    try:
        performance_percentage = Task.calculate_manager_performance(username)
        return Response({'username': username, 'performance_percentage': performance_percentage}, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_manager_performance(request, username):
    """
    Get performance of a specific manager by username.
    """
    try:
        performance_percentage = Task.calculate_manager_performance(username)
        return Response({'username': username, 'performance_percentage': performance_percentage}, status=status.HTTP_200_OK)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_all_managers_performance(request):
    """
    Get performance of all managers.
    """
    managers = Manager.objects.all()
    performance_data = []
    for manager in managers:
        performance_percentage = Task.calculate_manager_performance(manager.username)
        performance_data.append({'username': manager.username, 'performance_percentage': performance_percentage})
    
    return Response({'managers': performance_data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_training_program(request):
    serializer = TrainingProgramSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Training program created successfully'},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )
    
@api_view(['POST'])
def create_training_progress(request):
    serializer = TrainingParticipationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Training enroll created successfully'},
            status=status.HTTP_201_CREATED
        )
    return Response(
        {'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )    



@api_view(['POST'])
def enroll_participant(request):
    if request.method == 'POST':
        # Use the serializer to validate and save the data
        serializer = ParticipationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the participation instance
            training_participation = serializer.save()

            # Send email notification
            recipient_email = None
            recipient_name = None

            if training_participation.manager:
                recipient_email = training_participation.manager.email
                recipient_name = training_participation.manager.username
            elif training_participation.employee:
                recipient_email = training_participation.employee.email
                recipient_name = training_participation.employee.username

            if recipient_email:
                send_mail(
                    'Training Enrollment Success',
                    f'Dear {recipient_name}, you have been successfully enrolled in {training_participation.program}.',
                    settings.EMAIL_HOST_USER,
                    [recipient_email],
                    fail_silently=False,
                )

            return Response({'message': 'Participant successfully enrolled and notified.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



# List all training programs
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import TrainingProgram
from .serializers import TrainingProgramSerializer

@api_view(['GET'])
def list_training_programs(request):
    try:
        program = TrainingProgram.objects.all()
        serializer = TrainingProgramSerializer(program, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingProgram.DoesNotExist:
        return Response(
            {"error": "No training programs found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except APIException as e:
        return Response(
            {"error": f"API Exception: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_training_program_details(request, program_id):
    """
    Get details of a specific training program by ID.
    """
    try:
        program = TrainingProgram.objects.get(id=program_id)
        serializer = TrainingProgramSerializer(program)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingProgram.DoesNotExist:
        return Response({'error': 'Training program not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def view_training_progress(request):
    try:
        enroll = TrainingParticipation.objects.all()
        serializer = TrainingParticipationSerializer(enroll, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response(
            {"error": "No training enroll found."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except APIException as e:
        return Response(
            {"error": f"API Exception: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def view_employee_training_progress(request, username):
    """
    Get training progress for a specific employee by username.
    """
    try:
        participations = TrainingParticipation.objects.filter(employee__username=username)
        serializer = TrainingParticipationSerializer(participations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response({'error': 'Training progress not found for this employee'}, status=status.HTTP_404_NOT_FOUND)



# Update view for TrainingProgram
@api_view(['PUT'])
def update_program(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    serializer = TrainingProgramSerializer(program, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete view for TrainingProgram
@api_view(['DELETE'])
def delete_program(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    program.delete()
    return Response({'message': 'Program deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_training_programs_by_category(request, category):
    """
    Get all training programs under a specific category.
    """
    programs = TrainingProgram.objects.filter(category=category)
    serializer = TrainingProgramSerializer(programs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_training_program_by_name(request, program_id):
    """
    Get details of a training program by name.
    """
    try:
        program = TrainingProgram.objects.get(program_id=program_id)
        serializer = TrainingProgramSerializer(program)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingProgram.DoesNotExist:
        return Response({'error': 'Training program not found'}, status=status.HTTP_404_NOT_FOUND) #added





# Update view for TrainingProgress
@api_view(['PUT'])
def update_progress(request, id):
    enroll = get_object_or_404(TrainingParticipation, id=id)
    serializer = TrainingParticipationSerializer(enroll, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_certificate(request, id):
    certificate = get_object_or_404(Certification, id=id)
    serializer = CertificationSerializer(certificate, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete view for TrainingProgress
@api_view(['DELETE'])
def delete_progress(request, id):
    enroll = get_object_or_404(TrainingParticipation, id=id)
    enroll.delete()
    return Response({'message': 'Progress deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_certificate(request, id):
    certificate = get_object_or_404(Certification, id=id)
    certificate.delete()
    return Response({'message': 'Certificate deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_progress_by_program(request, id):
    """
    Get all training progress records for a specific program by name.
    """
    enroll = TrainingParticipation.objects.filter(id=id)
    serializer = TrainingParticipationSerializer(enroll, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_user_progress_by_program(request, username, program_name):
    """
    Get training progress for a specific user in a specific program.
    """
    try:
        progress = TrainingParticipation.objects.get(employee__username=username, program__name=program_name)
        serializer = TrainingParticipationSerializer(progress)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response({'error': 'Progress record not found for this user and program'}, status=status.HTTP_404_NOT_FOUND)




from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import CertificationSerializer
from .models import Certification
from rest_framework.exceptions import NotFound, ValidationError

@api_view(['POST'])
def upload_certificate(request):
    try:
        serializer = CertificationSerializer(data=request.data)
        if serializer.is_valid():
            participation_id = serializer.validated_data['participation'].id

            # Check if a certification already exists for the participation
            if Certification.objects.filter(participation_id=participation_id).exists():
                return Response(
                    {'error': 'A certification already exists for this participation.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the certification and send the email
            certification = serializer.save()
            certification.send_certificate_email()
            return Response({'message': 'Certificate uploaded and email sent successfully!'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def list_certificates(request):
    try:
        # Fetch all certificates and serialize them
        certificate = Certification.objects.all()
        if not certificate:
            raise NotFound('No certificates found.')
        serializer = CertificationSerializer(certificate, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except NotFound as e:
        # Handle not found errors
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        # Catch any unexpected errors
        return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_certificate_by_id(request, id):
    """
    Get details of a specific certificate by ID.
    """
    try:
        certificate = Certification.objects.get(id=id)
        serializer = CertificationSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Certification.DoesNotExist:
        return Response({'error': 'Certificate not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def employee_dashboard_certificates(request,username):
    employee = Employee.objects.get(username=username)  # Retrieve the employee username from the request body
    if not employee:
        return Response({'error': 'Employee username is required.'}, status=status.HTTP_400_BAD_REQUEST)

    certificates = Certification.objects.filter(participation__employee=employee)
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def list_employee_certificates(request, username):
    """
    Get all certificates for a specific employee by username.
    """
    certificates = Certification.objects.filter(participation__employee__username=username)
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_employee_certificate_by_program(request, username, program_name):
    """
    Get a specific certificate for an employee by username and program name.
    """
    try:
        certificate = Certification.objects.get(participation__employee__username=username, participation__program__name=program_name)
        serializer = CertificationSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Certification.DoesNotExist:
        return Response({'error': 'Certificate not found for this employee and program'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def manager_dashboard_certificates(request):
    manager = request.data.get('manager_username')  # Retrieve the manager username from the request body
    if not manager:
        return Response({'error': 'Manager username is required.'}, status=status.HTTP_400_BAD_REQUEST)

    certificates = Certification.objects.filter(participation_manager_username=manager)
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_certificates_by_manager(request, manager_username):
    """
    Get all certificates for employees supervised by a specific manager.
    """
    certificates = Certification.objects.filter(participation__manager__username=manager_username)
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_certificates_by_employee(request, manager_username, employee_username):
    """
    Get certificates for a specific employee under a manager.
    """
    certificates = Certification.objects.filter(
        participation__manager__username=manager_username,
        participation__employee__username=employee_username
    )
    serializer = CertificationSerializer(certificates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(['POST'])
def enroll_training_manager(request):
    training_programs = TrainingProgram.objects.filter(for_managers=True)
    data = [{'id': program.program_id, 'name': program.name} for program in training_programs]
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_manager_training_programs(request):
    """
    Get all training programs available for managers.
    """
    training_programs = TrainingProgram.objects.filter(for_managers=True)
    serializer = TrainingProgramSerializer(training_programs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_training_program_by_id(request, program_id):
    """
    Get details of a specific training program for managers by ID.
    """
    try:
        training_program = TrainingProgram.objects.get(id=program_id, for_managers=True)
        serializer = TrainingProgramSerializer(training_program)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingProgram.DoesNotExist:
        return Response({'error': 'Training program not found or not designated for managers'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def enroll_training_employee(request):
    training_programs = TrainingProgram.objects.filter(for_employees=True)
    data = [{'id': program.program_id, 'name': program.name} for program in training_programs]
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_employee_training_programs(request):
    """
    Get all training programs available for employees.
    """
    training_programs = TrainingProgram.objects.filter(for_employees=True)
    serializer = TrainingProgramSerializer(training_programs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_employee_training_program_by_id(request, program_id):
    """
    Get details of a specific training program for employees by ID.
    """
    try:
        training_program = TrainingProgram.objects.get(id=program_id, for_employees=True)
        serializer = TrainingProgramSerializer(training_program)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingProgram.DoesNotExist:
        return Response({'error': 'Training program not found or not designated for employees'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def enroll_manager(request):
    program_id = request.data.get('program_id')
    manager_username = request.data.get('manager_username')

    if not program_id or not manager_username:
        return Response({'error': 'Program ID and Manager username are required.'}, status=status.HTTP_400_BAD_REQUEST)

    program = TrainingProgram.objects.filter(program_id=program_id).first()
    manager = Manager.objects.filter(username=manager_username).first()

    if not program or not manager:
        return Response({'error': 'Invalid program or manager.'}, status=status.HTTP_404_NOT_FOUND)

    if TrainingParticipation.objects.filter(program=program, manager=manager).exists():
        return Response({'message': f'You have already been enrolled in {program.name} by admin.'}, status=status.HTTP_400_BAD_REQUEST)

    TrainingParticipation.objects.create(program=program, manager=manager, completion_status='not_started')

    send_mail(
        'Training Enrollment Success',
        f'You have been successfully enrolled in {program.name}.',
        settings.EMAIL_HOST_USER,
        [manager.email],
        fail_silently=False,
    )
    return Response({'message': f'Successfully enrolled in {program.name}.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def list_manager_enrollments(request, manager_username):
    """
    Get all training programs that a specific manager is enrolled in.
    """
    manager = Manager.objects.filter(username=manager_username).first()
    if not manager:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = TrainingParticipation.objects.filter(manager=manager)
    serializer = TrainingParticipationSerializer(enrollments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_enrollment_details(request, manager_username, program_id):
    """
    Get enrollment details for a specific manager in a specific program.
    """
    manager = Manager.objects.filter(username=manager_username).first()
    program = TrainingProgram.objects.filter(program_id=program_id).first()

    if not manager or not program:
        return Response({'error': 'Manager or program not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        enrollment = TrainingParticipation.objects.get(manager=manager, program=program)
        serializer = TrainingParticipationSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response({'error': 'Enrollment not found for this manager and program'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
def enroll_employee(request):
    program_id = request.data.get('program_id')
    employee_username = request.data.get('employee_username')

    if not program_id or not employee_username:
        return Response({'error': 'Program ID and Employee username are required.'}, status=status.HTTP_400_BAD_REQUEST)

    program = TrainingProgram.objects.filter(program_id=program_id).first()
    employee = Employee.objects.filter(username=employee_username).first()

    if not program or not employee:
        return Response({'error': 'Invalid program or employee.'}, status=status.HTTP_404_NOT_FOUND)

    if TrainingParticipation.objects.filter(program=program, employee=employee).exists():
        return Response({'message': f'You have already been enrolled in {program.name} by admin.'}, status=status.HTTP_400_BAD_REQUEST)

    TrainingParticipation.objects.create(program=program, employee=employee, completion_status='not_started')

    send_mail(
        'Training Enrollment Success',
        f'You have been successfully enrolled in {program.name}.',
        settings.EMAIL_HOST_USER,
        [employee.email],
        fail_silently=False,
    )
    return Response({'message': f'Successfully enrolled in {program.name}.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def list_employee_enrollments(request, employee_username):
    """
    Get all training programs that a specific employee is enrolled in.
    """
    employee = Employee.objects.filter(username=employee_username).first()
    if not employee:
        return Response({'error': 'Employee not found'}, status=status.HTTP_404_NOT_FOUND)

    enrollments = TrainingParticipation.objects.filter(employee=employee)
    serializer = TrainingParticipationSerializer(enrollments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_employee_enrollment_details(request, employee_username, program_id):
    """
    Get enrollment details for a specific employee in a specific program.
    """
    employee = Employee.objects.filter(username=employee_username).first()
    program = TrainingProgram.objects.filter(program_id=program_id).first()

    if not employee or not program:
        return Response({'error': 'Employee or program not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        enrollment = TrainingParticipation.objects.get(employee=employee, program=program)
        serializer = TrainingParticipationSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response({'error': 'Enrollment not found for this employee and program'}, status=status.HTTP_404_NOT_FOUND)




@api_view(['POST'])
def performance_chart_view(request):
    user_id = request.data.get('user_id')
    user_type = request.data.get('user_type')

    if not user_id or not user_type:
        return Response({'error': 'User ID and User Type are required.'}, status=status.HTTP_400_BAD_REQUEST)

    performance_data = get_performance_data(user_id, user_type)
    return Response({'performance': performance_data}, status=status.HTTP_200_OK)


def get_performance_data(user_id, user_type):
    if user_type == 'employee':
        logs = TaskLog.objects.filter(employee__employee_id=user_id)
    elif user_type == 'manager':
        logs = TaskLog.objects.filter(manager__manager_id=user_id)
    else:
        return {'error': 'Invalid user type.'}

    # Daily Performance
    today = now().date()
    daily_data = logs.filter(check_out_time__date=today).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Weekly Performance
    start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
    weekly_data = logs.filter(check_out_time__date__gte=start_of_week).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Monthly Performance
    start_of_month = today.replace(day=1)  # First day of the current month
    monthly_data = logs.filter(check_out_time__date__gte=start_of_month).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Annual Performance
    start_of_year = today.replace(month=1, day=1)  # First day of the current year
    annual_data = logs.filter(check_out_time__date__gte=start_of_year).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    return {
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data,
        'annual': annual_data
    }

@api_view(['GET'])
def get_employee_performance(request, employee_id):
    """
    Get the performance data for a specific employee.
    """
    logs = TaskLog.objects.filter(employee__employee_id=employee_id)
    
    # Daily Performance
    today = now().date()
    daily_data = logs.filter(check_out_time__date=today).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Weekly Performance
    start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
    weekly_data = logs.filter(check_out_time__date__gte=start_of_week).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Monthly Performance
    start_of_month = today.replace(day=1)  # First day of the current month
    monthly_data = logs.filter(check_out_time__date__gte=start_of_month).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Annual Performance
    start_of_year = today.replace(month=1, day=1)  # First day of the current year
    annual_data = logs.filter(check_out_time__date__gte=start_of_year).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    return Response({
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data,
        'annual': annual_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_performance(request, manager_id):
    """
    Get the performance data for a specific manager.
    """
    logs = TaskLog.objects.filter(manager__manager_id=manager_id)

    # Daily Performance
    today = now().date()
    daily_data = logs.filter(check_out_time__date=today).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Weekly Performance
    start_of_week = today - timedelta(days=today.weekday())  # Monday of this week
    weekly_data = logs.filter(check_out_time__date__gte=start_of_week).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Monthly Performance
    start_of_month = today.replace(day=1)  # First day of the current month
    monthly_data = logs.filter(check_out_time__date__gte=start_of_month).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    # Annual Performance
    start_of_year = today.replace(month=1, day=1)  # First day of the current year
    annual_data = logs.filter(check_out_time__date__gte=start_of_year).aggregate(
        total_hours=Sum('hours_worked'),
        task_count=Count('id')
    )

    return Response({
        'daily': daily_data,
        'weekly': weekly_data,
        'monthly': monthly_data,
        'annual': annual_data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
def task_check_in(request):
    task_id = request.data.get('task_id')
    user_type = request.data.get('user_type')
    user_id = request.data.get('user_id')

    if not task_id or not user_type or not user_id:
        return Response({'error': 'Task ID, User Type, and User ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if user_type == 'employee':
        employee = get_object_or_404(Employee, employee_id=user_id)
        emptask = get_object_or_404(employee_task, emptask_id=task_id)

        # Check if the employee already has any active task logs (not checked out)
        if TaskLog.objects.filter(employee=employee, check_out_time__isnull=True).exists():
            return Response({'error': "You have already checked in to a task. Please check out before starting a new task."}, status=status.HTTP_400_BAD_REQUEST)

        TaskLog.objects.create(employeetask=emptask, employee=employee, check_in_time=now())
        return Response({'success': 'Checked in successfully!'}, status=status.HTTP_200_OK)

    elif user_type == 'manager':
        manager = get_object_or_404(Manager, manager_id=user_id)
        task = get_object_or_404(Task, task_id=task_id)

        # Check if the manager already has any active task logs (not checked out)
        if TaskLog.objects.filter(manager=manager, check_out_time__isnull=True).exists():
            return Response({'error': "You have already checked in to a task. Please check out before starting a new task."}, status=status.HTTP_400_BAD_REQUEST)

        TaskLog.objects.create(task=task, manager=manager, check_in_time=now())
        return Response({'success': 'Checked in successfully!'}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def task_check_out(request):
    task_id = request.data.get('task_id')
    user_type = request.data.get('user_type')

    if not task_id or not user_type:
        return Response({'error': 'Task ID and User Type are required.'}, status=status.HTTP_400_BAD_REQUEST)

    if user_type == 'employee':
        emptask = get_object_or_404(employee_task, emptask_id=task_id)

        try:
            log = TaskLog.objects.get(employeetask=emptask, check_out_time__isnull=True)
        except TaskLog.DoesNotExist:
            return Response({'error': "This task has already been checked out or was never checked in."}, status=status.HTTP_400_BAD_REQUEST)

        log.check_out_time = now()
        log.calculate_hours_worked()
        log.save()
        return Response({'success': 'Checked out successfully!'}, status=status.HTTP_200_OK)

    elif user_type == 'manager':
        task = get_object_or_404(Task, task_id=task_id)

        try:
            log = TaskLog.objects.get(task=task, check_out_time__isnull=True)
        except TaskLog.DoesNotExist:
            return Response({'error': "This task has already been checked out or was never checked in."}, status=status.HTTP_400_BAD_REQUEST)

        log.check_out_time = now()
        log.calculate_hours_worked()
        log.save()
        return Response({'success': 'Checked out successfully!'}, status=status.HTTP_200_OK)

    return Response({'error': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_employee_active_task(request, employee_id):
    """
    Get the current active task log for a specific employee.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    active_log = TaskLog.objects.filter(employee=employee, check_out_time__isnull=True).first()

    if not active_log:
        return Response({'error': 'No active task found for this employee.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the active log details
    serializer = TaskLogSerializer(active_log)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_manager_active_task(request, manager_id):
    """
    Get the current active task log for a specific manager.
    """
    manager = get_object_or_404(Manager, manager_id=manager_id)
    active_log = TaskLog.objects.filter(manager=manager, check_out_time__isnull=True).first()

    if not active_log:
        return Response({'error': 'No active task found for this manager.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the active log details
    serializer = TaskLogSerializer(active_log)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def md_create_project(request):
    required_fields = ['project_id', 'project_name', 'project_description', 'project_startdate', 'project_deadline', 'project_manager']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    project = Project(
        project_id=request.data['project_id'],
        name=request.data['project_name'],
        description=request.data['project_description'],
        start_date=request.data['project_startdate'],
        deadline=request.data['project_deadline'],
        project_manager=request.data['project_manager']
    )
    project.save()
    return Response({'success': 'Project created successfully!'}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def md_edit_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    required_fields = ['project_id', 'project_name', 'project_description', 'project_start_date', 'project_deadline', 'project_manager']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    project.project_id = request.data['project_id']
    project.name = request.data['project_name']
    project.description = request.data['project_description']
    project.start_date = request.data['project_start_date']
    project.deadline = request.data['project_deadline']
    project.project_manager = request.data['project_manager']
    project.save()

    return Response({'success': 'Project updated successfully!'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def md_show_project_status(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    tasks = Task.objects.filter(project_name=project.name)
    emptasks = employee_task.objects.filter(team_project_name=project.name)

    context = {
        'project': {
            'project_id': project.project_id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date,
            'deadline': project.deadline,
            'manager': project.project_manager,
        },
        'tasks': list(tasks.values()),
        'emptasks': list(emptasks.values())
    }
    return Response(context, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_list_projects(request):
    """
    List all projects with their essential details.
    """
    projects = Project.objects.all()
    project_data = [
        {
            'project_id': project.project_id,
            'name': project.name,
            'description': project.description,
            'start_date': project.start_date,
            'deadline': project.deadline,
            'manager': project.project_manager,
        }
        for project in projects
    ]
    
    return Response(project_data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def md_delete_project(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    project.delete()
    return Response({'success': 'Project deleted successfully!'}, status=status.HTTP_200_OK)



@api_view(['POST'])
def md_create_task(request):
    required_fields = ['task_id', 'project_manager', 'project_name', 'task_name', 'task_description', 'priority', 'task_startdate', 'task_deadline']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        manager = Manager.objects.get(manager_name=request.data['project_manager'])
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
    
    task = Task(
        task_id=request.data['task_id'],
        project_manager=manager.manager_name,
        project_name=request.data['project_name'],
        task_name=request.data['task_name'],
        description=request.data['task_description'],
        priority=request.data['priority'],
        start_date=request.data['task_startdate'],
        deadline=request.data['task_deadline'],
        manager=manager
    )
    task.save()
    return Response({'success': 'Task created successfully!'}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def md_edit_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)

    required_fields = ['task_id', 'project_manager', 'project_name', 'task_name', 'task_description', 'priority', 'task_startdate', 'task_deadline']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        manager = Manager.objects.get(manager_name=request.data['project_manager'])
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)

    task.task_id = request.data['task_id']
    task.project_name = request.data['project_name']
    task.task_name = request.data['task_name']
    task.description = request.data['task_description']
    task.priority = request.data['priority']
    task.start_date = request.data['task_startdate']
    task.deadline = request.data['task_deadline']
    task.manager = manager
    task.save()

    return Response({'success': 'Task updated successfully!'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def md_delete_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    task.delete()
    return Response({'success': 'Task deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_show_task_details(request, task_id):
    """
    Retrieve the details of a task by its task ID.
    """
    task = get_object_or_404(Task, task_id=task_id)

    task_data = {
        'task_id': task.task_id,
        'project_manager': task.project_manager,
        'project_name': task.project_name,
        'task_name': task.task_name,
        'description': task.description,
        'priority': task.priority,
        'start_date': task.start_date,
        'deadline': task.deadline,
        'manager': task.manager,
    }

    return Response(task_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_list_project_tasks(request, project_name):
    """
    List all tasks associated with a specific project by project name.
    """
    tasks = Task.objects.filter(project_name=project_name)
    task_data = [
        {
            'task_id': task.task_id,
            'task_name': task.task_name,
            'description': task.description,
            'priority': task.priority,
            'start_date': task.start_date,
            'deadline': task.deadline,
            'manager': task.manager,
        }
        for task in tasks
    ]

    return Response(task_data, status=status.HTTP_200_OK)



@api_view(['POST'])
def md_create_role(request):
    # Validate required fields
    required_fields = ['role_id', 'role_name']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    # Create the role
    role = Role(
        role_id=request.data['role_id'],
        role_name=request.data['role_name']
    )
    role.save()
    return Response({'success': 'Role created successfully!'}, status=status.HTTP_201_CREATED)


@api_view(['PUT'])
def md_edit_role(request, id):
    role = get_object_or_404(Role, id=id)

    # Validate required fields
    required_fields = ['role_id', 'role_name']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the role
    role.role_id = request.data['role_id']
    role.role_name = request.data['role_name']
    role.save()

    return Response({'success': 'Role updated successfully!'}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def md_delete_role(request, id):
    role = get_object_or_404(Role, id=id)
    role.delete()
    return Response({'success': 'Role deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_show_role_details(request, id):
    """
    Retrieve the details of a role by its ID.
    """
    role = get_object_or_404(Role, id=id)

    role_data = {
        'role_id': role.role_id,
        'role_name': role.role_name
    }

    return Response(role_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_list_roles(request):
    """
    List all roles in the system.
    """
    roles = Role.objects.all()
    role_data = [
        {
            'role_id': role.role_id,
            'role_name': role.role_name
        }
        for role in roles
    ]

    return Response(role_data, status=status.HTTP_200_OK)



# Create Team
@api_view(['POST'])
def md_create_team(request):
    # Validate required fields
    required_fields = ['team_id', 'team_name', 'project', 'team_task', 'manager', 'team_leader', 'members']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract data from request
    team_name = request.data['team_name']
    project_name = request.data['project']
    team_task = request.data['team_task']
    manager_name = request.data['manager']
    team_leader_name = request.data['team_leader']
    members = request.data['members']
    team_id = request.data['team_id']

    # Fetch related objects
    project = get_object_or_404(Project, name=project_name)
    manager = get_object_or_404(Manager, manager_name=manager_name)
    team_leader = get_object_or_404(Employee, employee_name=team_leader_name)

    # Create the team
    team = Team(team_name=team_name, project=project, team_task=team_task,  manager=manager, team_leader=team_leader, team_id=team_id)
    team.save()

    # Add members to the team
    for member_name in members:
        member = get_object_or_404(Employee, employee_name=member_name)
        team.members.add(member)
    
    team.save()

    return Response({'success': 'Team created successfully!'}, status=status.HTTP_201_CREATED)


# Edit Team
@api_view(['PUT'])
def md_edit_team(request, team_id):
    team = get_object_or_404(Team, team_id=team_id)

    # Validate required fields
    required_fields = ['team_name', 'project', 'team_task', 'manager', 'team_leader', 'members']
    for field in required_fields:
        if field not in request.data:
            return Response({'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Extract data from request
    team_name = request.data['team_name']
    project_name = request.data['project']
    team_task = request.data['team_task']
    manager_name = request.data['manager']
    team_leader_name = request.data['team_leader']
    members = request.data['members']
    team_id = request.data['team_id']

    # Fetch related objects
    project = get_object_or_404(Project, name=project_name)
    manager = get_object_or_404(Manager, manager_name=manager_name)
    team_leader = get_object_or_404(Employee, employee_name=team_leader_name)

    # Update team details
    team.team_name = team_name
    team.project = project
    team.team_task = team_task
    team.manager = manager
    team.team_leader = team_leader
    team.team_id = team_id
    team.save()

    # Clear existing members and add updated ones
    team.members.clear()
    for member_name in members:
        member = get_object_or_404(Employee, employee_name=member_name)
        team.members.add(member)

    return Response({'success': 'Team updated successfully!'}, status=status.HTTP_200_OK)


# Delete Team
@api_view(['DELETE'])
def md_delete_team(request, team_id):
    team = get_object_or_404(Team, team_id=team_id)
    team.delete()
    return Response({'success': 'Team deleted successfully!'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_show_team_details(request, team_id):
    """
    Retrieve the details of a team by its team_id.
    """
    team = get_object_or_404(Team, team_id=team_id)

    team_data = {
        'team_id': team.team_id,
        'team_name': team.team_name,
        'project': team.project.name,
        'team_task': team.team_task,
        'manager': team.manager.manager_name,
        'team_leader': team.team_leader.employee_name,
        'members': [member.employee_name for member in team.members.all()],
    }

    return Response(team_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_list_teams(request):
    """
    List all teams in the system.
    """
    teams = Team.objects.all()
    team_data = [
        {
            'team_id': team.team_id,
            'team_name': team.team_name,
            'project': team.project.name,
            'team_task': team.team_task,
            'manager': team.manager.manager_name,
            'team_leader': team.team_leader.employee_name,
            'members': [member.employee_name for member in team.members.all()],
        }
        for team in teams
    ]

    return Response(team_data, status=status.HTTP_200_OK)




@api_view(['GET'])
def md_kanban_dashboard(request):
    # Fetch projects categorized by their status
    not_started_projects = Project.objects.filter(project_status='not_started')
    in_progress_projects = Project.objects.filter(project_status='in_progress')
    completed_projects = Project.objects.filter(project_status='completed')

    # Serialize project data to return as JSON
    not_started_projects_data = [{"project_id": project.project_id, "project_name": project.name, "status": project.project_status} for project in not_started_projects]
    in_progress_projects_data = [{"project_id": project.project_id, "project_name": project.name, "status": project.project_status} for project in in_progress_projects]
    completed_projects_data = [{"project_id": project.project_id, "project_name": project.name, "status": project.project_status} for project in completed_projects]

    # Return data as a JSON response
    return Response({
        'not_started_projects': not_started_projects_data,
        'in_progress_projects': in_progress_projects_data,
        'completed_projects': completed_projects_data
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_projects_by_category(request, category):
    """
    Fetch projects filtered by the given category.
    :param request: HTTP request
    :param category: Category to filter projects ('not_started', 'in_progress', 'completed')
    :return: JSON response with filtered projects
    """
    valid_categories = ['not_started', 'in_progress', 'completed']
    if category not in valid_categories:
        return Response({'error': f'Invalid category. Choose from {valid_categories}.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch projects filtered by category
    projects = Project.objects.filter(project_status=category)
    projects_data = [{"project_id": project.project_id, "project_name": project.name, "status": project.project_status} for project in projects]

    # Return the filtered data as a JSON response
    return Response({'projects': projects_data}, status=status.HTTP_200_OK)




@api_view(['GET'])
def md_projects_by_manager(request, manager_name):
    """
    Retrieve projects managed by a specific manager.
    """
    # Fetch projects where the manager is assigned
    projects = Project.objects.filter(project_manager=manager_name)

    # Serialize project data
    project_data = [{"project_id": project.project_id, "project_name": project.name, "status": project.project_status} for project in projects]

    return Response({
        'manager': manager_name,
        'projects': project_data
    }, status=status.HTTP_200_OK)

    

@api_view(['GET'])
def md_get_projects(request):
    projects = Project.objects.all().values('project_id', 'name', 'start_date', 'deadline', 'project_status')
    project_list = list(projects)  # Convert QuerySet to list
    return Response(project_list, status=200)

@api_view(['GET'])
def md_get_projects_by_status(request, status):
    """
    Retrieve projects filtered by their status.
    """
    projects = Project.objects.filter(project_status=status).values('project_id', 'name', 'start_date', 'deadline', 'project_status')
    project_list = list(projects)  # Convert QuerySet to list
    return Response(project_list, status=200)


@api_view(['GET'])
def md_get_project_data(request):
    projects = Project.objects.all()
    project_data = [
        {
            'id': project.project_id,
            'name': project.name,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'deadline': project.deadline.strftime('%Y-%m-%d'),
            'status': project.project_status
        }
        for project in projects
    ]
    return Response(project_data, status=200)

@api_view(['GET'])
def md_get_project_by_id(request, project_id):
    """
    Retrieve a project by its project_id.
    """
    try:
        project = Project.objects.get(project_id=project_id)
        project_data = {
            'id': project.project_id,
            'name': project.name,
            'start_date': project.start_date.strftime('%Y-%m-%d'),
            'deadline': project.deadline.strftime('%Y-%m-%d'),
            'status': project.project_status
        }
        return Response(project_data, status=200)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=404)



@api_view(['GET'])
def md_admin_view_documents(request):
    documents = TaskDocument.objects.all().values('document_id', 'document_name', 'upload_date')
    empdocuments = TaskEmpDocument.objects.all().values('document_id', 'document_name', 'upload_date')
    
    response_data = {
        'documents': list(documents),
        'empdocuments': list(empdocuments)
    }
    
    return Response(response_data, status=200)

@api_view(['GET'])
def md_get_document_by_id(request, document_id):
    """
    Retrieve a document by its document_id.
    """
    try:
        document = TaskDocument.objects.get(document_id=document_id)
        document_data = {
            'document_id': document.document_id,
            'document_name': document.document_name,
            'upload_date': document.upload_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        return Response(document_data, status=200)
    except TaskDocument.DoesNotExist:
        return Response({'error': 'Document not found'}, status=404)




@api_view(['GET'])
def md_employee_performance_view(request, username):
    performance_percentage = employee_task.calculate_employee_performance(username)
    return Response({'performance': performance_percentage}, status=200)

@api_view(['GET'])
def md_employee_tasks_view(request, username):
    """
    Retrieve all tasks assigned to a specific employee by their username.
    """
    try:
        employee = Employee.objects.get(employee_name=username)
        tasks = employee_task.objects.filter(employee=employee).values(
            'emptask_id', 'task_name', 'task_description', 'status', 'assigned_date', 'deadline'
        )
        task_list = list(tasks)
        return Response(task_list, status=200)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee not found'}, status=404)



@api_view(['GET'])
def md_manager_performance_view(request, username):
    performance_percentage = Task.calculate_manager_performance(username)
    return Response({'performance': performance_percentage}, status=200)

@api_view(['GET'])
def md_manager_tasks_view(request, username):
    """
    Retrieve all tasks managed by a specific manager by their username.
    """
    try:
        manager = Manager.objects.get(manager_name=username)
        tasks = Task.objects.filter(manager=manager).values(
            'task_id', 'task_name', 'task_description', 'priority', 'start_date', 'deadline', 'status'
        )
        task_list = list(tasks)
        return Response(task_list, status=200)
    except Manager.DoesNotExist:
        return Response({'error': 'Manager not found'}, status=404)


@api_view(['POST'])
def md_create_training_program(request):
    if request.method == 'POST':
        # Deserialize the incoming JSON data
        serializer = TrainingProgramSerializer(data=request.data)
        
        if serializer.is_valid():
            # Save the new training program if valid
            serializer.save()
            return Response({'message': 'Training program created successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def md_get_all_training_programs(request):
    """
    Retrieve a list of all training programs.
    """
    training_programs = TrainingProgram.objects.all().values(
        'id', 'name', 'description', 'start_date', 'end_date', 'status'
    )
    return Response(list(training_programs), status=200)

@api_view(['GET'])
def md_get_training_program_by_id(request, program_id):
    """
    Retrieve the details of a specific training program by its ID.
    """
    try:
        training_program = TrainingProgram.objects.get(id=program_id)
        response_data = {
            'id': training_program.id,
            'name': training_program.name,
            'description': training_program.description,
            'start_date': training_program.start_date.strftime('%Y-%m-%d'),
            'end_date': training_program.end_date.strftime('%Y-%m-%d'),
            'status': training_program.status
        }
        return Response(response_data, status=200)
    except TrainingProgram.DoesNotExist:
        return Response({'error': 'Training program not found'}, status=404)




@api_view(['POST'])
def md_enroll_participant(request):
    if request.method == 'POST':
        # Deserialize incoming data
        serializer = TrainingParticipationSerializer(data=request.data)
        
        if serializer.is_valid():
            participation = serializer.save()

            # Send email notification
            if participation.manager:
                recipient_email = participation.manager.email
                recipient_name = participation.manager.username
            elif participation.employee:
                recipient_email = participation.employee.email
                recipient_name = participation.employee.username
            else:
                recipient_email = None
                recipient_name = None

            if recipient_email:
                send_mail(
                    'Training Enrollment Success',
                    f'Dear {recipient_name}, you have been successfully enrolled in {participation.program}.',
                    settings.EMAIL_HOST_USER,
                    [recipient_email],
                    fail_silently=False,
                )

            return Response({'message': 'Participant enrolled successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_enrollments(request):
    """
    Retrieve a list of all enrollments.
    """
    enrollments = TrainingParticipation.objects.all()
    enrollments_data = [{
        "id": enrollment.id,
        "employee": enrollment.employee.username if enrollment.employee else None,
        "manager": enrollment.manager.username if enrollment.manager else None,
        "program": enrollment.program,
        "enrollment_date": enrollment.enrollment_date
    } for enrollment in enrollments]

    return Response({'enrollments': enrollments_data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_enrollment_by_id(request, enrollment_id):
    """
    Retrieve details of a specific enrollment by its ID.
    """
    try:
        enrollment = TrainingParticipation.objects.get(id=enrollment_id)
        enrollment_data = {
            "id": enrollment.id,
            "employee": enrollment.employee.username if enrollment.employee else None,
            "manager": enrollment.manager.username if enrollment.manager else None,
            "program": enrollment.program,
            "enrollment_date": enrollment.enrollment_date
        }
        return Response({'enrollment': enrollment_data}, status=status.HTTP_200_OK)
    except TrainingParticipation.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['GET'])
def md_list_training_programs(request):
    programs = TrainingProgram.objects.all()
    serializer = TrainingProgramSerializer(programs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def md_view_training_progress(request):
    participations = TrainingParticipation.objects.all()
    serializer = TrainingParticipationSerializer(participations, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
def md_update_program(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    if request.method == 'PUT':
        serializer = TrainingProgramSerializer(program, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Training program updated successfully!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def md_delete_program(request, program_id):
    program = get_object_or_404(TrainingProgram, program_id=program_id)
    program.delete()
    return Response({'message': 'Training program deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def md_get_training_programs_by_status(request, status):
    """
    Retrieve training programs filtered by their status.
    """
    training_programs = TrainingProgram.objects.filter(status=status).values(
        'id', 'name', 'description', 'start_date', 'end_date', 'status'
    )
    return Response(list(training_programs), status=200)

@api_view(['GET'])
def md_get_training_programs_by_date_range(request, start_date, end_date):
    """
    Retrieve training programs within a specific date range.
    """
    training_programs = TrainingProgram.objects.filter(
        start_date__gte=start_date,
        start_date__lte=end_date
    ).values('id', 'name', 'description', 'start_date', 'end_date', 'status')
    return Response(list(training_programs), status=200)


@api_view(['PUT'])
def md_update_progress(request, program_name):
    progress = get_object_or_404(TrainingParticipation, program__name=program_name)
    if request.method == 'PUT':
        serializer = TrainingParticipationSerializer(progress, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Training progress updated successfully!'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def md_delete_progress(request, program_name):
    progress = get_object_or_404(TrainingParticipation, program__name=program_name)
    progress.delete()
    return Response({'message': 'Training progress deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def md_get_progress_by_program(request, program_name):
    """
    Retrieve training progress for a specific program by its name.
    """
    progress = TrainingParticipation.objects.filter(program__name=program_name).values(
        'participant__name', 'progress', 'completion_date', 'feedback'
    )
    return Response(list(progress), status=200)

@api_view(['GET'])
def md_get_all_training_progress(request):
    """
    Retrieve progress data for all training programs.
    """
    progress = TrainingParticipation.objects.all().values(
        'program_name', 'participant_name', 'progress', 'completion_date', 'feedback'
    )
    return Response(list(progress), status=200)



@api_view(['POST'])
def md_upload_certificate(request):
    if request.method == 'POST':
        # Use serializer to handle file and form data
        serializer = CertificationSerializer(data=request.data)
        
        if serializer.is_valid():
            certification = serializer.save()
            
            # Send the certificate email (you might need to adjust this part as per your email logic)
            certification.send_certificate_email()
            
            # Return a success response
            return Response({'message': 'Certificate uploaded and email sent successfully!'}, status=status.HTTP_201_CREATED)
        
        # Return errors if the serializer is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def md_get_certificates_by_user(request, username):
    """
    Retrieve all certificates uploaded for a specific user.
    """
    certificates = Certification.objects.filter(user__username=username).values(
        'id', 'certificate_name', 'upload_date', 'file_url'
    )
    return Response(list(certificates), status=200)

@api_view(['GET'])
def md_get_all_certificates(request):
    """
    Retrieve all uploaded certificates.
    """
    certificates = Certification.objects.all().values(
        'id', 'user__username', 'certificate_name', 'upload_date', 'file_url'
    )
    return Response(list(certificates), status=200)





@api_view(['POST'])
def md_performance_chart(request, user_type, user_id):
    # Get the user type (manager or employee)
    if user_type == 'employee':
        user = get_object_or_404(Employee, employee_id=user_id)
        task_logs = TaskLog.objects.filter(employee=user)
    elif user_type == 'manager':
        user = get_object_or_404(Manager, manager_id=user_id)
        task_logs = TaskLog.objects.filter(manager=user)
    else:
        return Response({"error": "Invalid user type"}, status=status.HTTP_400_BAD_REQUEST)

    # Get current date
    today = now().date()
    
    # Calculate daily, weekly, monthly, and annual data
    daily_data = task_logs.filter(check_in_time__date=today).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    weekly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=7)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    monthly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=30)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    annual_data = task_logs.filter(check_in_time__year=today.year).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    # Prepare the response data
    performance_data = {
        'user_type': user_type,
        'user_id': user_id,
        'user_name': user.username,  # Assuming the user has a username field
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'annual_data': annual_data,
    }
    
    return Response(performance_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_employee_performance_chart(request, employee_id):
    """
    Get performance data for a specific employee.
    """
    employee = get_object_or_404(Employee, employee_id=employee_id)
    task_logs = TaskLog.objects.filter(employee=employee)

    # Calculate performance data
    today = now().date()
    daily_data = task_logs.filter(check_in_time__date=today).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    weekly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=7)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    monthly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=30)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    annual_data = task_logs.filter(check_in_time__year=today.year).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    # Response data
    performance_data = {
        'user_type': 'employee',
        'user_id': employee_id,
        'user_name': employee.username,  # Assuming Employee model has a username field
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'annual_data': annual_data,
    }

    return Response(performance_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_manager_performance_chart(request, manager_id):
    """
    Get performance data for a specific manager.
    """
    manager = get_object_or_404(Manager, manager_id=manager_id)
    task_logs = TaskLog.objects.filter(manager=manager)

    # Calculate performance data
    today = now().date()
    daily_data = task_logs.filter(check_in_time__date=today).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    weekly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=7)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    monthly_data = task_logs.filter(check_in_time__gte=today - timedelta(days=30)).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    annual_data = task_logs.filter(check_in_time__year=today.year).aggregate(
        hours_worked=Sum('hours_worked'),
        total_tasks=Count('task')
    )

    # Response data
    performance_data = {
        'user_type': 'manager',
        'user_id': manager_id,
        'user_name': manager.username,  # Assuming Manager model has a username field
        'daily_data': daily_data,
        'weekly_data': weekly_data,
        'monthly_data': monthly_data,
        'annual_data': annual_data,
    }

    return Response(performance_data, status=status.HTTP_200_OK)




@api_view(['POST'])
def md_create_performance_review(request):
    employee_name = request.data.get('employee_name')
    manager_username = request.data.get('manager_username')
    comments = request.data.get('comments')
    score = request.data.get('score')

    try:
        employee = Employee.objects.get(employee_name=employee_name)
        manager = Manager.objects.get(username=manager_username)
    except (Employee.DoesNotExist, Manager.DoesNotExist):
        return Response({"error": "Employee or Manager not found"}, status=status.HTTP_400_BAD_REQUEST)

    performance_review = PerformanceReview.objects.create(
        employee=employee,
        review_date=timezone.now(),
        manager=manager,
        comments=comments,
        score=score
    )
    return Response({"message": "Performance review created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def md_performance_review_list(request):
    reviews = PerformanceReview.objects.all()
    review_data = [
        {
            'employee_name': review.employee.employee_name,
            'manager_name': review.manager.username,
            'review_date': review.review_date,
            'comments': review.comments,
            'score': review.score
        }
        for review in reviews
    ]
    return Response(review_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def md_employee_performance_reviews(request, employee_name):
    """
    Get all performance reviews for a specific employee.
    """
    try:
        employee = Employee.objects.get(employee_name=employee_name)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    reviews = PerformanceReview.objects.filter(employee=employee)
    review_data = [
        {
            'review_date': review.review_date,
            'manager_name': review.manager.username,
            'comments': review.comments,
            'score': review.score,
        }
        for review in reviews
    ]

    return Response(review_data, status=status.HTTP_200_OK)


@api_view(['POST'])
def md_create_goal(request):
    employee_id = request.data.get('employee_id')
    goal_text = request.data.get('goal_text')
    start_date = request.data.get('start_date') 
    end_date = request.data.get('end_date')

    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_400_BAD_REQUEST)

    Goal.objects.create(
        employee=employee,
        goal_text=goal_text,
        start_date=start_date,
        end_date=end_date
    )
    return Response({"message": "Goal created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def md_goal_list(request):
    goals = Goal.objects.all()
    goal_data = [
        {
            'employee_name': goal.employee.employee_name,
            'goal_text': goal.goal_text,
            'start_date': goal.start_date,
            'end_date': goal.end_date
        }
        for goal in goals
    ]
    return Response(goal_data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_goals_by_employee(request, employee_id):
    """
    Retrieve goals for a specific employee by their ID.
    """
    try:
        goals = Goal.objects.filter(employee__id=employee_id)
        if not goals.exists():
            return Response({'message': 'No goals found for this employee.'}, status=status.HTTP_404_NOT_FOUND)
        
        goal_data = [
            {
                'employee_name': goal.employee.employee_name,
                'goal_text': goal.goal_text,
                'start_date': goal.start_date,
                'end_date': goal.end_date
            }
            for goal in goals
        ]
        return Response(goal_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
def md_create_feedback(request):
    from_manager_id = request.data.get('from_manager_id')
    to_employee_id = request.data.get('to_employee_id')
    comments = request.data.get('comments')

    try:
        from_manager = Manager.objects.get(manager_id=from_manager_id)
        to_employee = Employee.objects.get(employee_id=to_employee_id)
    except (Manager.DoesNotExist, Employee.DoesNotExist):
        return Response({"error": "Manager or Employee not found"}, status=status.HTTP_400_BAD_REQUEST)

    Feedback.objects.create(
        from_manager=from_manager,
        to_employee=to_employee,
        feedback_date=timezone.now(),
        comments=comments
    )
    return Response({"message": "Feedback created successfully"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def md_feedback_list(request):
    feedbacks = Feedback.objects.all()
    feedback_data = [
        {
            'from_manager': feedback.from_manager.username,
            'to_employee': feedback.to_employee.employee_name,
            'feedback_date': feedback.feedback_date,
            'comments': feedback.comments
        }
        for feedback in feedbacks
    ]
    return Response(feedback_data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_feedback_by_employee(request, employee_id):
    """
    Retrieve feedback given to a specific employee by their ID.
    """
    try:
        feedbacks = Feedback.objects.filter(to_employee__id=employee_id)
        if not feedbacks.exists():
            return Response({'message': 'No feedback found for this employee.'}, status=status.HTTP_404_NOT_FOUND)

        feedback_data = [
            {
                'from_manager': feedback.from_manager.username,
                'to_employee': feedback.to_employee.employee_name,
                'feedback_date': feedback.feedback_date,
                'comments': feedback.comments
            }
            for feedback in feedbacks
        ]
        return Response(feedback_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

  
# GET: Retrieve all tasks assigned to a specific manager -------- July 10 ------------------

@api_view(['GET'])
def list_tasks_for_manager(request, manager_id):
    """
    Retrieve tasks assigned to a specific manager using manager_id.
    """
    try:
        # Get the manager object
        manager = Manager.objects.get(manager_id=manager_id)

        # Filter tasks assigned to this manager
        tasks = Task.objects.filter(manager=manager)

        # Serialize the task data
        task_serializer = TaskSerializer(tasks, many=True)

        # Return success response
        return Response({
            'success': True,
            'tasks': task_serializer.data
        }, status=status.HTTP_200_OK)

    except Manager.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Manager not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'An unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#------------- July 10 --------------------------


@api_view(['GET'])
def list_employee_tasks_by_manager(request, manager_id):
    """
    Retrieve all employee tasks created by a specific manager.
    """
    try:
        manager = Manager.objects.get(manager_id=manager_id)

        tasks = employee_task.objects.filter(manager=manager)

        serializer = EmployeeTaskSerializer(tasks, many=True)

        return Response({
            'success': True,
            'tasks': serializer.data
        }, status=status.HTTP_200_OK)

    except Manager.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Manager not found.'
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            'success': False,
            'error': 'Unexpected error occurred.',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# New apis Created For Manpower Plannning 

from django.shortcuts import get_object_or_404
from .models import PositionRequest, Vacancy
from .serializers import PositionRequestSerializer, VacancySerializer
from authentication.models import Employee, Manager,Hr,Location



# projectmanagement/views.py
@api_view(['POST'])
def raise_position_request(request):
    """
    Team Lead raises a new position request.
    """
    try:
        employee_id = request.session.get('user_id')
        if not employee_id:
            return Response(
                {"success": False, "message": "User not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        team_leader = get_object_or_404(Employee, employee_id=employee_id)
        serializer_data = request.data.copy()
        serializer_data['requested_by'] = team_leader.id
        
        serializer = PositionRequestSerializer(data=serializer_data)
        if serializer.is_valid():
            position_request = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Position request raised successfully!",
                    "request_id": position_request.request_id
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def list_position_requests(request):
    """
    HR views all position requests, or Team Lead views their own position requests.
    """
    try:
        user_role = request.session.get('role')
        user_id = request.session.get('user_id')
        if not user_id:
            return Response(
                {"success": False, "message": "User not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if user_role == 'hr':
            requests = PositionRequest.objects.all().select_related('location', 'requested_by', 'hr_reviewer', 'manager_approver')
        else:
            team_leader = get_object_or_404(Employee, employee_id=user_id)
            requests = PositionRequest.objects.filter(requested_by=team_leader).select_related('location', 'requested_by', 'hr_reviewer', 'manager_approver')

        serializer = PositionRequestSerializer(requests, many=True)
        return Response(
            {"success": True, "requests": serializer.data},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def forward_position_request_to_management(request, request_id):
    """
    HR forwards a position request raised by a Team Lead to a specific manager for approval.
    """
    try:
        hr_id = request.session.get('user_id')
        if not hr_id:
            return Response(
                {"success": False, "message": "HR user not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        hr_reviewer = get_object_or_404(Hr, hr_id=hr_id)
        position_request = get_object_or_404(PositionRequest, request_id=request_id)
        manager_id = request.data.get('manager_id')

        if not manager_id:
            return Response(
                {"success": False, "message": "Manager ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Change the lookup to use 'id' instead of 'manager_id'
        manager = get_object_or_404(Manager, id=manager_id)

        if position_request.status != 'pending':
            return Response(
                {"success": False, "message": f"Request is in '{position_request.status}' status, not 'pending'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not position_request.requested_by:
            return Response(
                {"success": False, "message": "Request must be raised by a Team Lead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        position_request.hr_reviewer = hr_reviewer
        position_request.manager_approver = manager
        position_request.status = 'hr_review'
        position_request.save()
        return Response(
            {
                "success": True,
                "message": f"Request forwarded to manager with ID {manager.manager_id}.",
                "manager_id": manager.manager_id
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
def approve_position_request(request, request_id):
    """
    Manager approves or rejects a position request assigned to them.
    """
    try:
        manager_id = request.session.get('user_id')
        if not manager_id:
            return Response(
                {"success": False, "message": "Manager not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        manager = get_object_or_404(Manager, manager_id=manager_id)
        position_request = get_object_or_404(PositionRequest, request_id=request_id)
        action = request.data.get('action')

        if position_request.status != 'hr_review':
            return Response(
                {"success": False, "message": f"Request is in '{position_request.status}' status, not 'hr_review'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if position_request.manager_approver != manager:
            return Response(
                {"success": False, "message": "You are not assigned to approve this request."},
                status=status.HTTP_403_FORBIDDEN
            )

        if action == 'approve':
            position_request.status = 'approved'
            position_request.approval_date = timezone.now()
            position_request.save()

            vacancy = Vacancy(
                position_request=position_request,
                title=position_request.title,
                location=position_request.location.location_name,
                experience_level=position_request.experience_level,
                job_types=position_request.job_types,
                opening_roles=position_request.opening_roles,
            )
            vacancy.save()
            return Response(
                {
                    "success": True,
                    "message": "Position request approved and vacancy created!",
                    "vacancy_id": vacancy.vacancy_id
                },
                status=status.HTTP_200_OK
            )

        elif action == 'reject':
            position_request.status = 'rejected'
            position_request.save()
            return Response(
                {"success": True, "message": "Position request rejected."},
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"success": False, "message": "Invalid action. Use 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def hr_position_requests(request):
    """
    Fetch position requests assigned to the authenticated HR.
    """
    try:
        hr_id = request.session.get('user_id')
        if not hr_id:
            return Response(
                {"success": False, "message": "HR user not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        hr = get_object_or_404(Hr, hr_id=hr_id)
        position_requests = PositionRequest.objects.filter(hr_reviewer=hr).select_related(
            'location', 'role', 'requested_by', 'hr_reviewer', 'manager_approver'
        )

        serializer = PositionRequestSerializer(position_requests, many=True)
        return Response(
            {
                "success": True,
                "requests": serializer.data
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def manager_position_requests(request):
    """
    Fetch position requests assigned to the authenticated manager.
    """
    try:
        manager_id = request.session.get('user_id')
        if not manager_id:
            return Response(
                {"success": False, "message": "Manager not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        manager = get_object_or_404(Manager, manager_id=manager_id)
        position_requests = PositionRequest.objects.filter(
            manager_approver=manager,
            status='hr_review'
        ).select_related('location', 'role', 'requested_by', 'hr_reviewer', 'manager_approver')

        serializer = PositionRequestSerializer(position_requests, many=True)
        return Response(
            {
                "success": True,
                "requests": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def list_vacancies(request):
    """
    Retrieve all vacancies.
    """
    try:
        vacancies = Vacancy.objects.all().select_related('position_request__location')
        serializer = VacancySerializer(vacancies, many=True)
        return Response(
            {"success": True, "vacancies": serializer.data},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"success": False, "error": f"Server error: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
        
        
######################## New User VIEWS After the  change flow ###########################################




from authentication.models import User
from authentication.serializers import UserSerializer

@api_view(['GET'])
def user_employee_emptask(request, user_id): 
    """
    GET request to fetch tasks assigned to a specific user by their user_id.
    Only users with designation 'Employee' are eligible.
    """
    try:
        # Get the user
        user = User.objects.get(user_id=user_id)

        # Validate designation
        if user.designation != 'Employee':
            return Response({'error': 'User is not an employee'}, status=status.HTTP_403_FORBIDDEN)

        # Fetch tasks assigned to the user
        tasks = employee_task.objects.filter(assigned_to=user)

        task_data = [
            {
                'task_id': task.id,
                'task_name': task.task_name,
                'task_description': task.task_description,
                'deadline': task.deadline,
                'status': task.emp_taskstatus
            }
            for task in tasks
        ]

        return Response({'tasks': task_data}, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: {e}")
        return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    

@api_view(['POST'])
def create_team(request):
    try:
        team_name = request.data['team_name']
        project_name = request.data['project_name']
        team_task = request.data['team_task']
        manager_name = request.data['manager']
        team_leader_username = request.data['team_leader']
        members_usernames = request.data['members']

        # Fetch related objects using correct models and fields
        project = get_object_or_404(Project, name=project_name)
        manager = get_object_or_404(Manager, manager_name=manager_name)
        team_leader = get_object_or_404(User, username=team_leader_username)  # Changed to User model
        
        print("team_leader type:", type(team_leader))  # Should be <class 'yourapp.models.User'>
        print("team_leader instance:", team_leader)
        print("team_leader is User instance?", isinstance(team_leader, User))

        # Create the team
        team = Team(
            team_name=team_name,
            project=project,
            team_task=team_task,
            manager=manager,
            team_leader=team_leader,
        )
        team.save()

        # Fetch member User instances by username
        member_objects = User.objects.filter(username__in=members_usernames)
        if len(member_objects) != len(members_usernames):
            missing_members = set(members_usernames) - set(member.username for member in member_objects)
            return Response(
                {"success": False, "error": f"Some members not found: {', '.join(missing_members)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        team.members.set(member_objects)

        return Response({"success": True, "message": "Team created successfully!"}, status=status.HTTP_201_CREATED)

    except KeyError as e:
        return Response({"success": False, "error": f"Missing required field: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def view_my_teams(request):
    manager_username = request.session.get('user')

    if not manager_username:
        return Response({"success": False, "message": "Manager not found in session."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Use existing Manager model (since manager logic is untouched)
        manager = Manager.objects.get(username=manager_username)

        # Fetch teams managed by this manager
        teams = Team.objects.filter(manager=manager)

        team_data = [
            {
                "team_id": team.team_id,
                "team_name": team.team_name,
                "project_name": team.project.name,
                "team_task": team.team_task,
                "manager": team.manager.username,
                "team_leader": {
                    "id": team.team_leader.id,
                    "username": team.team_leader.username,
                    "name": team.team_leader.user_name
                } if team.team_leader else None,
                "members": [
                    {
                        "id": member.id,
                        "username": member.username,
                        "name": member.user_name
                    } for member in team.members.all()
                ]
            }
            for team in teams
        ]

        return Response({"success": True, "teams": team_data}, status=status.HTTP_200_OK)

    except Manager.DoesNotExist:
        return Response({"success": False, "message": "Manager not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)