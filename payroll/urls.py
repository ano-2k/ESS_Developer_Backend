from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Endpoint for employee payroll processing
    path('process-payroll/', views.process_payroll, name='process_payroll'),
    
    # Endpoint for manager payroll processing
    path('manager-process-payroll/', views.manager_process_payroll, name='manager_process_payroll'),
    
    # Endpoint for payroll history
    path('payroll-history/', views.payroll_history, name='payroll_history'),
     # Manager Payroll
    path('manager-payroll-history/', views.manager_payroll_history, name='manager_payroll_history'),
    path('manager/payroll-notification/', views.manager_payroll_notification, name='manager_payroll_notification'),
    path('get-supervisor-salary/<int:id>/', views.supervisor_salary_history_by_id, name='supervisor_salary_history_by_id'),
    path('get-manager-salary/<int:id>/', views.manager_salary_history_by_id, name='manager_salary_history_by_id'),
    path('get-employee-salary/<int:id>/', views.employee_salary_history_by_id, name='employee_salary_history_by_id'),
     path('get-hr-salary/<int:id>/', views.hr_salary_history_by_id, name='hr_salary_history_by_id'),
    # Payroll Notifications
    path('payroll-notification/', views.payroll_notification, name='payroll_notification'),

    # Supervisor Payroll
    path('supervisor/process-payroll/', views.supervisor_process_payroll, name='supervisor_process_payroll'),
    
    # Bonus Management
    path('bonus/create/', views.create_bonus, name='create_bonus'),
    path('bonus/history/', views.bonus_history, name='bonus_history'),
    
    # Salary Management
    path('salary/create/', views.create_salary, name='create_salary'),
    path('salary/history/', views.salary_history, name='salary_history'),
    path('salary/history/<str:user_id>/', views.salary_history_by_id, name='salary-history'),
    
     path('supervisor-salary/create/', views.create_supervisor_salary, name='create_supervisor_salary'),
    path('supervisor-salary/history/', views.supervisor_salary_history, name='supervisor_salary_history'),
   
     path('update-supervisor-salary/<int:id>/', views.update_supervisor_salary, name='update-supervisor-salary'),
    
    # Delete a specific salary record by ID
    path('delete-supervisor-salary/<int:id>/', views.delete_supervisor_salary, name='delete-supervisor-salary'),
    # Update a specific salary record by ID
    path('update-salary/<int:id>/', views.update_salary, name='update-salary'),
    
    # Delete a specific salary record by ID
    path('delete-salary/<int:id>/', views.delete_salary, name='delete-salary'),
    
     # Manager Salary Management
    path('salary/manager-create/', views.create_manager_salary, name='create_manager_salary'),
    path('manager-salary/history/', views.manager_salary_history, name='salary_history'),
    # Update a specific salary record by ID
    path('update-manager-salary/<int:id>/', views.update_manager_salary, name='update-manager_salary'),
    
    # Delete a specific salary record by ID
    path('delete-manager-salary/<int:id>/', views.delete_manager_salary, name='delete_manager_salary'),
    path('supervisor-payroll-history/', views.supervisor_payroll_history, name='supervisor_payroll_history'),
    # Payslip PDF Download
    path('download-pdf/<str:pdf_path>/', views.download_pdf, name='download_pdf'),
    path('media/payslips/<str:pdf_path>/', views.serve_payslip, name='serve_payslip'),
    #path('salary/history/<str:user_id>/', views.salary_history_by_id, name='salary_history_by_id'),
    path('bonus/history/<str:user_id>/', views.bonus_history_by_id, name='bonus_history_by_id'),
    
    ##################### HR PAYROLL URLS ###################
    path('salary/hr-create/', views.create_hr_salary, name='create_hr_salary'),
    path('hr-salary/history/', views.hr_salary_history, name='hr_salary_history'),
    # Update a specific salary record by ID
    path('update-hr-salary/<int:id>/', views.update_hr_salary, name='update-hr_salary'),
    
    # Delete a specific salary record by ID
    path('delete-hr-salary/<int:id>/', views.delete_hr_salary, name='delete_hr_salary'),
    
    path('hr-process-payroll/', views.hr_process_payroll, name='hr_process_payroll'),
    
    # Endpoint for payroll history
    path('hr_payroll-history/', views.hr_payroll_history, name='hr_payroll_history'),
    path('hr_payroll_notification/', views.hr_payroll_notification, name='hr_payroll_notification'),
    
    ##################### AR PAYROLL URLS ###################
    path('salary/ar-create/', views.create_ar_salary, name='create_ar_salary'),
    path('ar-salary/history/', views.ar_salary_history, name='ar_salary_history'),
    # Update a specific salary record by ID
    path('update-ar-salary/<int:id>/', views.update_ar_salary, name='update-ar_salary'),
    
    # Delete a specific salary record by ID
    path('delete-ar-salary/<int:id>/', views.delete_ar_salary, name='delete_ar_salary'),
    
    path('ar-process-payroll/', views.ar_process_payroll, name='ar_process_payroll'),
    
    # Endpoint for payroll history
    path('ar_payroll-history/', views.ar_payroll_history, name='ar_payroll_history'),
    path('ar_payroll_notification/', views.ar_payroll_notification, name='ar_payroll_notification'),
    path('get-ar-salary/<int:id>/', views.ar_salary_history_by_id, name='ar_salary_history_by_id'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


