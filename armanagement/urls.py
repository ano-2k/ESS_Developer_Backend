from django.urls import path
from . import views

urlpatterns = [
    # Client & Employee Summary APIs
    path('client-summary/<int:client_id>/', views.client_summary, name='client-summary'),
    path('employee-summary/<int:employee_id>/', views.employee_summary, name='employee-summary'),

    # Reminder and Target APIs
    path('send-reminder/', views.send_reminder, name='send-reminder'),
    path('set-client-target/', views.set_client_target, name='set-client-target'),
    path('set-employee-target/', views.set_employee_target, name='set-employee-target'),
    path('total-employees-summary/', views.total_employees_summary, name='total-employees-summary'),
    path('total-clients-summary/', views.total_clients_summary, name='total-clients-summary'),

    #new ADDED
    path('targets/', views.get_all_targets, name='get_all_targets'),
    path('targets/create/', views.create_target, name='create_target'),
    path('targets/<int:pk>/', views.get_target_by_id, name='get_target_by_id'),
    path('targets/<int:pk>/update/', views.update_target, name='update_target'),
    path('targets/<int:pk>/delete/', views.delete_target, name='delete_target'),
    
    # NEWLY ADDED ON JUNE 09
    path('client-targets/<str:employee_id>', views.get_client_targets, name='get_client_targets'),
    path('client-targets/create/', views.create_client_target, name='create_client_target'),

]