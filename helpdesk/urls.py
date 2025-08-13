from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs (unchanged)
    path('api/tickets/admin/', views.create_administrative_ticket, name='admin-ticket-create'),
    path('api/tickets/hr/', views.create_hr_ticket, name='hr-ticket-create'),
    path('api/tickets/supervisor/', views.create_supervisor_ticket, name='supervisor-ticket-create'),
    path('api/tickets/system/', views.create_system_ticket, name='system-ticket-create'),
    path('api/tickets/other/', views.create_other_ticket, name='other-ticket-create'),
    path('api/tickets/manager/', views.create_manager_ticket, name='manager-ticket-create'),
    path('api/tickets/list/<str:manager_id>/', views.ticket_list, name='ticket_list'),
    
    # New URLs for helpdesk-specific endpoints
    path('api/helpdesk/admin_list/', views.helpdesk_admin_list, name='helpdesk_admin_list'),
    path('api/helpdesk/hr_list/', views.helpdesk_hr_list, name='helpdesk_hr_list'),
    path('api/helpdesk/supervisor_list/', views.helpdesk_supervisor_list, name='helpdesk_supervisor_list'),
    
    
    path('api/tickets/<str:ticket_id>/reply/', views.ticket_reply, name='ticket-reply'),
    path('api/tickets/<str:ticket_id>/', views.ticket_update, name='ticket-update'),
    
    
    path('api/admin/tickets/<str:user_id>/', views.get_assigned_tickets, name='admin-tickets-assigned'),
    path('api/hr/tickets/<str:hr_id>/', views.get_assigned_hr_tickets, name='hr-tickets-assigned'),
    path('api/supervisor/tickets/<str:supervisor_id>/', views.get_assigned_supervisor_tickets, name='supervisor-tickets-assigned'),
    path('api/manager/tickets/<str:manager_id>/', views.get_assigned_manager_tickets, name='manager-tickets-assigned'),
    path('api/employee/tickets/<str:employee_id>/', views.get_assigned_employee_tickets, name='employee-tickets-assigned'),
    
    
    #----------------------------------------------------------------------------------------------------------------------------------
    
    path('api/tickets/supervisor_list/<str:supervisor_id>/', views.supervisor_ticket_list, name='supervisor_ticket_list'),
    path('api/tickets/hr_list/<str:hr_id>/', views.hr_ticket_list, name='hr_ticket_list'),
    
    #------------------------------------------------------------------------------------------------------------------------------------
    
    path('api/helpdesk/manager_list/', views.helpdesk_manager_list, name='helpdesk_manager_list'),
    path('api/tickets/employee_list/<str:employee_id>/', views.employee_ticket_list, name='employee_ticket_list'),
   
]