from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('emp_check_in/', views.emp_check_in, name='check_in'),
    path('emp_check_out/', views.emp_check_out, name='check_out'),


    path('assigned_task/', views.assigned_task, name='assigned_task'),
    path('assigned-task/<int:task_id>/', views.assigned_task_by_id, name='assigned_task_by_id'),  # New URL for GET by ID
     
     
    path('assigned_manager_task/', views.assigned_manager_task, name='assigned_manager_task'),
       path('assigned-manager-task/<int:task_id>/', views.assigned_manager_task_by_id, name='assigned_manager_task_by_id'),  # New URL for GET by ID

    
    path('create-project/', views.create_project, name='create_project'),
    path('edit-project/<str:id>/', views.edit_project, name='edit_project'),
    path('show-project-status/<str:project_id>/', views.show_project_status, name='show_project_status'),
    path('projects/',views.list_all_projects, name='list_all_projects'),
    path('delete_project/<str:id>/', views.delete_project, name='delete_project'),
    path('project/<str:project_id>/', views.get_project_by_id, name='get_project_by_id'),
    
    path('create-task/', views.create_task, name='create_task'),
    path('delete_task/<str:id>/', views.delete_task, name='delete_task'),
    path('edit-task/<str:id>/', views.edit_task, name='edit_task'),
    path('show-my-tasks/', views.show_my_tasks, name='show_my_tasks'),
    path('tasks/<str:task_id>/', views.get_task_details, name='get_task_details'),
    path('get-task/',views.list_all_task, name='list_all_task'),# GET


    path('create-role/', views.create_role, name='create_role'),
    path('delete_role/<str:id>/', views.delete_role, name='delete_role'),
    path('edit_role/<str:id>/', views.edit_role, name='edit_role'),
    path('roles/list/',views. list_roles, name='list_roles'),  # GET (All Roles)
    path('roles/<str:id>/',views. get_role_by_id, name='get_role_by_id'),  # GET (Role by ID)
    
    path('create_team/', views.create_team, name='create_team'),
    path('delete_team/<str:team_id>/', views.delete_team, name='delete_team'),
    path('edit_team/<str:team_id>/', views.edit_team, name='edit_team'),
    # path('view-my-teams/', views.view_my_teams, name='view_my_teams'),
    path('teams/', views.get_all_teams, name='get_all_teams'),
    path('teams/<str:team_id>/',views. get_team_by_id, name='get_team_by_id'),  # GET (Team by ID)
    
    
    path('assign-task/', views.assign_task_to_team_member, name='assign_task_to_team'),
    path('show-tasks/<str:user>/', views.show_employee_tasks, name='show_employee_tasks'),
     path('show-employee-task-by-id/<int:user>/<int:task_id>/', views.show_employee_task_by_id, name='show_employee_task_by_id'),  # New URL for GET by ID
    
    path('show-assigned-manager-task/', views.show_assigned_manager_task, name='show_assigned_manager_task'),
    path('show-task-by-id/<int:task_id>/', views.show_task_by_id, name='show_task_by_id'),  # New URL for GET by ID
    
    
    
    path('view-my-emptask/', views.view_my_emptask, name='view_my_emptask'),
    path('view-employee-emptask/<int:employee_id>/', views.view_employee_emptask_by_id, name='view_employee_emptask_by_id'),
    path('delete-emptask/<str:task_name>/', views.delete_emptask, name='delete_emptask'),
    
    
    path('project-manager-dashboard/<str:user>/', views.project_manager_dashboard, name='project_manager_dashboard'),
    path('projects/<int:project_id>/tasks/', views.get_project_tasks, name='get_project_tasks'), 
     # URL for fetching all projects for a specific manager
    path('manager-projects/<str:user_id>/', views.get_manager_projects, name='get_manager_projects'),
    
   
    
    path('update_project_status/<str:project_id>/', views.update_managerproject_status, name='update_project_status'),
      # path('get-project-by-id/<str:project_id>/', views.get_project_by_id, name='get_project_by_id'),
    path('get-projects-by-status/<str:status_filter>/', views.get_projects_by_status, name='get_projects_by_status'),
    
    path('kanban/', views.kanban_dashboard, name='kanban_dashboard'),
    path('kanban-dashboard/', views.kanban_dashboard_all, name='kanban_dashboard_all'),
    path('kanban-dashboard/<str:status_name>/', views.kanban_dashboard_by_status, name='kanban_dashboard_by_status'),

    path('update_project_status/', views.update_project_status, name='update_project_status'),
    path('get_projects', views.get_projects, name='get_projects'),
    path('get_tasks/',views.get_tasks,name='get_tasks'),
    path('get_employeetasks/',views.get_employeetasks,name='get_employeetasks'),
    path('update_taskstatus/',views.update_task_status,name='update_task_status'),
    path('update_employeetaskstatus/',views.update_employeetask_status,name='update_employeetask_status'),
    path('update_project_status/',views.update_project_status,name='update_project_status'),


    path('get_project_data/', views.get_project_data, name='get_project_data'),
     path('projects/<str:project_id>/', views.get_project_details, name='get_project_details'),  # GET
    path('projects/active/', views.list_active_projects, name='list_active_projects'),  # GET
    
    
    
    path('upload_document/<str:task_id>/', views.upload_document, name='upload_document'),
    path('upload_document_emp/<str:id>/', views.upload_document_emp, name='upload_document_emp'),
     path('tasks/<int:task_id>/documents/', views.get_task_documents, name='get_task_documents'),  # GET
    path('employee-tasks/<int:id>/documents/',views. get_employee_task_documents, name='get_employee_task_documents'),  # GET
    path('admin/documents/', views.admin_view_documents, name='admin_view_documents'), #no 

    path('show_performance_employee/<str:username>/', views.employee_performance_view, name='show_performance_employee'), #2 get
    path('employee/performance/<str:username>/', views.get_employee_performance, name='get_employee_performance'),
    path('employees/performance/', views.get_all_employees_performance, name='get_all_employees_performance'),

    path('show_performance_manager/<str:username>/', views.manager_performance_view, name='show_performance_manager'), #2 get
    path('manager/performance/<str:username>/', views.get_manager_performance, name='get_manager_performance'),
    path('managers/performance/', views.get_all_managers_performance, name='get_all_managers_performance'),


    path('create_training_program/', views.create_training_program, name='create_training_program'),
    path('create_training_progress/', views.create_training_progress, name='create_training_progress'),
    path('training_programs/', views.list_training_programs, name='training_programs'), #2 get
    path('training/programs/<int:program_id>/', views.get_training_program_details, name='get_training_program_details'),#added url
    path('enroll_participant/', views.enroll_participant, name='enroll_participant'),   #2 get

    path('training_progress/', views.view_training_progress, name='training_progress'),# 2 get
    path('training/progress/<str:username>/', views.view_employee_training_progress, name='view_employee_training_progress'),

    

    path('update_program/<str:program_id>/', views.update_program, name='update_program'),
    path('delete_program/<str:program_id>/', views.delete_program, name='delete_program'), 
    path('delete_certificate/<str:id>/', views.delete_certificate, name='delete_certificate'),# 2 get
    path('training/programs/category/<str:category>/', views.list_training_programs_by_category, name='list_training_programs_by_category'), #added
    path('training/programs/name/<str:program_id>/', views.get_training_program_by_name, name='get_training_program_by_name'),#added

    path('update_progress/<str:id>/', views.update_progress, name='update_progress'),
    path('update_certificate/<str:id>/', views.update_certificate, name='update_certificate'),
    path('delete_progress/<str:id>/', views.delete_progress, name='delete_progress'), # 2 get
    path('get-training/progress/program/<str:id>/', views.list_progress_by_program, name='list_progress_by_program'),#added
    path('training/progress/<str:username>/<str:program_name>/', views.get_user_progress_by_program, name='get_user_progress_by_program'),#added

    path('upload_certificate/', views.upload_certificate, name='upload_certificate'), #2get
    path('certificates/', views.list_certificates, name='list_certificates'),#added
    path('certificates/<int:id>/', views.get_certificate_by_id, name='get_certificate_by_id'),#added

    path('employee_dashboard_certificates/<str:username>/', views.employee_dashboard_certificates, name='employee_dashboard_certificates'),#2 get
    path('certificates/employee/<str:username>/', views.list_employee_certificates, name='list_employee_certificates'),
    path('certificates/employee/<str:username>/<str:program_name>/', views.get_employee_certificate_by_program, name='get_employee_certificate_by_program'),

    path('manager_dashboard_certificates/', views.manager_dashboard_certificates, name='manager_dashboard_certificates'),#2get
    path('certificates/manager/<str:manager_username>/', views.list_certificates_by_manager, name='list_certificates_by_manager'),#added
    path('certificates/manager/<str:manager_username>/employee/<str:employee_username>/', views.get_manager_certificates_by_employee, name='get_manager_certificates_by_employee'),#added

    path('enroll_training_manager/', views.enroll_training_manager, name='enroll_training_manager'), #2get
    path('training/manager-programs/', views.list_manager_training_programs, name='list_manager_training_programs'),#added
    path('training/manager-programs/<int:program_id>/', views.get_manager_training_program_by_id, name='get_manager_training_program_by_id'),#added

    path('enroll_training_employee/', views.enroll_training_employee, name='enroll_training_employee'),#2get
    path('training/employee-programs/', views.list_employee_training_programs, name='list_employee_training_programs'),
    path('training/employee-programs/<int:program_id>/', views.get_employee_training_program_by_id, name='get_employee_training_program_by_id'),#added

    path('enroll_manager/', views.enroll_manager, name='enroll_manager'),
    path('training/manager/enrollments/<str:manager_username>/', views.list_manager_enrollments, name='list_manager_enrollments'),#added
    path('training/manager/enrollment/<str:manager_username>/<int:program_id>/', views.get_manager_enrollment_details, name='get_manager_enrollment_details'),#added

    path('enroll_employee/', views.enroll_employee, name='enroll_employee'),
    path('training/employee/enrollments/<str:employee_username>/', views.list_employee_enrollments, name='list_employee_enrollments'),#added
    path('training/employee/enrollment/<str:employee_username>/<int:program_id>/', views.get_employee_enrollment_details, name='get_employee_enrollment_details'),#added

    path('performance_chart/', views.performance_chart_view, name='performance_chart'),
    path('performance/employee/<str:employee_id>/', views.get_employee_performance, name='get_employee_performance'),#added
    path('performance/manager/<str:manager_id>/', views.get_manager_performance, name='get_manager_performance'),#added

    path('task_check_in/', views.task_check_in, name='task_check_in'),
    path('task_check_out/', views.task_check_out, name='task_check_out'),
    path('task/employee/active/<str:employee_id>/', views.get_employee_active_task, name='get_employee_active_task'),#added
    path('task/manager/active/<str:manager_id>/', views.get_manager_active_task, name='get_manager_active_task'),#added
    
    
    path('md_create_project/', views.md_create_project, name='md_create_project'),
    path('md_edit_project/<str:project_id>/', views.md_edit_project, name='md_edit_project'),
    path('md_show_project_status/<str:project_id>/', views.md_show_project_status, name='md_show_project_status'),
    path('md_delete_project/<str:project_id>/', views.md_delete_project, name='md_delete_project'),
    path('md/projects/', views.md_list_projects, name='md_list_projects'),#added

    path('md_create_task/', views.md_create_task, name='md_create_task'),
    path('md_edit_task/<str:task_id>/', views.md_edit_task, name='md_edit_task'),
    path('md_delete_task/<str:task_id>/', views.md_delete_task, name='md_delete_task'), 
    path('md/task/details/<int:task_id>/', views.md_show_task_details, name='md_show_task_details'),#added
    path('md/tasks/project/<str:project_name>/', views.md_list_project_tasks, name='md_list_project_tasks'),#added

    path('md_create_role/', views.md_create_role, name='md_create_role'),
    path('md_edit_role/<str:id>/', views.md_edit_role, name='md_edit_role'),
    path('md_delete_role/<str:id>/', views.md_delete_role, name='md_delete_role'), 
    path('md/role/details/<int:id>/', views.md_show_role_details, name='md_show_role_details'),#added
    path('md/roles/', views.md_list_roles, name='md_list_roles'),#added
    
    path('md_create_team/', views.md_create_team, name='md_create_team'),
    path('md_edit_team/<str:team_id>/', views.md_edit_team, name='md_edit_team'),
    path('md_delete_team/<str:team_id>/', views.md_delete_team, name='md_delete_team'),
    path('md/team/details/<int:team_id>/', views.md_show_team_details, name='md_show_team_details'),#added
    path('md/teams/', views.md_list_teams, name='md_list_teams'),#added

    path('md_kanban/', views.md_kanban_dashboard, name='md_kanban_dashboard'),
    path('md/projects/by_manager/<str:manager_name>/', views.md_projects_by_manager, name='md_projects_by_manager'),#added
    path('projects/<str:category>/', views.get_projects_by_category, name='get_projects_by_category'),#added

    path('md_get_projects/', views.md_get_projects, name='md_get_projects'),
    path('md/get/projects/status/<str:status>/', views.md_get_projects_by_status, name='md_get_projects_by_status'),#added

    path('md_get_project_data/', views.md_get_project_data, name='md_get_project_data'),
    path('md/get/project/<int:project_id>/', views.md_get_project_by_id, name='md_get_project_by_id'),#added

    path('md_admin/documents/', views.md_admin_view_documents, name='md_admin_view_documents'),
    path('md/get/document/<int:document_id>/', views.md_get_document_by_id, name='md_get_document_by_id'),#added
    #add get


    path('md_show_performance_employee/<str:username>/', views.md_employee_performance_view, name='md_show_performance_employee'),
    path('md/employee/tasks/<str:username>/', views.md_employee_tasks_view, name='md_employee_tasks_view'),#added

    path('md_show_performance_manager/<str:username>/', views.md_manager_performance_view, name='md_show_performance_manager'),
    path('md/manager/tasks/<str:username>/', views.md_manager_tasks_view, name='md_manager_tasks_view'),#added

    path('md_training_programs/', views.md_create_training_program, name='md_create_training_program'),
    path('md/training-programs/', views.md_get_all_training_programs, name='md_get_all_training_programs'),#added
    path('md/training-programs/<int:program_id>/', views.md_get_training_program_by_id, name='md_get_training_program_by_id'),#added

    path('md_enroll_participant/', views.md_enroll_participant, name='md_enroll_participant'),
    path('enrollments/', views.get_all_enrollments, name='get_all_enrollments'),#added
    path('enrollments/<int:enrollment_id>/', views.get_enrollment_by_id, name='get_enrollment_by_id'),#added


    path('md_training_progress/', views.md_view_training_progress, name='md_training_progress'),

    path('md_update_program/<str:program_id>/', views.md_update_program, name='md_update_program'),
    path('md_delete_program/<str:program_id>/', views.md_delete_program, name='md_delete_program'),
    path('md/training-programs/status/<str:status>/', views.md_get_training_programs_by_status, name='md_get_training_programs_by_status'),#added
    path('md/training-programs/date-range/<str:start_date>/<str:end_date>/', views.md_get_training_programs_by_date_range, name='md_get_training_programs_by_date_range'),#added

    path('md_update_progress/<str:program_name>/', views.md_update_progress, name='md_update_progress'),
    path('md_delete_progress/<str:program_name>/', views.md_delete_progress, name='md_delete_progress'),
    path('md/training-progress/<str:program_name>/', views.md_get_progress_by_program, name='md_get_progress_by_program'),#added
    path('md/training-progress/all/', views.md_get_all_training_progress, name='md_get_all_training_progress'),#added

    path('md_upload_certificate/', views.md_upload_certificate, name='md_upload_certificate'),
    path('md/certificates/user/<str:username>/', views.md_get_certificates_by_user, name='md_get_certificates_by_user'),#added
    path('md/certificates/all/', views.md_get_all_certificates, name='md_get_all_certificates'),#added

    path('md_performance-chart/<str:user_type>/<int:user_id>/', views.md_performance_chart, name='md_performance_chart'),
    path('md/performance/employee/<int:employee_id>/', views.md_employee_performance_chart, name='md_employee_performance_chart'),#added
    path('md/performance/manager/<int:manager_id>/', views.md_manager_performance_chart, name='md_manager_performance_chart'),#added


    path('md_create_performance_review/', views.md_create_performance_review, name='md_create_performance_review'),
    path('md_performance_review_list/', views.md_performance_review_list, name='md_performance_review_list'),
    path('md/performance-reviews/employee/<str:employee_name>/', views.md_employee_performance_reviews, name='md_employee_performance_reviews'),#added

    # Goal Endpoints
    path('md_create_goal/', views.md_create_goal, name='md_create_goal'),
    path('md_goal_list/', views.md_goal_list, name='md_goal_list'),
    path('goals/employee/<int:employee_id>/', views.get_goals_by_employee, name='get_goals_by_employee'),#added

    # Feedback Endpoints
    path('md_create_feedback/', views.md_create_feedback, name='md_create_feedback'),
    path('md_feedback_list/', views.md_feedback_list, name='md_feedback_list'),
    path('feedbacks/employee/<str:employee_id>/', views.get_feedback_by_employee, name='get_feedback_by_employee'),#added
    
    # -------------JULY 10-------------
    path('manager-tasks/<str:manager_id>/', views.list_tasks_for_manager, name='list_tasks_for_manager'),
    path('employee-tasks/<str:manager_id>/', views.list_employee_tasks_by_manager),
    
    # New paths Created For Manpower Plannning 
    path('manpower/raise-position-request/', views.raise_position_request, name='raise_position_request'),
    path('manpower/position-requests/', views.list_position_requests, name='list_position_requests'),
    path('manpower/forward-to-management/<str:request_id>/', views.forward_position_request_to_management, name='forward_position_request_to_management'),
    path('manpower/approve-position-request/<str:request_id>/', views.approve_position_request, name='approve_position_request'),
    path('manpower/vacancies/', views.list_vacancies, name='list_vacancies'),
    path('manpower/hr-position-requests/', views.hr_position_requests, name='hr_position_requests'), 
    path('manpower/manager-position-requests/', views.manager_position_requests, name='manager_position_requests'),
    
     ######################## New User URLS After the  change flow ###########################################
     
     path('user/<str:user_id>/user_employee_tasks/', views.user_employee_emptask, name='user_employee_task'),
     path('view-my-teams/', views.view_my_teams, name='view_my_teams'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
