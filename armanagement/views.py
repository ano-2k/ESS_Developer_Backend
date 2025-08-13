from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.db.models import Sum, Q, F
from rest_framework import serializers, views, response, status
from datetime import timedelta

from Payment_In.models import RecordPayment
from Pincode.models import AddParty
from Sales_Invoice.models import SalesInvoice
from armanagement.models import ARReminder, Target, ARClientTarget
from armanagement.serializers import ARClientTargetSerializer, AREmployeeTargetSerializer, ARReminderSerializer, TargetSerializer
from authentication.models import Employee 
from Sales_Person.models import SalesPerson


# Create your views here.

@api_view(['GET'])
def client_summary(request, client_id):
    client = AddParty.objects.get(id=client_id)
    invoices = filter_by_custom_date_range(SalesInvoice.objects.filter(party=client), 'invoice_date', request)
    payments = filter_by_custom_date_range(RecordPayment.objects.filter(party=client), 'payment_date', request)

    total_sales = invoices.aggregate(total=Sum('total_amount__total'))['total'] or 0
    received = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
    outstanding = total_sales - received

    overdue = invoices.filter(due_date__lt=timezone.now().date(), balance_amount__gt=0)
    overdue_total = overdue.aggregate(total=Sum('balance_amount'))['total'] or 0

    reminders = ARReminder.objects.filter(invoice__party=client)
    reminder_data = ARReminderSerializer(reminders, many=True).data

    target_obj = client.ar_targets.last()
    target = target_obj.target_amount if target_obj else 0

    return response.Response({
        "total_sales": total_sales,
        "received_payments": received,
        "outstanding_dues": outstanding,
        "overdue_payments": overdue_total,
        "target_billing": target,
        "raised_billing": total_sales,
        "reminders": reminder_data,
    })

@api_view(['GET'])
def employee_summary(request, employee_id):
    employee = Employee.objects.get(id=employee_id)
    clients = AddParty.objects.filter(sales_person=employee)
    invoices = SalesInvoice.objects.filter(party__in=clients)

    invoices_filtered = filter_by_custom_date_range(invoices, 'invoice_date', request)
    payments = filter_by_custom_date_range(RecordPayment.objects.filter(party__in=clients), 'payment_date', request)

    total_invoiced = invoices_filtered.aggregate(total=Sum('total_amount__total'))['total'] or 0
    total_collected = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
    outstanding = total_invoiced - total_collected

    overdue = invoices_filtered.filter(due_date__lt=timezone.now().date(), balance_amount__gt=0)
    overdue_total = overdue.aggregate(total=Sum('balance_amount'))['total'] or 0

    target_obj = employee.collection_targets.last()
    target = target_obj.target_amount if target_obj else 0

    return response.Response({
        "total_sales": total_invoiced,
        "received_payments": total_collected,
        "outstanding_dues": outstanding,
        "overdue_payments": overdue_total,
        "collection_target": target,
    })

@api_view(['POST'])
def send_reminder(request):
    serializer = ARReminderSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
    return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def set_client_target(request):
    serializer = ARClientTargetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data)
    return response.Response(serializer.errors, status=400)

@api_view(['POST'])
def set_employee_target(request):
    serializer = AREmployeeTargetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return response.Response(serializer.data)
    return response.Response(serializer.errors, status=400)





@api_view(['GET'])
def total_clients_summary(request):
    invoices = filter_by_custom_date_range(SalesInvoice.objects.all(), 'invoice_date', request)
    payments = filter_by_custom_date_range(RecordPayment.objects.all(), 'payment_date', request)

    total_sales = invoices.aggregate(total=Sum('total_amount__total'))['total'] or 0
    total_collected = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
    outstanding = total_sales - total_collected

    overdue = invoices.filter(due_date__lt=timezone.now().date(), balance_amount__gt=0)
    overdue_total = overdue.aggregate(total=Sum('balance_amount'))['total'] or 0

    return response.Response({
        "total_sales": total_sales,
        "received_payments": total_collected,
        "outstanding_dues": outstanding,
        "overdue_payments": overdue_total
    })

@api_view(['GET'])
def total_employees_summary(request):
    employees = Employee.objects.all()
    results = []
    for emp in employees:
        clients = AddParty.objects.filter(sales_person=emp)
        invoices = filter_by_custom_date_range(SalesInvoice.objects.filter(party__in=clients), 'invoice_date', request)
        payments = filter_by_custom_date_range(RecordPayment.objects.filter(party__in=clients), 'payment_date', request)

        total_invoiced = invoices.aggregate(total=Sum('total_amount__total'))['total'] or 0
        total_collected = payments.aggregate(total=Sum('payment_amount'))['total'] or 0
        overdue_total = invoices.filter(due_date__lt=timezone.now().date(), balance_amount__gt=0).aggregate(total=Sum('balance_amount'))['total'] or 0

        results.append({
            "employee_id": emp.id,
            "employee_name": emp.name,
            "total_sales": total_invoiced,
            "received_payments": total_collected,
            "outstanding_dues": total_invoiced - total_collected,
            "overdue_payments": overdue_total
        })
    return response.Response(results)


def filter_by_custom_date_range(queryset, field_name, request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date or not end_date:
        return queryset.none()
    return queryset.filter(**{
        f"{field_name}__date__gte": start_date,
        f"{field_name}__date__lte": end_date
    })



#new added

@api_view(['POST'])
def create_target(request):
    serializer = TargetSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_all_targets(request):
    targets = Target.objects.all()
    serializer = TargetSerializer(targets, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_target_by_id(request, pk):
    try:
        target = Target.objects.get(pk=pk)
    except Target.DoesNotExist:
        return Response({'error': 'Target not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TargetSerializer(target)
    return Response(serializer.data)

@api_view(['PUT'])
def update_target(request, pk):
    try:
        target = Target.objects.get(pk=pk)
    except Target.DoesNotExist:
        return Response({'error': 'Target not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = TargetSerializer(target, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_target(request, pk):
    try:
        target = Target.objects.get(pk=pk)
    except Target.DoesNotExist:
        return Response({'error': 'Target not found'}, status=status.HTTP_404_NOT_FOUND)
    
    target.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

# NEWLY ADDED ON JUNE 09 

@api_view(['POST'])
def create_client_target(request):
    employee_id = request.data.get('employee_id')
    client_id = request.data.get('client')
    
    # Determine if the employee is a SalesPerson for the client
    sales_person = None
    if client_id and employee_id:
        try:
            client = AddParty.objects.get(id=client_id)
            try:
                employee = Employee.objects.get(employee_id=employee_id)
                sales_person_instance = SalesPerson.objects.get(employee=employee)
                if client.sales_person and client.sales_person.id == sales_person_instance.id:
                    sales_person = sales_person_instance
            except (Employee.DoesNotExist, SalesPerson.DoesNotExist):
                pass  # If employee or SalesPerson doesn't exist, sales_person remains null
        except AddParty.DoesNotExist:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
    
    # Prepare data for serializer
    data = request.data.copy()
    data['sales_person'] = sales_person.id if sales_person else None
    
    serializer = ARClientTargetSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# NEWLY ADDED ON JUNE 09 

@api_view(['GET'])
def get_client_targets(request, employee_id): 
    targets = ARClientTarget.objects.none()  
    if employee_id:
        try:
            employee = Employee.objects.get(employee_id=employee_id)
            try:
                sales_person = SalesPerson.objects.get(employee=employee)
                targets = ARClientTarget.objects.filter(sales_person=sales_person)
            except SalesPerson.DoesNotExist:
                targets = ARClientTarget.objects.filter(sales_person__isnull=True, client__sales_person__isnull=True)
        except Employee.DoesNotExist:
            pass  # If employee doesn't exist, return empty queryset
    
    serializer = ARClientTargetSerializer(targets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
