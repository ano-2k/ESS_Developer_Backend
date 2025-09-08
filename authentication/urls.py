from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #urls for Admin
    path('', views.index, name='index'),
    path('api/details/', views.details, name='details'),
    path('admin/logout/', views.user_logout, name='user_logout'),
    path('admin/forgot_password/', views.forgot_password, name='forgot_password'),
    path('admin/reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('admin_home/', views.custom_admin_home, name='custom_admin_home'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('employee_dashboard/', views.employee_dashboard, name='employee_dashboard'),
    # #CRUD Operations for Admin
   path('admin/managers/add/', views.add_manager, name='add_manager'),
    path('admin/managers/<str:id>/', views.update_manager, name='update_manager'),
    path('admin/managers/delete/<str:id>/', views.delete_manager, name='delete_manager'),
    path('api/managers/get/<str:id>/', views.view_manager_by_id, name='view_manager_by_id'),
    path('admin/supervisor/add/', views.add_supervisor, name='add_supervisor'),
    path('admin/supervisor/<str:id>/', views.update_supervisor, name='update_supervisor'),
    path('admin/supervisor/delete/<str:id>/', views.delete_supervisor, name='delete_supervisor'),
    path('api/employees/get/<str:id>/', views.view_employee_by_id, name='view_employee_by_id'),
    path('api/employee_list/', views.employee_list, name='employee_list'),
    path('admin/employees/add/', views.add_employee, name='add_employee'),
    path('admin/employees/<str:id>/', views.update_employee, name='update_employee'),
    path('admin/employees/delete/<str:id>/', views.delete_employee, name='delete_employee'),
    path('api/get-hrs/<str:id>/', views.view_hr_by_id, name='view_hr_by_id'),
    path('admin/departments/', views.add_department, name='add_department'),
    path('admin/departments/<int:id>/', views.update_department, name='update_department'),
    path('admin/departments/delete/<int:id>/', views.delete_department, name='delete_department'),

    path('admin/shifts/', views.add_shift, name='add_shift'),
    path('admin/shifts/<int:id>/', views.update_shift, name='update_shift'),
    path('admin/shifts/delete/<int:id>/', views.delete_shift, name='delete_shift'),

    path('admin/locations/', views.add_location, name='add_location'),
    path('admin/locations/<int:id>/', views.update_location, name='update_location'),
    path('admin/locations/delete/<int:id>/', views.delete_location, name='delete_location'),

    # urls for Managers & Employees 
    path('common_login/', views.common_user_login, name='common_user_login'),
   
    path('manager/forgot_password/', views.forgot_password_manager, name='forgot_password_manager'),
    path('manager/reset_password/<str:token>/', views.reset_password_manager, name='reset_password_manager'),
    path('supervisor/forgot_password/', views.forgot_password_supervisor, name='forgot_password_supervisor'),
    path('supervisor/reset_password/<str:token>/', views.reset_password_supervisor, name='reset_password_supervisor'),
    path('employee/forgot_password/', views.forgot_password_employee, name='forgot_password_employee'),
    path('employee/reset_password/<str:token>/', views.reset_password_employee, name='reset_password_employee'),
    path('api/employees/', views.view_employee_profile, name='view_employee_profile'),
    path('api/employees/<str:id>/update/', views.update_employee_profile, name='update_employee_profile'),
    path('api/managers/<str:id>/', views.view_manager_profile, name='view_manager_profile'),
    path('api/managers/<str:id>/update', views.update_manager_profile, name='update_manager_profile'),
    path('api/manager/view_employee/', views.manager_view_employee_profile, name='manager_view_employee_profile'),
    path('admin_view_employee_profile/<str:employee_id>/', views.admin_view_employee_profile, name='admin_view_employee_profile'),
    path('admin_view_manager_profile/<str:manager_id>/', views.admin_view_manager_profile, name='admin_view_manager_profile'),

    path('supervisor_dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('api/supervisor/get/<str:id>/', views.view_supervisor_by_id, name='view_supervisor_by_id'),
    path('api/supervisor/<str:id>/update/', views.update_supervisor_profile, name='update_supervisor_profile'),
    
    path('md/home/', views.md_home, name='md_home'),
    path('md/add_manager/', views.md_add_manager, name='md_add_manager'),
    path('md/add_supervisor/', views.md_add_supervisor, name='md_add_supervisor'),
    path('md/add_employee/', views.md_add_employee, name='md_add_employee'),
    path('md/add_department/', views.md_add_department, name='md_add_department'),
    path('md/add_shift/', views.md_add_shift, name='md_add_shift'),
    path('md/add_location/', views.md_add_location, name='md_add_location'),
    path('md/delete_manager/<str:manager_id>/', views.md_delete_manager, name='md_delete_manager'),
    path('md/delete_employee/<str:employee_id>/', views.md_delete_employee, name='md_delete_employee'),
    path('md/delete_department/<str:department_id>/', views.md_delete_department, name='md_delete_department'),
    path('md/delete_shift/<str:shift_number>/', views.md_delete_shift, name='md_delete_shift'),
    path('md/delete_location/<str:location_id>/', views.md_delete_location, name='md_delete_location'),
    path('md/update_manager/<int:id>/', views.md_update_manager, name='md_update_manager'),
    path('md/update_employee/<int:id>/', views.md_update_employee, name='md_update_employee'),
    path('md/update_department/<int:id>/', views.md_update_department, name='md_update_department'),
    path('md/update_shift/<int:id>/', views.md_update_shift, name='md_update_shift'),
    path('md/update_location/<int:id>/', views.md_update_location, name='md_update_location'),
    path('md/forgot_password_md/', views.forgot_password_md, name='forgot_password_md'),
    path('md/reset_password_md/<token>/', views.reset_password_md, name='reset_password_md'),

    # hr all function urls
    
    path('api/hr_list/', views.hr_list, name='hr_list'),
    path('admin/hrs/add/', views.add_hr, name='add_hr'),
    path('admin/hrs/<str:id>/', views.update_hr, name='update_hr'),
    path('admin/hrs/delete/<str:id>/', views.delete_hr, name='delete_hr'),
    path('hr_dashboard/', views.hr_dashboard, name='hr_dashboard'),
     path('admin/hr_forgot_password/', views.hr_forgot_password, name='hr_forgot_password'),
    path('admin/hr_reset_password/<str:token>/', views.hr_reset_password, name='hr_reset_password'),
    path('api/hrs/<str:id>/update', views.update_hr_profile, name='update_hr_profile'),  
        
    #AR ALL FUNCTION URLS 

    path('api/ar_list/', views.ar_list, name='ar_list'),
    path('admin/ars/add/', views.add_ar, name='add_ar'),
    path('admin/ars/<str:id>/', views.update_ar, name='update_ar'),
    path('admin/ars/delete/<str:id>/', views.delete_ar, name='delete_ar'),
    path('ar_dashboard/', views.ar_dashboard, name='ar_dashboard'),
     path('admin/ar_forgot_password/', views.ar_forgot_password, name='ar_forgot_password'),
    path('admin/ar_reset_password/<str:token>/', views.ar_reset_password, name='ar_reset_password'),
    path('api/ars/<str:id>/update', views.update_ar_profile, name='update_ar_profile'),  
    path('api/get-ars/<str:id>/', views.view_ar_by_id, name='view_ar_by_id'),    
    

    # #forgot/reset password for md
    path('requests/add/', views.add_request, name='add_request'),
    path('requests/supervisor/', views.supervisor_view_allrequest, name='supervisor_view_allrequest'),
    path('requests/admin/', views.admin_view_request, name='admin_view_request'),
    
    path('todos/', views.todo_list, name='todo_list'),              # GET: List all Todos
    path('todos/create/', views.todo_create, name='todo_create'),   # POST: Create a new Todo
    path('todos/toggle/<int:id>/', views.todo_toggle, name='todo_toggle'),  # PATCH: Toggle Todo
    path('todos/delete/<int:id>/', views.todo_delete, name='todo_delete'),  # DELETE: Delete Todo
    path('news/send/', views.send_news, name='send_news'),
    path('news/view/', views.view_news, name='view_news'),
    path('news/update_news/<int:id>/', views.update_news, name='update_news'),
    path('news/delete_news/<int:id>/', views.delete_news, name='delete_news'),
    path('tickets/', views.self_all_service, name='self_service'),
    path('tickets/add/', views.add_ticket, name='add_ticket'),
    path('requests/', views.self_request, name='self_request'),
    path('admin/get-departments/<int:id>/', views.get_department, name='get_department'),
    
    # All get functions
    path('todos/<int:id>', views.todo_list, name='todo_list'), 
    # path('news/view/', views.view_news, name='view_news'),
    path('tickets/<int:id>', views.self_service, name='self_service'),
     
    path('api/manager_list/', views.manager_list, name='manager_list'),
    path('api/employee_list/', views.employee_list, name='employee_list'),
    path('api/supervisor_list/', views.supervisor_list, name='supervisor_list'),
    path('api/admin_list/', views.admin_list, name='admin_list'),  
       
      
    #   ADMIN SHOW DETAILS
    path('admin/show-departments/<int:id>', views.show_department, name='show_department'),
    path('admin/overall-departments/', views.overall_department, name='overall_department'),
    path('admin/departmentss/', views.overall_department, name='overall_department'),
    path('admin/show-shift/<int:id>', views.show_shift, name='showshift'),
    path('admin/show-shift/', views.overall_shift, name='overall_shift'),
    path('admin/shifts/', views.overall_shift, name='overall_shift'),
    path('admin/overall-location/', views.overall_location, name='overall_overall'),
    path('admin/show-location/<int:id>/', views.show_location, name='show_location'),
          
        #   MD SHOW DETAILS
     path('MD/show-departments/<int:id>', views.md_show_department, name='md_show_department'),
      path('MD/overall-departments/', views.md_show_overall_department, name='md_show_overall_department'),
      path('MD/show-shift/<int:id>', views.md_show_shift, name='showshift'),
      path('MD/show-shift/', views.md_show_overall_shift, name='md_show_overall_shift'),
      path('MD/overall-location/', views.md_show_overall_location, name='md_show_overall_location'),
      path('MD/show-location/<int:id>', views.md_show_location, name='md_show_location'),
      path('api/md/md_manager_list/', views.md_manager_list, name='md_manager_list'),
      path('api/md/md_employee_list/', views.md_employee_list, name='md_employee_list'),
      path('api/md/md_supervisor/', views.md_supervisor_list, name='md_supervisor_list'),
      
      path('api/md/employees/<str:id>/', views.md_view_employee_profile, name='md_view_employee_profile'),
      path('api/md/managers/<str:id>/', views.md_view_manager_profile, name='md_view_employee_profile'),
      path('api/md/supervisors/<str:id>/', views.md_view_supervisor_profile, name='md_view_employee_profile'),
      path('requests/supervisor/<str:user_id>/', views.supervisor_view_all_request, name='supervisor_view_allrequest'),


      #hr
      path('hiring/', views.hiring_list_create, name='hiring-list-create'),
      path('hiring/<int:id>/', views.hiring_detail, name='hiring-detail'),
      path('hiring/update_status/<int:id>/', views.update_hiring_status, name='update-hiring-status'),
      path("generate-job-description/", views.generate_job_description, name="generate_job_description"),
      path('chatbot/', views.hr_chatbot, name="hr_chatbot"),
      path('extract-pdf/', views.extract_pdf_content, name='extract_pdf'),


      path('api/admin/<str:user_id>/features/', views.get_admin_features, name='get_admin_features'),
      path('api/admin/<str:user_id>/features/update/', views.update_admin_features, name='update_admin_features'),
      
      #check employee is a team leader or not 
      path('check_team_leader/', views.check_team_leader, name='check_team_leader'),
      
      #Job Alert Hr Flow 
      path('job_alert/create/<str:hr_id>/', views.create_job_alert, name='create_job_alert'),
      path('job_alert/update/<str:job_id>/', views.update_job_alert, name='update_job_alert'),
      path('job_alert/delete/<str:job_id>/', views.delete_job_alert, name='delete_job_alert'),
      path('job_alerts/<str:hr_id>/', views.get_job_alerts, name='get_job_alerts'),
      
      #Candidate Hr Flow 
      path('candidate/create/<str:hr_id>/', views.create_candidate, name='create_candidate'),
      path('candidate/update/<str:c_id>/', views.update_candidate, name='update_candidate'),
      path('candidate/delete/<str:c_id>/', views.delete_candidate, name='delete_candidate'),
      path('candidates/<str:hr_id>/', views.get_candidates, name='get_candidates'),
      
      ######################## New User URLS After the  change flow ###########################################

      path('api/users_list/', views.user_list, name='user_list'),
      path('admin/add_user/', views.add_user, name='add_user'),
      
      path('user/common_login/', views.common_users_login, name='common_users_login'), #working 
      path('user/details/', views.user_details, name='user_details'), #working 
    #   path('user/user-employee-dashboard/<str:user_id>/', views.user_employee_dashboard, name='user_employee_dashboard'),
    
      path('user/user-dashboard/<str:user_id>/', views.user_dashboard, name='user_dashboard'), #combined view for emp,sup,hr dashboard
      path('user/<str:user_id>/verify_team_leader/', views.verify_team_leader, name='verify_team_leader'),
      
  # Super Admin
  
     path('api/superadmin/<str:user_id>/superadmin-features/', views.get_superadmin_features, name='get_superadmin_features'),
     path('api/superadmin/<str:user_id>/update-superadmin-features/', views.update_superadmin_features, name='update_superadmin_features'),
  
  # Update User (PUT / PATCH)
    path('users/update/<str:id>/', views.update_user, name='update_user'),

    # Delete User
    path('users/delete/<str:id>/', views.delete_user, name='delete_user'),

    # Forgot Password (Send Reset Email)
    path('users/forgot_password/', views.forgot_password_user, name='forgot_password_user'),

    # Reset Password (Verify Token & Set New Password)
    path('users/reset_password/<str:token>/', views.reset_password_user, name='reset_password_user'),

      
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
