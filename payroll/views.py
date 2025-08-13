from datetime import datetime
from email.message import EmailMessage
import os
# from tkinter.tix import Meter
from django.conf import settings
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import urllib.parse

from attendance.models import Attendance
from authentication.models import Ar, Employee, Hr, Manager
from ess.settings import DEFAULT_FROM_EMAIL
from .models import ArPayrollManagement, ArPayrollNotification, ArSalary, HrPayrollManagement, HrPayrollNotification, HrSalary, ManagerPayrollManagement, ManagerSalary, PayrollManagement, SupervisorPayrollManagement,PayrollNotification, ManagerPayrollNotification, SupervisorPayrollNotification, SupervisorSalary
 # Assuming these helper functions exist
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def calculate_net_salary(per_day_rate, total_days):
    return float(per_day_rate) * float(total_days)


def manager_calculate_net_salary(per_day_rate, total_days):
    return (float(per_day_rate) * float(total_days))

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_payslip_pdf(payroll):
    # Save the PDF file in the media directory under 'payslips/'
    file_path = os.path.join(settings.MEDIA_ROOT, 'payslips', f'{payroll.user_id}_{payroll.month.strftime("%Y_%m")}.pdf')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create the directory if it doesn't exist

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Add content to the PDF
    c.drawString(100, height - 100, f'Payslip for {payroll.user} - {payroll.month.strftime("%B %Y")}')
    c.drawString(100, height - 120, f'User ID: {payroll.user_id}')
    c.drawString(100, height - 140, f'Base Salary: {payroll.base_salary}')
    c.drawString(100, height - 160, f'Total Working Hours: {payroll.total_working_hours}')
    c.drawString(100, height - 180, f'Total Overtime Hours: {payroll.overtime_hours}')
    c.drawString(100, height - 200, f'Net Salary: {payroll.net_salary}')
    c.drawString(100, height - 220, 'Thank you for your hard work!')
    c.drawString(100, height - 280, 'Best regards')
    c.drawString(100, height - 300, 'Your Company')

    c.save()
    return file_path


def serve_payslip(request, pdf_path):
    file_path = os.path.join('media', 'payslips', pdf_path)

    # Check if file exists
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{pdf_path}"'  # "inline" allows opening in the browser
        return response
    else:
        return HttpResponseNotFound("File not found")

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# def manager_create_payslip_pdf(payroll):
#     # Save the PDF file in the media directory under 'payslips/'
#     file_path = os.path.join(settings.MEDIA_ROOT, 'payslips', f'{payroll.user_id}_{payroll.month.strftime("%Y_%m")}.pdf')
#     os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create the directory if it doesn't exist

#     c = canvas.Canvas(file_path, pagesize=letter)
#     width, height = letter

#     # Add content to the PDF
#     c.drawString(100, height - 100, f'Payslip for {payroll.user} - {payroll.month.strftime("%B %Y")}')
#     c.drawString(100, height - 120, f'User ID: {payroll.user_id}')
#     c.drawString(100, height - 140, f'Base Salary: {payroll.base_salary}')
#     c.drawString(100, height - 160, f'Total Working Hours: {payroll.total_working_hours}')
#     c.drawString(100, height - 180, f'Total Overtime Hours: {payroll.overtime_hours}')
#     c.drawString(100, height - 200, f'Net Salary: {payroll.net_salary}')
#     c.drawString(100, height - 220, 'Thank you for your hard work!')
#     c.drawString(100, height - 280, 'Best regards')
#     c.drawString(100, height - 300, 'Your Company')

#     c.save()
#     return file_path


# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os
from django.conf import settings

def manager_create_payslip_pdf(payroll):
    # Save the PDF file in the media directory under 'payslips/'
    file_path = os.path.join(settings.MEDIA_ROOT, 'payslips', f'{payroll.user_id}_{payroll.month.strftime("%Y_%m")}.pdf')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Create the directory if it doesn't exist

    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Header: User Details
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 60, f'Payslip for {payroll.user} - {payroll.month.strftime("%B %Y")}')
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 80, f'User ID: {payroll.user_id}')
    c.drawString(100, height - 100, f'Base Salary: ${payroll.base_salary:,.2f}')
    c.drawString(100, height - 120, f'Total Working Hours: {payroll.total_working_hours}')
    c.drawString(100, height - 140, f'Total Overtime Hours: {payroll.overtime_hours}')

    # Table: Payroll Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, height - 180, "Description")
    c.drawString(300, height - 180, "Amount")
    
    # Drawing a line under the table header
    c.line(90, height - 185, width - 90, height - 185)
    
    # Table Data
    y_position = height - 200
    payroll_items = [
        ("Base Salary", payroll.base_salary),
        ("Overtime Pay", payroll.overtime_pay),
        # ("Deductions", payroll.deductions),
        ("Net Salary", payroll.net_salary)
    ]
    
    for item in payroll_items:
        c.setFont("Helvetica", 12)
        c.drawString(100, y_position, item[0])  # Description
        c.drawString(300, y_position, f"${item[1]:,.2f}")  # Amount
        y_position -= 20
    
    # Drawing a line at the end of the table
    c.line(90, y_position + 10, width - 90, y_position + 10)

    # Footer: Thank You and Company Information
    c.setFont("Helvetica", 10)
    c.drawString(100, y_position - 40, "Thank you for your hard work!")
    c.drawString(100, y_position - 60, "Best regards,")
    c.drawString(100, y_position - 80, "Your Company")

    c.save()
    return file_path

# Helper functions
def calculate_net_salary(per_day_rate, total_days):
    return float(per_day_rate) * float(total_days)

# def manager_calculate_net_salary(per_day_rate, total_days):
#     return float(per_day_rate) * float(total_days)
@api_view(['GET'])
def supervisor_payroll_history(request):
    """
    Fetch payroll history with optional filters.
    """
    user_filter = request.query_params.get('user')
    month_filter = request.query_params.get('month')

    payrolls = SupervisorPayrollManagement.objects.all()
    if user_filter:
        payrolls = payrolls.filter(user=user_filter)
    if month_filter:
        payrolls = payrolls.filter(
            month__year=month_filter[:4],
            month__month=month_filter[5:7]
        )

    data = [
        {
            "id": payroll.id,
            "user": payroll.user,
            "month": payroll.month.strftime("%Y-%m"),
            "net_salary": payroll.net_salary,
            "pdf_path": payroll.pdf_path,
        }
        for payroll in payrolls
    ]
    return Response(data)


@api_view(['POST'])
def process_payroll(request):
    """
    Generate payroll for employees, including salary calculations, payslip generation, and email notification.
    """
    month_str = request.data.get('month')
    employee_id = request.data.get('employee_id')

    if not month_str or not employee_id:
        return Response({'success': False, 'message': 'Employee ID and Month are required.'}, status=400)

    # Validate and parse the month
    try:
        month = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return Response({'success': False, 'message': 'Invalid month format. Use YYYY-MM.'}, status=400)

    # Fetch employee details
    try:
        employee = Employee.objects.get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return Response({'success': False, 'message': 'Employee not found.'}, status=404)

    # Fetch salary details
    salary = Salary.objects.filter(user_id=employee_id).first()
    if not salary:
        return Response(
            {'success': False, 'message': 'Salary details not found for this employee. Please add salary details.'},
            status=404
        )

    # Check if payroll already exists
    if PayrollManagement.objects.filter(user_id=employee_id, month=month).exists():
        return Response({'success': False, 'message': 'Payslip for this month already generated.'}, status=400)

    # Calculate working and overtime hours
    total_hours = Attendance.objects.filter(
        employee=employee,
        date__month=month.month,
        date__year=month.year
    ).aggregate(Sum('total_working_hours'))['total_working_hours__sum'] or 0

    overtime_hours = Attendance.objects.filter(
        employee=employee,
        date__month=month.month,
        date__year=month.year
    ).aggregate(Sum('overtime'))['overtime__sum'] or 0

    # Calculate salary components
    base_salary = float(salary.monthly_salary)
    per_day_rate = base_salary / 30  # Adjust if needed
    per_hour_rate = per_day_rate / 8  # Assuming 8 hours a workday
    total_days = total_hours / 8  # Total days worked
    net_salary = calculate_net_salary(per_day_rate, total_days)
    overtime_salary = overtime_hours * per_hour_rate

    # Create payroll entry
    payroll = PayrollManagement.objects.create(
        user=employee.username,
        user_id=employee.employee_id,
        month=month,
        email=employee.email,
        base_salary=base_salary,
        net_salary=net_salary,
        total_working_hours=total_hours,
        overtime_hours=overtime_hours,
        overtime_pay=overtime_salary,
    )

    # Generate PDF and save file path
    try:
        pdf_path = create_payslip_pdf(payroll)  # Assuming this function handles saving and returning file path
    except Exception as e:
        return Response({'success': False, 'message': f'Error generating payslip: {str(e)}'}, status=500)

    # Save PDF path to payroll record
    payroll.pdf_path = pdf_path
    payroll.save()

    # Send Email with Payslip
    subject = f'Your Payslip for {month.strftime("%B %Y")}'
    html_message = render_to_string('payroll/payslip_view.html', {'payroll': payroll})
    plain_message = strip_tags(html_message)

    try:
        # Sending the email with PDF attachment
        email = EmailMessage(
            subject, 
            plain_message, 
            'sudhakar.ibacustech@gmail.com',  # Your 'from' email
            [employee.email]  # Employee email
        )
        email.attach_file(pdf_path)  # Attach the PDF file
        email.send()
    except Exception as e:
        return Response({'success': False, 'message': f'Error sending email: {str(e)}'}, status=500)

    return Response({
        'success': True,
        'payroll_id': payroll.id,
        'pdf_path': pdf_path
    }, status=200)
    
    
@api_view(['POST'])
def manager_process_payroll(request):
    """
    Generate payroll for managers, including salary calculations, payslip generation, and email notification.
    """
    month_str = request.data.get('month')
    manager_id = request.data.get('manager_id')

    if not month_str or not manager_id:
        return Response({'success': False, 'message': 'Manager ID and Month are required.'}, status=400)

    # Validate and parse the month
    try:
        month = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return Response({'success': False, 'message': 'Invalid month format. Use YYYY-MM.'}, status=400)

    # Fetch employee details
    try:
        manager = Manager.objects.get(manager_id=manager_id)
    except Manager.DoesNotExist:
        return Response({'success': False, 'message': 'Manager not found.'}, status=404)

    # Fetch salary details
    salary = ManagerSalary.objects.filter(user_id=manager_id).first()
    if not salary:
        return Response(
            {'success': False, 'message': 'Salary details not found for this manager. Please add salary details.'},
            status=404
        )

    # Check if payroll already exists
    if ManagerPayrollManagement.objects.filter(user_id=manager_id, month=month).exists():
        return Response({'success': False, 'message': 'Payslip for this month already generated.'}, status=400)

    # Calculate working and overtime hours
    total_hours = Attendance.objects.filter(
        manager=manager,
        date__month=month.month,
        date__year=month.year
    ).aggregate(Sum('total_working_hours'))['total_working_hours__sum'] or 0

    overtime_hours = Attendance.objects.filter(
        manager=manager,
        date__month=month.month,
        date__year=month.year
    ).aggregate(Sum('overtime'))['overtime__sum'] or 0

    # Calculate salary components
    base_salary = float(salary.monthly_salary)
    per_day_rate = base_salary / 30  # Adjust if needed
    per_hour_rate = per_day_rate / 8  # Assuming 8 hours a workday
    total_days = total_hours / 8  # Total days worked
    net_salary = calculate_net_salary(per_day_rate, total_days)
    overtime_salary = overtime_hours * per_hour_rate

    # Create payroll entry
    payroll = ManagerPayrollManagement.objects.create(
        user=manager.username,
        user_id=manager.manager_id,
        month=month,
        email=manager.email,
        base_salary=base_salary,
        net_salary=net_salary,
        total_working_hours=total_hours,
        overtime_hours=overtime_hours,
        overtime_pay=overtime_salary,
    )

    # Generate PDF and save file path
    try:
        pdf_path = manager_create_payslip_pdf(payroll)  # Assuming this function handles saving and returning file path
    except Exception as e:
        return Response({'success': False, 'message': f'Error generating payslip: {str(e)}'}, status=500)

    # Save PDF path to payroll record
    payroll.pdf_path = pdf_path
    payroll.save()

    # Send Email with Payslip
    subject = f'Your Payslip for {month.strftime("%B %Y")}'
    html_message = render_to_string('payroll/payslip_view.html', {'payroll': payroll})
    plain_message = strip_tags(html_message)

    try:
        # Sending the email with PDF attachment
        email = EmailMessage(
            subject, 
            plain_message, 
            'sudhakar.ibacustech@gmail.com',  # Your 'from' email
            [manager.email]  # Employee email
        )
        email.attach_file(pdf_path)  # Attach the PDF file
        email.send()
    except Exception as e:
        return Response({'success': False, 'message': f'Error sending email: {str(e)}'}, status=500)

    return Response({
        'success': True,
        'payroll_id': payroll.id,
        'pdf_path': pdf_path
    }, status=200)
    
    
@api_view(['GET'])
def payroll_history(request):
    """
    Fetch payroll history with optional filters.
    """
    user_filter = request.query_params.get('user')
    month_filter = request.query_params.get('month')

    payrolls = PayrollManagement.objects.all()
    if user_filter:
        payrolls = payrolls.filter(user=user_filter)
    if month_filter:
        payrolls = payrolls.filter(
            month__year=month_filter[:4],
            month__month=month_filter[5:7]
        )

    data = [
        {
            "id": payroll.id,
            "user": payroll.user,
            "month": payroll.month.strftime("%Y-%m"),
            "net_salary": payroll.net_salary,
            "pdf_path": payroll.pdf_path,
        }
        for payroll in payrolls
    ]
    return Response(data)

from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponseNotFound, JsonResponse, HttpResponse
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMessage
from django.utils import timezone
from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import PayrollManagement, BonusType, Salary
from authentication.models import Employee, Supervisor
from .serializers import ArSalarySerializer, HrSalarySerializer, ManagerSalarySerializer, PayrollManagementSerializer, BonusTypeSerializer, SalarySerializer, SupervisorSalarySerializer
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Helper Functions ---



# def create_payslip_pdf(payroll):
#     file_path = f'media/{payroll.user_id}_{payroll.month.strftime("%Y_%m")}.pdf'
#     c = canvas.Canvas(file_path, pagesize=letter)
#     width, height = letter

#     c.drawString(100, height - 100, f'Payslip for {payroll.user} - {payroll.month.strftime("%B %Y")}')
#     c.drawString(100, height - 120, f'User ID: {payroll.user_id}')
#     c.drawString(100, height - 140, f'Base Salary: {payroll.base_salary}')
#     c.drawString(100, height - 160, f'Total Working Hours: {payroll.total_working_hours}')
#     c.drawString(100, height - 180, f'Total Overtime Hours: {payroll.overtime_hours}')
#     c.drawString(100, height - 200, f'Net Salary: {payroll.net_salary}')
#     c.drawString(100, height - 220, 'Thank you for your hard work!')
#     c.drawString(100, height - 280, 'Best regards,')
#     c.drawString(100, height - 300, 'Your Company')
#     c.save()
#     return file_path

# --- Manager Views ---

@api_view(['GET'])
def manager_payroll_history(request):
    """
    Fetch payroll history with optional filters.
    """
    user_filter = request.query_params.get('user')
    month_filter = request.query_params.get('month')

    payrolls = ManagerPayrollManagement.objects.all()
    if user_filter:
        payrolls = payrolls.filter(user=user_filter)
    if month_filter:
        payrolls = payrolls.filter(
            month__year=month_filter[:4],
            month__month=month_filter[5:7]
        )

    data = [
        {
            "id": payroll.id,
            "user": payroll.user,
            "month": payroll.month.strftime("%Y-%m"),
            "net_salary": payroll.net_salary,
            "pdf_path": payroll.pdf_path,
        }
        for payroll in payrolls
    ]
    return Response(data)

    
from django.http import HttpResponse, JsonResponse
from django.conf import settings
import os
from rest_framework.decorators import api_view

@api_view(['GET'])
def download_pdf(request, pdf_path):
    """
    Download the payslip PDF.
    """
    # Construct the file path where the PDF is stored
    file_path = os.path.join(settings.MEDIA_ROOT, 'payslips', pdf_path)

    try:
        # Ensure the file exists
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found'}, status=404)

        # Open the file and return it as a response
        with open(file_path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
def payroll_notification(request):
    user = request.session.get('user')
    payrolls = PayrollManagement.objects.filter(user=user)
    notifications = PayrollNotification.objects.filter(user=user).order_by('-date', '-time')

    if request.accepted_renderer.format == 'html':
        return render(request, 'payroll/payroll_notification.html', {'payrolls': payrolls, 'notifications': notifications})
    else:
        return Response({'payrolls': PayrollManagementSerializer(payrolls, many=True).data,
                         'notifications': notifications.values()})

@api_view(['GET'])
def manager_payroll_notification(request):
    user = request.session.get('user')
    notifications = ManagerPayrollNotification.objects.filter(user=user).order_by('-date', '-time')

    return Response({'notifications': notifications.values()})

# --- Supervisor Views ---


@api_view(['POST'])
def supervisor_process_payroll(request):
    """
    Generate payroll for supervisors, including salary calculations, payslip generation, and email notification.
    """
    month_str = request.data.get('month')
    supervisor_id = request.data.get('supervisor_id')

    if not month_str or not supervisor_id:
        return Response({'success': False, 'message': 'Supervisor ID and Month are required.'}, status=400)

    try:
        month = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return Response({'success': False, 'message': 'Invalid month format. Use YYYY-MM.'}, status=400)

    try:
        supervisor = Supervisor.objects.get(supervisor_id=supervisor_id)
    except Supervisor.DoesNotExist:
        return Response({'success': False, 'message': 'Supervisor not found.'}, status=404)

    salary = SupervisorSalary.objects.filter(user_id=supervisor_id).first()

    if not salary:
        return Response({'success': False, 'message': 'Salary details not found for this supervisor.'}, status=404)

        
    if SupervisorPayrollManagement.objects.filter(user_id=supervisor_id, month=month).exists():
        return Response({'success': False, 'message': 'Payslip for this month already generated.'}, status=200)

    if SupervisorSalary.objects.filter(user_id=supervisor_id, effective_date__gte=month).exists():
        return Response({'success': False, 'message': 'Salary effective date has not started yet.'}, status=200)
    
    total_hours = Attendance.objects.filter(
        supervisor=supervisor, date__month=month.month, date__year=month.year
    ).aggregate(Sum('total_working_hours'))['total_working_hours__sum'] or 0

    overtime_hours = Attendance.objects.filter(
        supervisor=supervisor, date__month=month.month, date__year=month.year
    ).aggregate(Sum('overtime'))['overtime__sum'] or 0

    base_salary = float(salary.monthly_salary)
    per_day_rate = base_salary / 30 if base_salary > 0 else 0  
    per_hour_rate = per_day_rate / 8 if per_day_rate > 0 else 0  
    total_days = total_hours / 8 if total_hours > 0 else 0  
    net_salary = total_days * per_day_rate
    overtime_salary = overtime_hours * per_hour_rate

    payroll = SupervisorPayrollManagement.objects.create(
        user=supervisor.username,
        user_id=supervisor.supervisor_id,
        month=month,
        email=supervisor.email,
        base_salary=base_salary,
        net_salary=net_salary,
        total_working_hours=total_hours,
        overtime_hours=overtime_hours,
        overtime_pay=overtime_salary,
    )

    try:
        pdf_path = create_payslip_pdf(payroll)  
    except Exception as e:
        return Response({'success': False, 'message': f'Error generating payslip: {str(e)}'}, status=500)

    payroll.pdf_path = pdf_path
    payroll.save()

    subject = f'Your Payslip for {month.strftime("%B %Y")}'
    html_message = render_to_string('payroll/payslip_view.html', {'payroll': payroll})
    plain_message = strip_tags(html_message)

    try:
        email = EmailMessage(
            subject, plain_message, DEFAULT_FROM_EMAIL, [supervisor.email]
        )
        email.attach_file(pdf_path)  
        email.send()
    except Exception as e:
        return Response({'success': False, 'message': f'Error sending email: {str(e)}'}, status=500)

    return Response({'success': True, 'payroll_id': payroll.id, 'pdf_path': pdf_path}, status=200)
# --- Bonus Management ---


@api_view(['POST'])
def create_bonus(request):
    """
    Function-based view to create a bonus record.
    """
    try:
        user_id = request.data.get('user_id')
        bonus_type = request.data.get('bonus_type')
        amount = request.data.get('amount')
        due_date = request.data.get('due_date')
        paid_status = request.data.get('paid_status', 'pending')  # Default is 'pending'

        # Validate required fields
        if not all([user_id, bonus_type, amount, due_date]):
            return Response({"detail": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # If bonus is marked as "paid"
        if paid_status == 'paid':
            # Calculate total_paid by summing all bonuses for this user
            existing_paid_bonuses = BonusType.objects.filter(user_id=user_id, paid_status='paid')
            total_paid = sum(float(bonus.amount) for bonus in existing_paid_bonuses) + float(amount)

            bonus = BonusType.objects.create(
                user_id=user_id,
                bonus_type=bonus_type,
                amount=amount,
                due_date=due_date,
                paid_status='paid',
                total_paid=total_paid,
            )
        else:
            # Create a bonus with "pending" status
            bonus = BonusType.objects.create(
                user_id=user_id,
                bonus_type=bonus_type,
                amount=amount,
                due_date=due_date,
                paid_status='pending',
                total_paid=0,  # No payment yet
            )

        serializer = BonusTypeSerializer(bonus)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def bonus_history(request):
    bonuses = BonusType.objects.all()
    serializer = BonusTypeSerializer(bonuses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def bonus_history_by_id(request, user_id):
    """
    Retrieve bonus history for a specific user by ID.
    """
    try:
        bonus = BonusType.objects.filter(user_id=user_id)
        if not bonus.exists():
            return Response(
                {"detail": "No bonus history found for the provided user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = BonusTypeSerializer(bonus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# --- Salary Management ---

@api_view(['POST'])
def create_salary(request):
    """
    Create a salary record for a user.
    """
    try:
        # Extract data from request
        user_id = request.data.get('user_id')
        annual_salary = request.data.get('annual_salary')
        bonus = request.data.get('bonus', "0")  # Default bonus to 0 if not provided
        effective_date = request.data.get('effective_date')

        # Validate required fields
        if not all([user_id, annual_salary, effective_date]):
            return Response(
                {"detail": "Missing required fields: 'user_id', 'annual_salary', or 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert effective_date to a datetime object
        try:
            effective_date = datetime.strptime(effective_date, "%Y-%m").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a salary record already exists for the user
        if Salary.objects.filter(user_id=user_id, effective_date__year=effective_date.year, effective_date__month=effective_date.month).exists():
            return Response(
                {"detail": "A salary record already exists for this user and effective date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the salary record
        salary = Salary.objects.create(
            user_id=user_id,
            annual_salary=annual_salary,
            bonus=bonus,
            effective_date=effective_date,
        )

        # Serialize and return the created salary record
        serializer = SalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
     
@api_view(['GET'])
def salary_history(request):
    try:
        # Fetch all salary records
        salaries = Salary.objects.all()
        
        # Serialize the data
        serializer = SalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Salary.DoesNotExist:
        # Handle case where Salary records do not exist
        return Response(
            {"error": "No salary records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# @api_view(['GET'])
# def salary_history(request):
#     try:
#         # Fetch all salary records (this will return an empty queryset if no records exist)
#         salaries = Salary.objects.all()
        
#         # Serialize the data
#         serializer = SalarySerializer(salaries, many=True)
        
#         # Return the serialized data (even if it's an empty list)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
#     except Exception as e:
#         # Handle unexpected errors (e.g., database issues)
#         return Response(
#             {"error": "An unexpected error occurred.", "details": str(e)},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


@api_view(['GET'])
def salary_history_by_id(request, user_id):
    try:
        # Filter salary records by employee_id (if provided)
        if user_id:
            salaries = Salary.objects.filter(user_id=user_id)
        else:
            salaries = Salary.objects.all()
        
        # Serialize the data
        serializer = SalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


            
@api_view(['POST'])
def create_supervisor_salary(request):
    """
    Create a salary record for a user.
    """
    try:
        # Extract data from request
        user_id = request.data.get('user_id')
        annual_salary = request.data.get('annual_salary')
        bonus = request.data.get('bonus', "0")  # Default bonus to 0 if not provided
        effective_date = request.data.get('effective_date')

        # Validate required fields
        if not all([user_id, annual_salary, effective_date]):
            return Response(
                {"detail": "Missing required fields: 'user_id', 'annual_salary', or 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert effective_date to a datetime object
        try:
            effective_date = datetime.strptime(effective_date, "%Y-%m").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a salary record already exists for the user
        if SupervisorSalary.objects.filter(user_id=user_id, effective_date__year=effective_date.year, effective_date__month=effective_date.month).exists():
            return Response(
                {"detail": "A salary record already exists for this user and effective date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the salary record
        salary = SupervisorSalary.objects.create(
            user_id=user_id,
            annual_salary=annual_salary,
            bonus=bonus,
            effective_date=effective_date,
        )

        # Serialize and return the created salary record
        serializer = SupervisorSalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['GET'])
def supervisor_salary_history(request):
    try:
        # Fetch all salary records
        salaries = SupervisorSalary.objects.all()
        
        # Serialize the data
        serializer = SupervisorSalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except SupervisorSalary.DoesNotExist:
        # Handle case where Salary records do not exist
        return Response(
            {"error": "No salary records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


        
        
@api_view(['POST'])
def create_manager_salary(request):
    """
    Create a salary record for a user.
    """
    try:
        # Extract data from request
        user_id = request.data.get('user_id')
        annual_salary = request.data.get('annual_salary')
        bonus = request.data.get('bonus', "0")  # Default bonus to 0 if not provided
        effective_date = request.data.get('effective_date')

        # Validate required fields
        if not all([user_id, annual_salary, effective_date]):
            return Response(
                {"detail": "Missing required fields: 'user_id', 'annual_salary', or 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert effective_date to a datetime object
        try:
            effective_date = datetime.strptime(effective_date, "%Y-%m").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a salary record already exists for the user
        if ManagerSalary.objects.filter(user_id=user_id, effective_date__year=effective_date.year, effective_date__month=effective_date.month).exists():
            return Response(
                {"detail": "A salary record already exists for this user and effective date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the salary record
        salary = ManagerSalary.objects.create(
            user_id=user_id,
            annual_salary=annual_salary,
            bonus=bonus,
            effective_date=effective_date,
        )

        # Serialize and return the created salary record
        serializer = ManagerSalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
def manager_salary_history(request):
    try:
        # Fetch all salary records
        salaries = ManagerSalary.objects.all()
        
        # Serialize the data
        serializer = ManagerSalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ManagerSalary.DoesNotExist:
        # Handle case where Salary records do not exist
        return Response(
            {"error": "No salary records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(['PUT'])
def update_manager_salary(request, id):
    """
    Update salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = ManagerSalary.objects.get(id=id)
        
        
        data = request.data.copy()
        effective_date = data.get('effective_date')
        
        
        if effective_date:
            try:
                effective_date = timezone.datetime.strptime(effective_date, "%Y-%m").date().replace(day=1)
                # Check if effective_date is in the future
                if effective_date <= timezone.now().date():
                    return Response(
                        {"detail": "Effective date must be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                data['effective_date'] = effective_date
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        serializer = ManagerSalarySerializer(salary, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Salary record updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ManagerSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['DELETE'])
def delete_manager_salary(request, id):
    """
    Delete salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = ManagerSalary.objects.get(id=id)
        
        # Delete the salary record
        salary.delete()
        return Response(
            {"detail": "Salary record deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ManagerSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Salary
from .serializers import SalarySerializer

@api_view(['PUT'])
def update_salary(request, id):
    """
    Update salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = Salary.objects.get(id=id)
        
        # Update the salary record
        serializer = SalarySerializer(salary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Salary record updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Salary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_salary(request, id):
    """
    Delete salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = Salary.objects.get(id=id)
        
        # Delete the salary record
        salary.delete()
        return Response(
            {"detail": "Salary record deleted successfully."},
            status=status.HTTP_200_OK
        )
    except Salary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PUT'])
def update_supervisor_salary(request, id):
    """
    Update salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = SupervisorSalary.objects.get(id=id)
        
        # Update the salary record
        serializer = SupervisorSalarySerializer(salary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Salary record updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except SupervisorSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_supervisor_salary(request, id):
    """
    Delete salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = SupervisorSalary.objects.get(id=id)
        
        # Delete the salary record
        salary.delete()
        return Response(
            {"detail": "Salary record deleted successfully."},
            status=status.HTTP_200_OK
        )
    except SupervisorSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


################### Hr Payroll Management Function code ####################################

@api_view(['POST'])
def hr_process_payroll(request):
    """
    Generate payroll for hrs, including salary calculations, payslip generation, and email notification.
    """
    month_str = request.data.get('month')
    hr_id = request.data.get('hr_id')

    if not month_str or not hr_id:
        return Response({'success': False, 'message': 'Hr ID and Month are required.'}, status=400)

    try:
        month = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return Response({'success': False, 'message': 'Invalid month format. Use YYYY-MM.'}, status=400)

    try:
        hr = Hr.objects.get(hr_id=hr_id)
    except Hr.DoesNotExist:
        return Response({'success': False, 'message': 'Hr not found.'}, status=404)

    salary = HrSalary.objects.filter(user_id=hr_id).first()

    if not salary:
        return Response({'success': False, 'message': 'Salary details not found for this supervisor.'}, status=404)

        
    if HrPayrollManagement.objects.filter(user_id=hr_id, month=month).exists():
        return Response({'success': False, 'message': 'Payslip for this month already generated.'}, status=200)

    if HrSalary.objects.filter(user_id=hr_id, effective_date__gte=month).exists():
        return Response({'success': False, 'message': 'Salary effective date has not started yet.'}, status=200)
    
    total_hours = Attendance.objects.filter(
        hr=hr, date__month=month.month, date__year=month.year
    ).aggregate(Sum('total_working_hours'))['total_working_hours__sum'] or 0

    overtime_hours = Attendance.objects.filter(
        hr=hr, date__month=month.month, date__year=month.year
    ).aggregate(Sum('overtime'))['overtime__sum'] or 0

    base_salary = float(salary.monthly_salary)
    per_day_rate = base_salary / 30 if base_salary > 0 else 0  
    per_hour_rate = per_day_rate / 8 if per_day_rate > 0 else 0  
    total_days = total_hours / 8 if total_hours > 0 else 0  
    net_salary = total_days * per_day_rate
    overtime_salary = overtime_hours * per_hour_rate

    payroll = HrPayrollManagement.objects.create(
        user=hr.username,
        user_id=hr.hr_id,
        month=month,
        email=hr.email,
        base_salary=base_salary,
        net_salary=net_salary,
        total_working_hours=total_hours,
        overtime_hours=overtime_hours,
        overtime_pay=overtime_salary,
    )

    try:
        pdf_path = create_payslip_pdf(payroll)  
    except Exception as e:
        return Response({'success': False, 'message': f'Error generating payslip: {str(e)}'}, status=500)

    payroll.pdf_path = pdf_path
    payroll.save()

    subject = f'Your Payslip for {month.strftime("%B %Y")}'
    html_message = render_to_string('payroll/payslip_view.html', {'payroll': payroll})
    plain_message = strip_tags(html_message)

    try:
        email = EmailMessage(
            subject, plain_message, DEFAULT_FROM_EMAIL, [hr.email]
        )
        email.attach_file(pdf_path)  
        email.send()
    except Exception as e:
        return Response({'success': False, 'message': f'Error sending email: {str(e)}'}, status=500)

    return Response({'success': True, 'payroll_id': payroll.id, 'pdf_path': pdf_path}, status=200)
# --- Bonus Man
@api_view(['GET'])
def hr_payroll_history(request):
    """
    Fetch payroll history with optional filters.
    """
    user_filter = request.query_params.get('user')
    month_filter = request.query_params.get('month')

    payrolls = HrPayrollManagement.objects.all()
    if user_filter:
        payrolls = payrolls.filter(user=user_filter)
    if month_filter:
        payrolls = payrolls.filter(
            month__year=month_filter[:4],
            month__month=month_filter[5:7]
        )

    data = [
        {
            "id": payroll.id,
            "user": payroll.user,
            "month": payroll.month.strftime("%Y-%m"),
            "net_salary": payroll.net_salary,
            "pdf_path": payroll.pdf_path,
        }
        for payroll in payrolls
    ]
    return Response(data)

@api_view(['GET'])
def hr_payroll_notification(request):
    user = request.session.get('user')
    notifications = HrPayrollNotification.objects.filter(user=user).order_by('-date', '-time')

    return Response({'notifications': notifications.values()})

@api_view(['POST'])
def create_hr_salary(request):
    """
    Create a salary record for a user.
    """
    try:
        # Extract data from request
        user_id = request.data.get('user_id')
        annual_salary = request.data.get('annual_salary')
        bonus = request.data.get('bonus', "0")  # Default bonus to 0 if not provided
        effective_date = request.data.get('effective_date')

        # Validate required fields
        if not all([user_id, annual_salary, effective_date]):
            return Response(
                {"detail": "Missing required fields: 'user_id', 'annual_salary', or 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert effective_date to a datetime object
        try:
            effective_date = datetime.strptime(effective_date, "%Y-%m").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a salary record already exists for the user
        if HrSalary.objects.filter(user_id=user_id, effective_date__year=effective_date.year, effective_date__month=effective_date.month).exists():
            return Response(
                {"detail": "A salary record already exists for this user and effective date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the salary record
        salary = HrSalary.objects.create(
            user_id=user_id,
            annual_salary=annual_salary,
            bonus=bonus,
            effective_date=effective_date,
        )

        # Serialize and return the created salary record
        serializer = HrSalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
def hr_salary_history(request):
    try:
        # Fetch all salary records
        salaries = HrSalary.objects.all()
        
        # Serialize the data
        serializer = HrSalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except HrSalary.DoesNotExist:
        # Handle case where Salary records do not exist
        return Response(
            {"error": "No salary records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


            
        
@api_view(['PUT'])
def update_hr_salary(request, id):
    """
    Update salary details for a specific record by ID.
    """
    try:
        
        salary = HrSalary.objects.get(id=id)
        
        
        data = request.data.copy()
        effective_date = data.get('effective_date')
        
        
        if effective_date:
            try:
                
                if len(effective_date.split('-')) == 2:  # Check if it's in YYYY-MM format
                    effective_date = f"{effective_date}-01"
                effective_date = timezone.datetime.strptime(effective_date, "%Y-%m-%d").date()
                
                if effective_date <= timezone.now().date():
                    return Response(
                        {"detail": "Effective date must be in the future."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                data['effective_date'] = effective_date
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use 'YYYY-MM' or 'YYYY-MM-DD' for 'effective_date'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        
        serializer = HrSalarySerializer(salary, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Salary record updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except HrSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def delete_hr_salary(request, id):
    """
    Delete salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = HrSalary.objects.get(id=id)
        
        # Delete the salary record
        salary.delete()
        return Response(
            {"detail": "Salary record deleted successfully."},
            status=status.HTTP_200_OK
        )
    except HrSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def supervisor_salary_history_by_id(request, id):
    """
    Retrieve salary details for a specific salary record by ID.
    """
    try:
        salary = SupervisorSalary.objects.get(id=id)  # Use get() for a single record
        serializer = SupervisorSalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SupervisorSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

        

@api_view(['GET'])
def manager_salary_history_by_id(request, id):
    """
    Retrieve salary history for a specific user by ID.
    """
    try:
        salaries = ManagerSalary.objects.filter(id=id)
        if not salaries.exists():
            return Response(
                {"detail": "No salary history found for the provided user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ManagerSalarySerializer(salaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@api_view(['GET'])
def employee_salary_history_by_id(request, id):
    """
    Retrieve salary history for a specific user by ID.
    """
    try:
        salaries = Salary.objects.filter(id=id)
        if not salaries.exists():
            return Response(
                {"detail": "No salary history found for the provided user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SalarySerializer(salaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )        

@api_view(['GET'])
def hr_salary_history_by_id(request, id):
    """
    Retrieve salary history for a specific user by ID.
    """
    try:
        salaries = HrSalary.objects.filter(id=id)
        if not salaries.exists():
            return Response(
                {"detail": "No salary history found for the provided user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = HrSalarySerializer(salaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

################### Ar Payroll Management Function code ####################################

@api_view(['POST'])
def ar_process_payroll(request):
    """
    Generate payroll for hrs, including salary calculations, payslip generation, and email notification.
    """
    month_str = request.data.get('month')
    ar_id = request.data.get('ar_id')

    if not month_str or not ar_id:
        return Response({'success': False, 'message': 'Hr ID and Month are required.'}, status=400)

    try:
        month = datetime.strptime(month_str, "%Y-%m")
    except ValueError:
        return Response({'success': False, 'message': 'Invalid month format. Use YYYY-MM.'}, status=400)

    try:
        ar = Ar.objects.get(ar_id=ar_id)
    except Ar.DoesNotExist:
        return Response({'success': False, 'message': 'Hr not found.'}, status=404)

    salary = ArSalary.objects.filter(user_id=ar_id).first()

    if not salary:
        return Response({'success': False, 'message': 'Salary details not found for this supervisor.'}, status=404)

        
    if ArPayrollManagement.objects.filter(user_id=ar_id, month=month).exists():
        return Response({'success': False, 'message': 'Payslip for this month already generated.'}, status=200)

    if ArSalary.objects.filter(user_id=ar_id, effective_date__gte=month).exists():
        return Response({'success': False, 'message': 'Salary effective date has not started yet.'}, status=200)
    
    total_hours = Attendance.objects.filter(
        ar=ar, date__month=month.month, date__year=month.year
    ).aggregate(Sum('total_working_hours'))['total_working_hours__sum'] or 0

    overtime_hours = Attendance.objects.filter(
        ar=ar, date__month=month.month, date__year=month.year
    ).aggregate(Sum('overtime'))['overtime__sum'] or 0

    base_salary = float(salary.monthly_salary)
    per_day_rate = base_salary / 30 if base_salary > 0 else 0  
    per_hour_rate = per_day_rate / 8 if per_day_rate > 0 else 0  
    total_days = total_hours / 8 if total_hours > 0 else 0  
    net_salary = total_days * per_day_rate
    overtime_salary = overtime_hours * per_hour_rate

    payroll = ArPayrollManagement.objects.create(
        user=ar.username,
        user_id=ar.ar_id,
        month=month,
        email=ar.email,
        base_salary=base_salary,
        net_salary=net_salary,
        total_working_hours=total_hours,
        overtime_hours=overtime_hours,
        overtime_pay=overtime_salary,
    )

    try:
        pdf_path = create_payslip_pdf(payroll)  
    except Exception as e:
        return Response({'success': False, 'message': f'Error generating payslip: {str(e)}'}, status=500)

    payroll.pdf_path = pdf_path
    payroll.save()

    subject = f'Your Payslip for {month.strftime("%B %Y")}'
    html_message = render_to_string('payroll/payslip_view.html', {'payroll': payroll})
    plain_message = strip_tags(html_message)

    try:
        email = EmailMessage(
            subject, plain_message, DEFAULT_FROM_EMAIL, [ar.email]
        )
        email.attach_file(pdf_path)  
        email.send()
    except Exception as e:
        return Response({'success': False, 'message': f'Error sending email: {str(e)}'}, status=500)

    return Response({'success': True, 'payroll_id': payroll.id, 'pdf_path': pdf_path}, status=200)
# --- Bonus Man
@api_view(['GET'])
def ar_payroll_history(request):
    """
    Fetch payroll history with optional filters.
    """
    user_filter = request.query_params.get('user')
    month_filter = request.query_params.get('month')

    payrolls = ArPayrollManagement.objects.all()
    if user_filter:
        payrolls = payrolls.filter(user=user_filter)
    if month_filter:
        payrolls = payrolls.filter(
            month__year=month_filter[:4],
            month__month=month_filter[5:7]
        )

    data = [
        {
            "id": payroll.id,
            "user": payroll.user,
            "month": payroll.month.strftime("%Y-%m"),
            "net_salary": payroll.net_salary,
            "pdf_path": payroll.pdf_path,
        }
        for payroll in payrolls
    ]
    return Response(data)

@api_view(['GET'])
def ar_payroll_notification(request):
    user = request.session.get('user')
    notifications = ArPayrollNotification.objects.filter(user=user).order_by('-date', '-time')

    return Response({'notifications': notifications.values()})

@api_view(['POST'])
def create_ar_salary(request):
    """
    Create a salary record for a user.
    """
    try:
        # Extract data from request
        user_id = request.data.get('user_id')
        annual_salary = request.data.get('annual_salary')
        bonus = request.data.get('bonus', "0")  # Default bonus to 0 if not provided
        effective_date = request.data.get('effective_date')

        # Validate required fields
        if not all([user_id, annual_salary, effective_date]):
            return Response(
                {"detail": "Missing required fields: 'user_id', 'annual_salary', or 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Convert effective_date to a datetime object
        try:
            effective_date = datetime.strptime(effective_date, "%Y-%m").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use 'YYYY-MM' for 'effective_date'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if a salary record already exists for the user
        if ArSalary.objects.filter(user_id=user_id, effective_date__year=effective_date.year, effective_date__month=effective_date.month).exists():
            return Response(
                {"detail": "A salary record already exists for this user and effective date."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create and save the salary record
        salary = ArSalary.objects.create(
            user_id=user_id,
            annual_salary=annual_salary,
            bonus=bonus,
            effective_date=effective_date,
        )

        # Serialize and return the created salary record
        serializer = ArSalarySerializer(salary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['GET'])
def ar_salary_history(request):
    try:
        # Fetch all salary records
        salaries = ArSalary.objects.all()
        
        # Serialize the data
        serializer = ArSalarySerializer(salaries, many=True)
        
        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ArSalary.DoesNotExist:
        # Handle case where Salary records do not exist
        return Response(
            {"error": "No salary records found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception as e:
        # Handle unexpected errors
        return Response(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


            
        
@api_view(['PUT'])
def update_ar_salary(request, id):
    """
    Update salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = ArSalary.objects.get(id=id)
        
        # Update the salary record
        serializer = ArSalarySerializer(salary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Salary record updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ArSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
def delete_ar_salary(request, id):
    """
    Delete salary details for a specific record by ID.
    """
    try:
        # Fetch the salary record
        salary = ArSalary.objects.get(id=id)
        
        # Delete the salary record
        salary.delete()
        return Response(
            {"detail": "Salary record deleted successfully."},
            status=status.HTTP_200_OK
        )
    except ArSalary.DoesNotExist:
        return Response(
            {"detail": "Salary record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def ar_salary_history_by_id(request, id):
    """
    Retrieve salary history for a specific user by ID.
    """
    try:
        salaries = ArSalary.objects.filter(id=id)
        if not salaries.exists():
            return Response(
                {"detail": "No salary history found for the provided user ID."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ArSalarySerializer(salaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"detail": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        

