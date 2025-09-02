from django.urls import path
from .import views

urlpatterns = [
    # Employee attendance
    path('employee/attendance/form/<str:user_id>/', views.employee_attendance_form, name='employee_attendance_form'),
    path('employee/submit-attendance/', views.submit_employee_attendance, name='submit_employee_attendance'),
    path('employee/employee-attendance-history/<str:user_id>/', views.employee_attendance_history, name='employee_attendance_history'),
    path('employee/all-employee-attendance-history/', views.employee_all_attendance_history, name='employee_all_attendance_history'),

    # Manager attendance
    path('manager/attendance/form/<str:user_id>/', views.manager_attendance_form, name='manager_attendance_form'),
    path('manager/submit-attendance/', views.submit_manager_attendance, name='submit_manager_attendance'),
    path('manager/manager-attendance-history/<str:user_id>/', views.manager_attendance_history, name='manager_attendance_history'),
    path('manager/employee-attendance-history/', views.manager_employee_attendance_history, name='manager_employee_attendance_history'),

    # Supervisor attendance
    path('supervisor/attendance/form/<str:user_id>/', views.supervisor_attendance_form, name='supervisor_attendance_form'),
    path('supervisor/submit-attendance/', views.submit_supervisor_attendance, name='submit_supervisor_attendance'),
    path('supervisor/supervisor-attendance-history/', views.supervisor_attendance_history, name='supervisor_attendance_history'),
    
    path('employee/attendance/request-reset/', views.employee_request_check_out_reset, name='employee-request-check-out-reset'),
    path('manager/attendance/request-reset/', views.manager_request_check_out_reset, name='manager-request-check-out-reset'),
    path('supervisor/attendance/request-reset/', views.supervisor_request_check_out_reset, name='supervisor-request-check-out-reset'),
    path('hr/attendance-reset/request-reset/', views.hr_attendance_request_reset, name='hr-request-check-out-reset'),
    # Manager & Employee
    path('manager/manager-reset-requests/', views.manager_reset_requests, name='manager_reset_requests'),
    path('manager/approve-and-reset-checkout-time/<request_id>/', views.approve_and_reset_checkout_time, name='approve_and_reset_checkout_time'),
    path('manager/reject-reset-request/<int:request_id>/', views.reject_reset_request, name='reject_reset_request'),

    # Admin & Manager
     # Admin & Manager
    path('admin/manager-reset-requests/', views.admin_manager_reset_requests, name='admin_manager_reset_requests'),
    path('admin/approve-and-reset-checkout-time/<int:id>/', views.admin_approve_and_reset_checkout_time, name='admin_approve_and_reset_checkout_time'),
    path('admin/reject-reset-request/<int:id>/', views.admin_reject_manager_reset_request, name='admin_reject_manager_reset_request'),

    # Admin & Employee
    path('admin/employee-reset-requests/', views.admin_employee_reset_requests, name='admin_employee_reset_requests'),
    path('admin/approve-and-reset-employee-reset-request/<int:id>/', views.admin_approve_and_reset_employee_checkout_time, name='admin_approve_and_reset_employee_checkout_time'),
    path('admin/reject-employee-reset-request/<int:id>/', views.admin_reject_employee_reset_request, name='admin_reject_employee_reset_request'),

    # Admin & Supervisor
    path('admin/supervisor-reset-requests/', views.admin_supervisor_reset_requests, name='admin_supervisor_reset_requests'),
    path('admin/approve-and-reset-supervisor-reset-request/<int:id>/', views.admin_approve_and_reset_supervisor_checkout_time, name='admin_approve_and_reset_supervisor_checkout_time'),
    path('admin/reject-supervisor-reset-request/<int:id>/', views.admin_reject_supervisor_reset_request, name='admin_reject_supervisor_reset_request'),

     # MD & Employee
    path('md/employee-reset-requests/', views.md_employee_reset_requests, name='md_employee_reset_requests'),
    path('md/approve-and-reset-employee-reset-request/<int:request_id>/', views.md_approve_and_reset_employee_checkout_time, name='md_approve_and_reset_employee_checkout_time'),
    path('md/reject-employee-reset-request/<int:request_id>/', views.md_reject_employee_reset_request, name='md_reject_employee_reset_request'),

    # MD & Manager
    path('md/manager-reset-requests/', views.md_manager_reset_requests, name='md_manager_reset_requests'),
    path('md/approve-and-reset-manager-reset-request/<int:request_id>/', views.md_approve_and_reset_manager_checkout_time, name='md_approve_and_reset_manager_checkout_time'),
    path('md/reject-manager-reset-request/<int:request_id>/', views.md_reject_manager_reset_request, name='md_reject_manager_reset_request'),

    # MD & Supervisor
    path('md/supervisor-reset-requests/', views.md_supervisor_reset_requests, name='md_supervisor_reset_requests'),
    path('md/approve-and-reset-supervisor-reset-request/<int:request_id>/', views.md_approve_and_reset_supervisor_checkout_time, name='md_approve_and_reset_supervisor_checkout_time'),
    path('md/reject-supervisor-reset-request/<int:request_id>/', views.md_reject_supervisor_reset_request, name='md_reject_supervisor_reset_request'),

    # Admin -> Employee, Manager, Supervisor history checking
    path('admin/employee-attendance-history/', views.admin_employee_attendance_history, name='admin_employee_attendance_history'),
    path('supervisor_attendance_history/<str:user_id>/', views.supervisor_attendance_history, name='supervisor_attendance_history'),
    path('admin/manager-attendance-history/', views.admin_manager_attendance_history, name='admin_manager_attendance_history'),
    path('admin_all_managers_attendance_history', views.admin_all_managers_attendance_history, name='admin_all_managers_attendance_history'),
    path('admin_all_hrs_attendance_history', views.admin_all_hrs_attendance_history, name='admin_all_hrs_attendance_history'),
    
    path('admin/supervisor-attendance-history/', views.admin_supervisor_attendance_history, name='admin_supervisor_attendance_history'),
    
    
    ###############################################################################
    path('manager-weekly-attendance-chart/<str:user_id>/', views.manager_weekly_attendance_chart, name='manager_weekly_attendance_chart'),
    path('attendance/weekly/<str:user_id>/', views.employee_weekly_attendance, name='employee_weekly_attendance_chart'),
    path('employee/weekly-chart/', views.show_employees_weekly_chart, name='employee-weekly-chart'),
      
    path('employee/monthly-attendance-chart/<str:user_id>/', views.employee_monthly_attendance_chart, name='employee-monthly-attendance-chart'),
    path('employee/yearly-attendance-chart/<str:user_id>/', views.employee_yearly_attendance_chart, name='employee-yearly-attendance-chart'),
        
        
    path('manager/monthly-attendance-chart/<str:user_id>/', views.manager_monthly_attendance_chart, name='manager-monthly-attendance-chart'),
    path('employees/monthly-attendance-chart/<str:user_id>/',views. show_employees_monthly_chart, name='employees-monthly-attendance-chart'),


    #new one
    path('api/admin-weekly-chart/', views.admin_employee_weekly_chart, name='api_weekly_chart'),
    path('api/admin-monthly-chart/', views.admin_employee_monthly_chart, name='api_monthly_chart'),  
    
    path('api/admin-manager-weekly-chart/', views.admin_manager_weekly_chart, name='admin_manager_weekly_chart'),
    path('api/admin-manager-monthly-chart/', views.admin_manager_monthly_chart, name='admin_manager_monthly_chart'),

    path('api/admin-supervisor-weekly-chart/', views.admin_supervisor_weekly_chart, name='admin_supervisor_weekly_chart'),
    path('api/admin-supervisor-monthly-chart/', views.admin_supervisor_monthly_chart, name='admin_supervisor_monthly_chart'),      
    
    
     # POST: Create a new permission hour request
    path('request-permission-hours/', views.request_permission_hours, name='request_permission_hours'),
    
    # GET: Fetch permission hour requests for the logged-in employee
    path('get-permission-hours/', views.get_permission_hours, name='get_permission_hours'),
    path('get-all-permission-hours/', views.get_all_permission_hours, name='get_all_permission_hours'),
    
    # PUT: Update an existing permission hour request by ID
    path('request-permission-hours/<int:id>/',views. update_permission_hour, name='update_permission_hour'),
    
    # DELETE: Delete a specific permission hour request by ID
    path('request-permission-hours/<int:id>/', views.delete_permission_hour, name='delete_permission_hour'),
    
    path('manage-permission-hours/',views. manage_permission_hours, name='manage_permission_hours'),
     
    path('approve-permission-hour/<int:permission_id>/', views.approve_permission_hour, name='approve_permission_hour'),
    path('permission-hour/<int:permission_id>/', views.get_permission_hour, name='get_permission_hour'),
    path('permission-hour/<int:permission_id>/update/',views. update_permission_hour, name='update_permission_hour'),
    path('permission-hour/<int:permission_id>/delete/',views. delete_permission_hour, name='delete_permission_hour'),
    
#################################################################3

    # ############################################
    #   path('api/interview-schedules/', views.interview_schedule, name='interview_schedule'),  # Get all schedules
    # path('api/interview-schedules/<int:schedule_id>/', views.interview_schedule_detail, name='interview_schedule_detail'),  # Get schedule by ID
    #  path('api/add-interview-schedule/', views.add_interview_schedule, name='add_interview_schedule'),#post
    #   path('api/interview-schedules/<int:schedule_id>/update/', views.interview_schedule_update, name='interview_schedule_update'),  # Update schedule
    # path('api/interview-schedules/<int:schedule_id>/delete/', views.interview_schedule_delete, name='interview_schedule_delete'),  # Delete schedule
    
    # ##############################################################
    # path('api/department-active-jobs/', views.department_active_jobs, name='department_active_jobs'),  # GET: List all jobs
    # path('api/department-active-jobs/<int:job_id>/', views.get_department_active_job, name='get_department_active_job'),  # GET: Get job by ID
    # path('api/department-active-jobs/add/', views.add_department_active_job, name='add_department_active_job'),  # POST: Add a new job
    # path('api/department-active-jobs/<int:job_id>/update/', views.update_department_active_job, name='update_department_active_job'),  # PUT: Update job
    # path('api/department-active-jobs/<int:job_id>/delete/', views.delete_department_active_job, name='delete_department_active_job'),  # DELETE: Delete job
    
    # path('api/admin-weekly-chart/', views.admin_employee_weekly_chart, name='api_weekly_chart'),
    # path('api/admin-monthly-chart/', views.admin_employee_monthly_chart, name='api_monthly_chart'),  
    
    # path('api/admin-manager-weekly-chart/', views.admin_manager_weekly_chart, name='admin_manager_weekly_chart'),
    # path('api/admin-manager-monthly-chart/', views.admin_manager_monthly_chart, name='admin_manager_monthly_chart'),  
    
    # path('api/admin-supervisor-weekly-chart/', views.admin_supervisor_weekly_chart, name='admin_supervisor_weekly_chart'),
    # path('api/admin-supervisor-monthly-chart/', views.admin_supervisor_monthly_chart, name='admin_supervisor_monthly_chart'),      
    
    # ##########################################
    # path('api/calendar/', views.calendar_view, name='calendar_view'),  # GET: List all events
    # path('api/calendar/add/', views.add_event, name='add_event'),  # POST: Add a new event
    # path('api/calendar/<int:event_id>/', views.get_event_by_id, name='get_event_by_id'),  # GET: Get event by ID
    # path('api/calendar/<int:event_id>/update/',views. update_event, name='update_event'),  # PUT: Update event by ID
    # path('api/calendar/<int:event_id>/delete/', views.delete_event, name='delete_event'),  # DELETE: Delete event by ID

    
    # path('api/offers/',views. offer_list, name='offer_list'),  # GET: List offers, POST: Create offer
    # path('api/offers/<int:id>/update/',views. update_offer_status, name='update_offer_status'),  # PUT: Update offer status
    # path('api/offers/<int:id>/',views. get_offer_by_id, name='get_offer_by_id'),  # GET: Retrieve offer by ID
    # path('api/offers/<int:id>/delete/',views. delete_offer, name='delete_offer'),  # DELETE: Delete offer


     ############################################
      path('api/interview-schedules/', views.interview_schedule, name='interview_schedule'),  # Get all schedules
    path('api/interview-schedules/<int:id>/', views.interview_schedule_detail, name='interview_schedule_detail'),  # Get schedule by ID
     path('api/add-interview-schedule/', views.add_interview_schedule, name='add_interview_schedule'),#post
      path('api/interview-schedules-update/<int:id>/', views.interview_schedule_update, name='interview_schedule_update'),  # Update schedule
    path('api/interview-schedules-delete/<int:id>/', views.interview_schedule_delete, name='interview_schedule_delete'),  # Delete schedule
    # path("select-interviewer/", views.select_interviewer, name="select_interviewer"),
    ##############################################################
    path('api/department-active-jobs/', views.department_active_jobs, name='department_active_jobs'),  # GET: List all jobs
    path('api/department-active-jobs/<int:job_id>/', views.get_department_active_job, name='get_department_active_job'),  # GET: Get job by ID
    path('api/department-active-jobs/add/', views.add_department_active_job, name='add_department_active_job'),  # POST: Add a new job
    path('api/department-active-jobs-update/<int:job_id>/', views.update_department_active_job, name='update_department_active_job'),  # PUT: Update job
    path('api/department-active-jobs-delete/<int:job_id>/', views.delete_department_active_job, name='delete_department_active_job'),  # DELETE: Delete job
    

    ##########################################
    path('api/calendar/', views.calendar_view, name='calendar_view'),  # GET: List all events
    path('api/calendar/add/', views.add_event, name='add_event'),  # POST: Add a new event
    path('api/calendar/<int:id>/', views.get_event_by_id, name='get_event_by_id'),  # GET: Get event by ID
    path('api/calendar-update/<int:id>/',views. update_event, name='update_event'),  # PUT: Update event by ID
    path('api/calendar-delete/<int:id>/', views.delete_event, name='delete_event'),  # DELETE: Delete event by ID

############################################################
    path('api/feedback/', views.feedback_list, name='feedback_list'), 
    path('api/feedback/<int:feedback_id>/', views.get_feedback, name='get_feedback'),
    path('api/feedback/add/', views.add_feedback, name='add_feedback'),
    path('api/feedback/<int:feedback_id>/update/', views.update_feedback, name='update_feedback'),
    path('api/feedback/<int:feedback_id>/delete/', views.delete_feedback, name='delete_feedback'),
    
  ################################################
  
    path('api/offers/',views. offer_list, name='offer_list'),  # GET: List offers, POST: Create offer
    path('api/offers/<int:id>/update/',views. update_offer_status, name='update_offer_status'),  # PUT: Update offer status
    path('api/offers/<int:id>/',views. get_offer_by_id, name='get_offer_by_id'),  # GET: Retrieve offer by ID
    path('api/offers/<int:id>/delete/',views. delete_offer, name='delete_offer'),  # DELETE: Delete offer

    path('api/shift-attendance/', views.ShiftAttendanceListCreateAPIView.as_view(), name='shift-attendance-list-create'),
    path('api/shift-attendance/<int:pk>/', views.ShiftAttendanceDetailAPIView.as_view(), name='shift-attendance-detail'),

    path('api/onboarding-dashboard/', views.OnboardingDashboard.as_view(), name='onboarding-dashboard'), 
    path('api/onboarding-task/<int:pk>/', views.OnboardingTaskDetailAPIView.as_view(), name='onboarding-task-detail'),


    path('api/shift-time/add/', views.add_shift_time, name='add_shift'),  # POST: Add a new event
    path('api/shift-time-update/<int:id>/', views.update_shift_time, name='update_shift'),  # GET: Get event by ID
    path('api/shift-time-delete/<int:id>/',views. delete_shift_time, name='delete_shift'),  # PUT: Update event by ID
    path('api/get-shift-time/', views.overall_shift_time, name='get_shift'),

    path('supervisor/attendance/weekly/<str:user_id>/', views.supervisor_weekly_attendance, name='supervisor_weekly_attendance_chart'),
    path('supervisor/monthly-attendance-chart/<str:user_id>/', views.supervisor_monthly_attendance_chart, name='supervisor-monthly-attendance-chart'),

     ######################################### HR urls ########################
    path('api/admin-hr-weekly-chart/', views.admin_hr_weekly_chart, name='admin_hr_weekly_chart'),
    path('api/admin-hr-monthly-chart/', views.admin_hr_monthly_chart, name='admin_hr_monthly_chart'),  
    path('admin/hr-attendance-history/', views.admin_hr_attendance_history, name='admin_hr_attendance_history'),
    path('admin/hr-reset-requests/', views.admin_hr_reset_requests, name='admin_hr_reset_requests'),
    path('admin/hr-approve-and-reset-checkout-time/<int:id>/', views.admin_hr_approve_and_reset_checkout_time, name='admin_hr_approve_and_reset_checkout_time'),
    path('admin/hr-reject-reset-request/<int:id>/', views.admin_hr_reject_manager_reset_request, name='admin_hr_reject_reset_request'),
    
    path('hr/attendance/form/<str:user_id>/', views.hr_attendance_form, name='hr_attendance_form'),
    path('hr/submit-attendance/', views.submit_hr_attendance, name='submit_hr_attendance'),
    path('hr/manager-attendance-history/<str:user_id>/', views.hr_attendance_history, name='hr_attendance_history'),
    path('hr-weekly-attendance-chart/<str:user_id>/', views.hr_weekly_attendance_chart, name='hr_weekly_attendance_chart'),
    path('hr_request_check_out_reset/<str:user_id>/', views.hr_request_check_out_reset, name='hr_request_check_out_reset'),
    path('hr/monthly-attendance-chart/<str:user_id>/', views.hr_monthly_attendance_chart, name='hr-monthly-attendance-chart'),

     ######################################### AR urls ########################
    path('api/admin-ar-weekly-chart/', views.admin_ar_weekly_chart, name='admin_ar_weekly_chart'),
    path('api/admin-ar-monthly-chart/', views.admin_ar_monthly_chart, name='admin_ar_monthly_chart'),  
    path('admin/ar-attendance-history/', views.admin_ar_attendance_history, name='admin_ar_attendance_history'),
    path('admin/ar-reset-requests/', views.admin_ar_reset_requests, name='admin_ar_reset_requests'),
    path('admin/ar-approve-and-reset-checkout-time/<int:id>/', views.admin_ar_approve_and_reset_checkout_time, name='admin_ar_approve_and_reset_checkout_time'),
    path('admin/ar-reject-reset-request/<int:id>/', views.admin_ar_reject_manager_reset_request, name='admin_ar_reject_reset_request'),
    
    path('ar/attendance/form/<str:user_id>/', views.ar_attendance_form, name='ar_attendance_form'),
    path('ar/submit-attendance/', views.submit_ar_attendance, name='submit_ar_attendance'),
    path('ar/manager-attendance-history/<str:user_id>/', views.ar_attendance_history, name='ar_attendance_history'),
    path('ar-weekly-attendance-chart/<str:user_id>/', views.ar_weekly_attendance_chart, name='ar_weekly_attendance_chart'),
    path('ar_request_check_out_reset/<str:user_id>/', views.ar_request_check_out_reset, name='ar_request_check_out_reset'),
    path('ar/monthly-attendance-chart/<str:user_id>/', views.ar_monthly_attendance_chart, name='ar-monthly-attendance-chart'),
     path('ar/attendance-reset/request-reset/', views.ar_attendance_request_reset, name='ar-request-check-out-reset'),

    #admin chart
    path('api/checked-in-users/', views.get_checked_in_users, name='checked-in-users'),

    path('admin/overall-manager-daily-chart/', views.admin_overall_manager_daily_chart, name='admin_overall_manager_daily_chart'),
    path('admin/overall-supervisor-daily-chart/', views.admin_overall_supervisor_daily_chart, name='admin_overall_supervisor_daily_chart'),
    path('admin/overall-hr-daily-chart/', views.admin_overall_hr_daily_chart, name='admin_overall_hr_daily_chart'),
    path('admin/overall-employee-daily-chart/', views.admin_overall_employee_daily_chart, name='admin_overall_employee_daily_chart'),
    
    path('check_in_with_auto_leave/', views.check_in_with_auto_leave, name='check_in_with_auto_leave'),
    path('check_in_manager_with_auto_leave/', views.check_in_manager_with_auto_leave, name='check_in_manager_with_auto_leave'),
    path('check_in_hr_with_auto_leave/', views.check_in_hr_with_auto_leave, name='check_in_hr_with_auto_leave'),
    path('check_in_employee_with_auto_leave/', views.check_in_employee_with_auto_leave, name='check_in_employee_with_auto_leave'),
     
    ######################## New User urls After the  change flow ###########################################
    
    path('user/all-user-attendance-history/', views.all_user_attendance_history, name='all_user_attendance_history'),
    path('admin/user-reset-requests/', views.admin_user_reset_requests, name='admin_user_reset_requests'),
    path('admin/approve-and-reset-user-reset-request/<int:id>/', views.admin_approve_and_reset_user_reset_request,  name='admin_approve_and_reset_user_checkout_time'),
    path('admin/reject-user-reset-request/<int:id>/', views.admin_reject_user_reset_request, name='admin_reject_user_reset_request'),
    path('user/submit-user-attendance/', views.submit_user_attendance, name='submit_user_attendance'),
    path('user/user-attendance-form/<str:user_id>/', views.user_attendance_form, name='user-attendance-form'),
    path('user/user-employee-attendance-history/<str:user_id>/', views.user_employee_attendance_history, name='user_employee_attendance_history'),
    
    path("monthly-summary/", views.all_user_monthly_summary, name="all_user_monthly_summary"),
    path("department-summary/", views.all_user_department_summary, name="all_user_department_summary"),
    # path('user/user-weekly-attendance/<str:user_id>/', views.user_weekly_attendance_chart, name='user_weekly_attendance_chart'),
   path("overtime-summary/", views.overtime_summary, name="overtime_summary"),
    path("department-overtime-summary/", views.department_overtime_summary, name="department_overtime_summary"),

]
