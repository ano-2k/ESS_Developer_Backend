from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
# Import the views from the same directory

urlpatterns = [
    path('api/apply-leave/', views.apply_leave, name='apply_leave'),
    path('api/hr_apply-leave/', views.hr_apply_leave, name='hr_apply_leave'),
    path('leave-history/', views.leave_history, name='leave_history'),
    path('employee-leave-status/', views.employee_leave_status, name='employee_leave_status'),
    path('delete_employee_leave/<int:id>/', views.delete_employee_leave, name='delete_employee_leave'),
     path('delete_supervisor_leave/<int:id>/', views.delete_supervisor_leave, name='delete_supervisor_leave'),
     path('delete_manager_leave/<int:id>/', views.delete_manager_leave, name='delete_manager_leave'),
    path('employee-leave-calendar/', views.employee_leave_calendar, name='employee_leave_calendar'),
    path('manager-apply-leave/', views.manager_apply_leave, name='manager_apply_leave'),
    path('manager-leave-history/', views.manager_leave_history, name='manager_leave_history'),
    path('manager-leave-calendar/', views.manager_leave_calendar_view, name='manager_leave_calendar'),
     path('manager-leave-status/', views.manager_leave_status, name='manager_leave_status'),
    # Leave policies endpoints
     # Leave policies endpoints
    path('leave-policies/', views.leave_policies, name='leave_policies'),
    path('leave-balance/update/<str:user>/', views.update_leave_balance, name='update_leave_balance'),

    path('supervisor-leave-policies/', views.supervisor_leave_policies, name='leave_policies'),
    path('supervisor-leave-balance/update/<str:user>/', views.update_supervisor_leave_balance, name='update_leave_balance'),
    # Manager leave policies endpoints
    path('manager-leave-policies/', views.manager_leave_policies, name='manager_leave_policies'),
    path('manager-leave-balance/update/<str:user>/', views.update_manager_leave_balance, name='update_manager_leave_balance'),

    # Notification endpoints
    path('notification/cancel/<int:notification_id>/', views.cancel_notification, name='cancel_notification'),
    path('admin-notification/cancel/<int:notification_id>/', views.admin_cancel_notification, name='admin_cancel_notification'),
    path('manager-notification/cancel/<int:notification_id>/', views.manager_cancel_notification, name='manager_cancel_notification'),
    path('supervisor-apply-leave/', views.supervisor_apply_leave, name='supervisor_apply_leave'),
    path('leave-history/', views.supervisor_leave_history, name='supervisor_leave_history'),
    path('leave-calendar/', views.supervisor_leave_calendar_view, name='supervisor_leave_calendar_view'),
     path('supervisor-leave-status/', views.supervisor_leave_status, name='supervisor_leave_status'),
   
    path('cancel-supervisor-notification/<int:notification_id>/', views.supervisor_cancel_notification, name='supervisor_cancel_notification'),

    #api 
    path('leave-history-id/<str:id>/', views.leave_history_by_id, name='leave_history_by_id'),
    path('leave-history-list/', views.leave_history_list, name='leave_history_list'),
    path('leave-status/<str:id>/',views. employee_leave_status, name='employee_leave_status'),
    path('leave-calendar/<str:id>/',views. employee_leave_calendar_view_by_id, name='employee_leave_calendar_view_by_id'),
    path('manager-leave-history-id/<str:id>/',views.manager_leave_history_by_id, name='manager_leave_history_by_id'),
    path('manager-leave-history-list/', views.manager_leave_history_list, name='manager_leave_history_list'),
    path('manager-leave-calendar-id/<str:id>/', views.manager_leave_calendar_view_by_id, name='manager_leave_calendar_view_by_id'),
    path('manager-leave-calendar-list/', views.manager_leave_calendar_view_list, name='manager_leave_calendar_view_list'),
    path('manager-leave-status-id/<str:id>/', views.manager_leave_status_by_id, name='manager_leave_status_by_id'),
    path('leave-policies-id/<str:id>/', views.leave_policies_by_id, name='leave_policies_by_id'),
    # path('leave-policies-list/', views.leave_policies_list, name='leave_policies_list'),
    
     path('hr-leave-history-id/<str:id>/', views.hr_leave_history_by_id, name='hr_leave_history_by_id'),
    # path('manager-leave-policies-id/<str:id>/', views.manager_leave_policies_by_id, name='manager_leave_policies_by_id'),
    path('supervisor-leave-history-id/<str:id>/', views.supervisor_leave_history_by_id, name='supervisor_leave_history_by_id'),
    path('supervisor-leave-history-list/', views.supervisor_leave_history_by_list, name='supervisor_leave_history_by_list'),
    path('supervisor-leave-calendar-id/<str:id>/', views.supervisor_leave_calendar_view_by_id, name='supervisor_leave_calendar_view_by_id'),
    path('supervisor-leave-calendar-list/', views.supervisor_leave_calendar_view_by_list, name='supervisor_leave_calendar_view_by_list'),

    # path('supervisor-leave-policies-id/<str:id>/', views.supervisor_leave_policies_by_id, name='supervisor_leave_policies_by_id'),
    # path('supervisor-leave-policies-list/', views.supervisor_leave_policies_by_list, name='supervisor_leave_policies_by_list'),
    
    ##################### hr leave urls
    path('hr-leave-status/', views.hr_leave_status, name='hr_leave_status'),
    path('hr-leave-policies/', views.hr_leave_policies, name='hr_leave_policies'),
    path('update-hr-leave-balance/<str:user>/', views.update_hr_leave_balance, name='update_hr_leave_balance'),
    path('cancel-hr-notification/<int:id>/', views.hr_cancel_notification, name='hr_cancel_notification'),
    path('delete_hr_leave/<int:id>/', views.delete_hr_leave, name='delete_hr_leave'),
    path('hr-apply-leave/', views.hr_apply_leave, name='hr_apply_leave'),
    path('hr-leave-history/', views.hr_leave_history, name='hr_leave_history'),

    path('edit_manager_leave_balance/<int:id>/', views.edit_manager_leave_balance, name='edit_manager_leave_balance'),
    path('delete_manager_leave_balance/<int:id>/', views.delete_manager_leave_balance, name='delete_manager_leave_balance'),
    
    path('edit_employee_leave_balance/<int:id>/', views.edit_employee_leave_balance, name='edit_employee_leave_balance'),
    path('delete_employee_leave_balance/<int:id>/', views.delete_employee_leave_balance, name='delete_employee_leave_balance'),
     
    path('edit_supervisor_leave_balance/<int:id>/', views.edit_supervisor_leave_balance, name='edit_supervisor_leave_balance'),
    path('delete_supervisor_leave_balance/<int:id>/', views.delete_supervisor_leave_balance, name='delete_supervisor_leave_balance'),
     
    path('edit_hr_leave_balance/<int:id>/', views.edit_hr_leave_balance, name='edit_hr_leave_balance'),
    path('delete_hr_leave_balance/<int:id>/', views.delete_hr_leave_balance, name='delete_hr_leave_balance'),

    ##################### hr leave urls
    path('ar-leave-status/', views.ar_leave_status, name='ar_leave_status'),
    path('ar-leave-policies/', views.ar_leave_policies, name='ar_leave_policies'),
    path('update-ar-leave-balance/<str:user>/', views.update_ar_leave_balance, name='update_ar_leave_balance'),
    path('cancel-ar-notification/<int:id>/', views.ar_cancel_notification, name='ar_cancel_notification'),
    path('delete_ar_leave/<int:id>/', views.delete_ar_leave, name='delete_ar_leave'),
    path('ar-apply-leave/', views.ar_apply_leave, name='ar_apply_leave'),
    path('ar-leave-history/', views.ar_leave_history, name='ar_leave_history'),
    path('edit_ar_leave_balance/<int:id>/', views.edit_ar_leave_balance, name='edit_ar_leave_balance'),
    path('delete_ar_leave_balance/<int:id>/', views.delete_ar_leave_balance, name='delete_ar_leave_balance'),
    path('ar-leave-history-id/<str:id>/', views.ar_leave_history_by_id, name='ar_leave_history_by_id'),
    path('submit-late-login-reason/', views.submit_late_login_reason, name='submit-late-login-reason'),
    path('supervisor-leave-history-id/<str:supervisor_id>/', views.supervisor_leave_history, name='supervisor-leave-history'),
    path('admin_supervisor_late_login_reasons/', views.admin_supervisor_late_login_reasons, name='admin-supervisor-late-login-reasons'),
    path('approve_late_login_reason/<int:reason_id>/', views.approve_late_login_reason, name='approve-late-login-reason'),
    path('reject_late_login_reason/<int:reason_id>/', views.reject_late_login_reason,name='reject-late-login-reason'),
    path('edit_supervisor_leave_request/<int:leave_id>/', views.edit_supervisor_leave_request, name='edit_supervisor_leave_request'),
    
    path('submit_hr_late_login_reason/', views.submit_hr_late_login_reason, name='submit_hr_late_login_reason'),
    path('hr-leave-history-id/<str:supervisor_id>/', views.hr_leave_history, name='hr-leave-history'),
    path('admin_hr_late_login_reasons/', views.admin_hr_late_login_reasons, name='admin_hr_late_login_reasons'),
    path('approve_hr_late_login_reason/<int:reason_id>/', views.approve_hr_late_login_reason, name='approve_hr_late_login_reason'),
    path('reject_hr_late_login_reason/<int:reason_id>/', views.reject_hr_late_login_reason,name='reject_hr_late_login_reason'),
    path('edit_hr_leave_request/<int:leave_id>/', views.edit_hr_leave_request, name='edit_hr_leave_request'),

    path('submit_manager_late_login_reason/', views.submit_manager_late_login_reason, name='submit_manager_late_login_reason'),
    path('admin_manager_late_login_reasons/', views.admin_manager_late_login_reasons, name='admin_manager_late_login_reasons'),
    path('approve_manager_late_login_reason/<int:reason_id>/', views.approve_manager_late_login_reason, name='approve_manager_late_login_reason'),
    path('reject_manager_late_login_reason/<int:reason_id>/', views.reject_manager_late_login_reason,name='reject_manager_late_login_reason'),
    path('edit_manager_leave_request/<int:leave_id>/', views.edit_manager_leave_request, name='edit_manager_leave_request'),

    path('submit_employee_late_login_reason/', views.submit_employee_late_login_reason, name='submit-employee-late-login-reason'),
    path('admin_employee_late_login_reasons/', views.admin_employee_late_login_reasons, name='admin-employee-late-login-reasons'),
    path('approve_employee_late_login_reason/<int:reason_id>/', views.approve_employee_late_login_reason, name='approve-employee-late-login-reason'),
    path('reject_employee_late_login_reason/<int:reason_id>/', views.reject_employee_late_login_reason, name='reject-employee-late-login-reason'),
    path('edit_employee_leave_request/<int:leave_id>/', views.edit_employee_leave_request, name='edit_employee_leave_request'),
    
    
    ###################### New Setup ##################################
    
    path('user/user-leave-policies/', views.user_leave_policies, name='user_leave_policies'),
    path('user/update-leave-balance/<str:username>/', views.update_user_leave_balance, name='update_user_leave_balance'),
    path('user/edit_user_leave_balance/<int:id>/', views.edit_user_leave_balance, name='edit_user_leave_balance'),
    path('user/delete_user_leave_balance/<int:id>/', views.delete_user_leave_balance, name='delete_user_leave_balance'),
    path('submit_user_late_login_reason/', views.submit_user_late_login_reason, name='submit-user-late-login-reason'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
