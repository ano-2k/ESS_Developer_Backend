from django.urls import path
from . import views 

urlpatterns = [
    path('create-performance-review/', views.create_performance_review, name='create_performance_review'),
    path('api/performance-review/list/', views.performance_review_list, name='performance_review_list'),
    path('performance-reviews/<int:review_id>/', views.performance_review_detail, name='performance_review_detail'),
     path('performance-reviews/<int:review_id>/update/', views.update_performance_review, name='update_performance_review'),
    path('performance-reviews-delete/<int:id>/', views.delete_performance_review, name='delete_performance_review'),


    path('api/goal/create/', views.create_goal, name='create_goal'),
    path('api/goal/list/', views.goal_list, name='goal_list'),
    path('goals/<int:goal_id>/', views.goal_detail, name='goal_detail'),
    path('goals/<int:goal_id>/update/', views.update_goal, name='update_goal'),  # Update a specific goal
    path('goals-delete/<int:id>/', views.delete_goal, name='delete_goal'),  # Delete a specific goal


    path('api/feedback/create/', views.create_feedback, name='create_feedback'),
    path('api/feedback/list/', views.feedback_list, name='feedback_list'),
    path('feedbacks/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),  # Retrieve a feedback by ID
    path('feedbacks/<int:feedback_id>/update/', views.employee_update_feedback, name='employee_update_feedback'),  # Update feedback by ID
    path('admin/delete-feedback/<int:feedback_id>/', views.admin_delete_employee_feedback, name='delete_feedback'),  # Delete feedback by ID
################
    path('api/kpi_dashboard/', views.kpi_dashboard, name='kpi_dashboard'),
    path('kpi-dashboard/<int:employee_id>/', views.kpi_dashboard_detail, name='kpi_dashboard_detail'),#added

    path('kpi-dashboard/employee/', views.kpi_dashboard_employee_request, name='kpi_dashboard_employee_request'),#added
    path('api/kpi_dashboard_employee/<int:employee_id>/', views.kpi_dashboard_employee, name='kpi_dashboard_employee'),

    path('api/kpi_dashboard_admin/', views.kpi_dashboard_admin, name='kpi_dashboard_admin'),
    path('kpi-dashboard/admin/task/<int:task_id>/', views.kpi_detail_task, name='kpi_detail_task'),#added
####################
    path('performance_review_list_employee/<str:employee_name>/', views.performance_review_list_employee, name='performance_review_list_employee'),
    path('performance-reviews/', views.performance_review_list_request, name='performance_review_list_request'),#added
    
    path('view_goal_employee/<str:employee_name>/', views.view_goal_employee, name='view_goal_employee'),
    path('goals/', views.view_goal_employee_request, name='view_goal_employee_request'),#added
    
    path('view_feedback_employee/<str:id>/', views.view_feedback_employee, name='view_feedback_employee'),
    path('feedback/', views.view_feedback_employee_request, name='view_feedback_employee_request'),#added
  #########################3

    
      # URL for creating a performance review
    path('reviews/', views.create_performance_review_manager, name='create_performance_review_manager'),
    
    # URL for updating a specific performance review by review_id
    path('update-reviews/<int:review_id>/', views.update_performance_review_manager, name='update_performance_review_manager'),
     path('delete_performance_review_manager/<int:id>/',views. delete_performance_review_manager, name='delete_performance_review_manager'),
    path('admin/get_performance_review_all/', views.get_performance_review_all, name='get_performance_reviews_all'),
    # URL for getting all performance reviews for a specific manager by manager_id
    path('manager/<int:manager_id>/reviews/', views.get_performance_reviews_for_manager, name='get_performance_reviews_for_manager'),
    
       # URL for getting all performance reviews for a manager by manager ID
    path('manager/<int:manager_id>/reviews/', views.get_performance_reviews_for_manager, name='get_performance_reviews_for_manager'),
     path('delete_admin_feedback/<int:id>/', views.delete_admin_feedback, name='delete_admin_feedback'),#added
    # URL for getting a specific performance review by its ID
    path('get-reviews/<int:review_id>/', views.get_performance_review_by_id, name='get_performance_review_by_id'),
    
    path('performance-reviews-manager/', views.performance_review_manager_request, name='performance_review_manager_request'),#added
    ###############################
    path('api/create_goal_manager/', views.create_goal_manager, name='create_goal_manager'),

    # Update a manager goal by its ID using PUT method
    path('update-goal/<int:goal_id>/', views.update_manager_goal, name='update_manager_goal'),

    # Delete a manager goal by its ID using DELETE method
    path('delete-goal/<int:goal_id>/',views. delete_manager_goal, name='delete_manager_goal'),

    # Retrieve a specific manager goal by its ID using GET method
    path('delete-goal/<int:id>/',views. get_manager_goal, name='get_manager_goal'),

    # Retrieve all goals for a specific manager using GET method
    path('get-goals/',views. get_all_manager_goals, name='get_all_manager_goals'),
    
    path('get-manager-goal-all/',views. get_manager_goal_all, name='get_manager_goal_all'),
############################################################################

    # Retrieve a specific manager feedback by its ID using GET method
    
    path('api/view_manager_reviews/', views.view_manager_reviews, name='view_manager_reviews'),
    path('reviews/manager/id/<int:review_id>/', views.get_manager_review_by_id, name='get_manager_review_by_id'),#added
    
    path('api/view_manager_goals/', views.view_manager_goals, name='view_manager_goals'),
    path('goals/manager/id/<int:id>/', views.get_manager_goal_by_id, name='get_manager_goal_by_id'), #added
    path('api/create_feedback_manager/', views.create_feedback_manager, name='create_feedback_manager'),
    path('api/view_manager_feedbacks/', views.view_manager_feedbacks, name='view_manager_feedbacks'),
    path('feedbacks/manager/<int:id>/', views.get_manager_feedback_by_id, name='get_manager_feedback_by_id'),#added
    
    path('api/view_create_performance_review_manager/<str:manager_name>/', views.view_create_performance_review_manager, name='view_create_performance_review_manager'),
    path('performance-reviews/manager/id/<int:review_id>/', views.get_manager_performance_review_by_id, name='get_manager_performance_review_by_id'),#added url
    path('admin/update-manager-goal/<int:goal_id>/', views.update_manager_goal, name='update_manager_goal'),
    path('api/view_create_goal_manager/<str:manager_name>/', views.view_create_goal_manager, name='view_create_goal_manager'),
    path('goals-manager/<int:id>/', views.get_manager_goal_by_id, name='get_manager_goal_by_id'), #added url
    
    
    path('api/view_create_feedback_manager/<str:manager_name>/', views.view_create_feedback_manager, name='view_create_feedback_manager'),
    # path('feedback/manager/id/<int:feedback_id>/', views.get_manager_feedback_by_id, name='get_manager_feedback_by_id'), #added url
    
    path('api/feedback_form/', views.feedback_form, name='feedback_form'),
    path('feedback/form/<int:user_id>/', views.get_feedback_form_by_id, name='get_feedback_form_by_id'),#added url
    
     path('update_manager_feedback/<int:id>/', views.update_manager_feedback, name='update_manager_feedback'),
    
    path('api/submit_feedback/', views.submit_feedback, name='submit_feedback'),
       # Update feedback by its ID using PUT method
    path('update-feedback/<int:feedback_id>/', views.update_feedback, name='update_feedback'),

    # Delete feedback by its ID using DELETE method
    # path('delete-feedback/<int:feedback_id>/',views. delete_feedback, name='delete_feedback'),
    path('delete_manager_feedback/<int:id>/', views.delete_manager_feedback, name='delete_manager_feedback'),#added
    # Retrieve a specific feedback by its ID using GET method
    path('get-feedback/<int:feedback_id>/', views.get_feedback_by_id, name='get_feedback_by_id'),

    # Retrieve all feedback for a specific employee or manager using GET method
    path('get-feedback/', views.get_feedback_for_person, name='get_feedback_for_person'),
    
    
    
    
    path('api/admin_feedback_dashboard/', views.admin_feedback_dashboard, name='admin_feedback_dashboard'),
    path('feedback/<int:feedback_id>/', views.get_feedback_by_id, name='get_feedback_by_id'), #added url
    
    
##############################
    path('api/update_feedback_status/<int:feedback_id>/', views.update_feedback_status, name='update_feedback_status'),
      # Update feedback by its ID using PUT method
    path('update-feedback/<int:feedback_id>/',views. update_feedback, name='update_feedback'),

    # Delete feedback by its ID using DELETE method
    # path('delete-feedback/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),

    # Retrieve a specific feedback by its ID using GET method
    path('get-feedback/<int:feedback_id>/', views.get_feedback_by_id, name='get_feedback_by_id'),

    # Retrieve all feedback for a specific employee or manager using GET method
    path('get-feedback/', views.get_feedback_for_person, name='get_feedback_for_person'),
    
    #################
    
    path('api/update_goal/<int:goal_id>/', views.update_employee_goal, name='update_employee_goal'),
       # Retrieve an employee's goal using GET method
    path('employee-goal/<int:goal_id>/', views.get_employee_goal, name='get_employee_goal'),

    # Update an employee's goal using PUT method
    path('update-employee-goal/<int:goal_id>/',views. update_employee_goal, name='update_employee_goal'),

    # Delete an employee's goal using DELETE method
    path('delete-employee-goal/<int:goal_id>/',views. delete_employee_goal, name='delete_employee_goal'),
     # Retrieve all goals for a specific employee by their employee_id using GET method
    path('employee-goals/<int:employee_id>/', views.get_all_employee_goals, name='get_all_employee_goals'),
    
    ###############################
    
    path('api/update_manager_goal/<int:goal_id>/', views.update_manager_goal, name='update_manager_goal'),
     # Retrieving a manager goal using GET method
    path('manager-goal/<int:goal_id>/', views.get_manager_goal, name='get_manager_goal'),

    # Updating a manager goal using PUT method
    path('update-manager-goal/<int:goal_id>/', views.update_manager_goal, name='update_manager_goal'),

    # Deleting a manager goal using DELETE method
    path('delete-manager-goal/<int:goal_id>/',views. delete_manager_goal, name='delete_manager_goal'),
      # Retrieve all goals for a specific manager using GET method
    path('manager-goals/<int:manager_id>/', views.get_all_manager_goals, name='get_all_manager_goals'),
    
    ######################################
    
    path('api/check_if_manager/', views.check_if_manager, name='check_if_manager'),
      # Checking if a user is a manager using GET method
    path('check-if-manager/<str:username>/', views.check_if_manager, name='check_if_manager'),

    # Updating a manager's details using PUT method
    path('update-manager/<int:manager_id>/', views.update_manager, name='update_manager'),

    # Deleting a manager using DELETE method
    path('delete-manager/<int:manager_id>/', views.delete_manager, name='delete_manager'),

    # Retrieving a manager's details using GET method
    path('get-manager/<int:manager_id>/',views. get_manager, name='get_manager'),
    ]
