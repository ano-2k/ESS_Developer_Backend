from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from authentication.models import Admin, Hr, Supervisor, Manager,Employee
from .models import AdministrativeTicket, HRTicket, SupervisorTicket, SystemTicket, OtherTicket,TicketReply,ManagerTicket,EmployeeTicket
from .serializers import (
    AdministrativeTicketSerializer, HRTicketSerializer,
    SupervisorTicketSerializer, SystemTicketSerializer, OtherTicketSerializer,ManagerTicketSerializer,EmployeeTicketSerializer,
    CombinedTicketSerializer, HelpdeskAdminSerializer, HelpdeskHrSerializer, HelpdeskSupervisorSerializer,HelpdeskManagerSerializer
)
import logging
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_administrative_ticket(request):
    logger.info("Received data for administrative ticket: %s", request.data)
    serializer = AdministrativeTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        manager_id = ticket.manager.manager_id if ticket.manager else None
        supervisor_id = ticket.supervisor.supervisor_id if ticket.supervisor else None
        hr_id = ticket.hr.hr_id if ticket.hr else None
        employee_id = ticket.employee.employee_id if ticket.employee else None
        logger.info("Other ticket created with ticket_id: %s, manager_id: %s, supervisor_id: %s ,hr_id: %s,employee_id: %s",
                    ticket.ticket_id, manager_id, supervisor_id,hr_id,employee_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for administrative ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_hr_ticket(request):
    logger.info("Received data for HR ticket: %s", request.data)
    serializer = HRTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        manager_id = ticket.manager.manager_id if ticket.manager else None
        supervisor_id = ticket.supervisor.supervisor_id if ticket.supervisor else None
        employee_id = ticket.employee.employee_id if ticket.employee else None
        logger.info("HR ticket created with ticket_id: %s, manager_id: %s, supervisor_id: %s,employee_id: %s", 
                    ticket.ticket_id, manager_id, supervisor_id,employee_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for HR ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_supervisor_ticket(request):
    logger.info("Received data for supervisor ticket: %s", request.data)
    serializer = SupervisorTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        manager_id = ticket.manager.manager_id if ticket.manager else None
        employee_id = ticket.employee.employee_id if ticket.employee else None
        logger.info("Supervisor ticket created with ticket_id: %s, manager_id: %s, employee_id: %s",
            ticket.ticket_id, manager_id, employee_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for supervisor ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#---------------------- Not Checked --------------
@api_view(['POST'])
def create_system_ticket(request):
    logger.info("Received data for system ticket: %s", request.data)
    serializer = SystemTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        manager_id = ticket.manager.manager_id if ticket.manager else None
        supervisor_id = ticket.supervisor.supervisor_id if ticket.supervisor else None
        hr_id = ticket.hr.hr_id if ticket.hr else None
        logger.info("Other ticket created with ticket_id: %s, manager_id: %s, supervisor_id: %s ,hr_id: %s",
                    ticket.ticket_id, manager_id, supervisor_id,hr_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for system ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#---------------------- Not Checked --------------

@api_view(['POST'])
def create_other_ticket(request):
    logger.info("Received data for other ticket: %s", request.data)
    serializer = OtherTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        manager_id = ticket.manager.manager_id if ticket.manager else None
        supervisor_id = ticket.supervisor.supervisor_id if ticket.supervisor else None
        hr_id = ticket.hr.hr_id if ticket.hr else None
        employee_id = ticket.employee.employee_id if ticket.employee else None
        logger.info("Other ticket created with ticket_id: %s, manager_id: %s, supervisor_id: %s ,hr_id: %s, employee_id: %s",
                    ticket.ticket_id, manager_id, supervisor_id,hr_id,employee_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for other ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ticket_list(request, manager_id):
    # Verify manager exists
    if not Manager.objects.filter(manager_id=manager_id).exists():
        return Response({"error": f"Manager with ID {manager_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Filter tickets by manager_id (string field in Manager model)
    admin_tickets = AdministrativeTicket.objects.filter(manager__manager_id=manager_id)
    hr_tickets = HRTicket.objects.filter(manager__manager_id=manager_id)
    supervisor_tickets = SupervisorTicket.objects.filter(manager__manager_id=manager_id)
    system_tickets = SystemTicket.objects.filter(manager__manager_id=manager_id)
    other_tickets = OtherTicket.objects.filter(manager__manager_id=manager_id)
    
    # Combine all filtered tickets into a single list
    all_tickets = list(admin_tickets) + list(hr_tickets) + list(supervisor_tickets) + list(system_tickets) + list(other_tickets)
    
    # Check if any tickets were found
    if not all_tickets:
        return Response({"message": "No tickets found for this manager"}, status=status.HTTP_204_NO_CONTENT)
    
    # Serialize the combined list
    serializer = CombinedTicketSerializer(all_tickets, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_assigned_tickets(request, user_id):
    if not Admin.objects.filter(user_id=user_id).exists():
        return Response({"error": f"Admin with user_id {user_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    # Original admin tickets
    tickets = AdministrativeTicket.objects.filter(
        raise_to__user_id=user_id
    )
    # Newly added other tickets
    other_tickets = OtherTicket.objects.filter(
        raise_to__user_id=user_id
    )
    # Combine both into a single list
    all_tickets = list(tickets) + list(other_tickets)
    if not all_tickets:
        return Response({"message": "No tickets found for this admin"}, status=status.HTTP_204_NO_CONTENT)
    # Original serializer for admin tickets
    serializer = AdministrativeTicketSerializer(tickets, many=True)
    # New serializer for other tickets (use a different variable)
    other_serializer = OtherTicketSerializer(other_tickets, many=True)
    # Combine both serialized data
    combined_data = serializer.data + other_serializer.data
    return Response(combined_data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_assigned_hr_tickets(request, hr_id):
    if not Hr.objects.filter(hr_id=hr_id).exists():
        return Response({"error": f"HR with hr_id {hr_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tickets = HRTicket.objects.filter(
        raise_to__hr_id=hr_id
    )
    
    if not tickets.exists():
        return Response({"message": "No tickets found for this HR"}, status=status.HTTP_204_NO_CONTENT)
    
    serializer = HRTicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_assigned_supervisor_tickets(request, supervisor_id):
    if not Supervisor.objects.filter(supervisor_id=supervisor_id).exists():
        return Response({"error": f"Supervisor with supervisor_id {supervisor_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tickets = SupervisorTicket.objects.filter(
        raise_to__supervisor_id=supervisor_id
    )
    
    if not tickets.exists():
        return Response({"message": "No tickets found for this Supervisor"}, status=status.HTTP_204_NO_CONTENT)
    
    serializer = SupervisorTicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_assigned_manager_tickets(request, manager_id):
    if not Manager.objects.filter(manager_id=manager_id).exists():
        return Response({"error": f"Manager with manager_id {manager_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tickets = ManagerTicket.objects.filter(
        raise_to__manager_id=manager_id
    )
    
    if not tickets.exists():
        return Response({"message": "No tickets found for this Manager"}, status=status.HTTP_204_NO_CONTENT)
    
    serializer = ManagerTicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_assigned_employee_tickets(request, employee_id):
    if not Employee.objects.filter(employee_id=employee_id).exists():
        return Response({"error": f"Employee with employee_id {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    tickets = EmployeeTicket.objects.filter(
        raise_to__employee_id=employee_id
    )
    
    if not tickets.exists():
        return Response({"message": "No tickets found for this Employee"}, status=status.HTTP_204_NO_CONTENT)
    
    serializer = EmployeeTicketSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def ticket_reply(request, ticket_id):
    reply_text = request.data.get('reply_text')
    if not reply_text:
        return Response({"error": "Reply text is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    ticket = None
    for model in [AdministrativeTicket, HRTicket, SupervisorTicket, ManagerTicket,OtherTicket]:
        try:
            ticket = model.objects.get(ticket_id=ticket_id)
            break
        except model.DoesNotExist:
            continue
    
    if not ticket:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Create reply
    content_type = ContentType.objects.get_for_model(ticket)
    TicketReply.objects.create(
        content_type=content_type,
        object_id=ticket.id,
        reply_text=reply_text
    )
    
    # Update ticket status and timestamp
    ticket.status = 'Review'
    ticket.last_updated = timezone.now()
    ticket.save()
    
    return Response({"message": "Reply submitted successfully"}, status=status.HTTP_200_OK)

@api_view(['PATCH'])
def ticket_update(request, ticket_id):
    ticket = None
    for model in [AdministrativeTicket, HRTicket, SupervisorTicket, SystemTicket, OtherTicket,ManagerTicket]:
        try:
            ticket = model.objects.get(ticket_id=ticket_id)
            break
        except model.DoesNotExist:
            continue
    
    if not ticket:
        return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer_class = {
        AdministrativeTicket: AdministrativeTicketSerializer,
        HRTicket: HRTicketSerializer,
        SupervisorTicket: SupervisorTicketSerializer,
        SystemTicket: SystemTicketSerializer,
        OtherTicket: OtherTicketSerializer,
        ManagerTicket: ManagerTicketSerializer
    }.get(type(ticket))
    
    serializer = serializer_class(ticket, data=request.data, partial=True)
    if serializer.is_valid():
        ticket.last_updated = timezone.now()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def helpdesk_admin_list(request):
    try:
        admins = Admin.objects.all()
        serializer = HelpdeskAdminSerializer(admins, many=True)
        logger.info("Successfully retrieved admin list for helpdesk")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Error retrieving admin list: %s", str(e))
        return Response({"error": "Failed to retrieve admin list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def helpdesk_hr_list(request):
    try:
        hrs = Hr.objects.all()
        serializer = HelpdeskHrSerializer(hrs, many=True)
        logger.info("Successfully retrieved HR list for helpdesk")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Error retrieving HR list: %s", str(e))
        return Response({"error": "Failed to retrieve HR list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def helpdesk_supervisor_list(request):
    try:
        supervisors = Supervisor.objects.all()
        serializer = HelpdeskSupervisorSerializer(supervisors, many=True)
        logger.info("Successfully retrieved supervisor list for helpdesk")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Error retrieving supervisor list: %s", str(e))
        return Response({"error": "Failed to retrieve supervisor list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    #---------------------------------------------------------------------------------------------------------------------------
    
@api_view(['GET'])
def supervisor_ticket_list(request, supervisor_id):
    # Verify supervisor exists
    if not Supervisor.objects.filter(supervisor_id=supervisor_id).exists():
        return Response({"error": f"Supervisor with ID {supervisor_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Filter tickets by supervisor_id (string field in Supervisor model)
    admin_tickets = AdministrativeTicket.objects.filter(supervisor__supervisor_id=supervisor_id)
    hr_tickets = HRTicket.objects.filter(supervisor__supervisor_id=supervisor_id)
    system_tickets = SystemTicket.objects.filter(supervisor__supervisor_id=supervisor_id)
    other_tickets = OtherTicket.objects.filter(supervisor__supervisor_id=supervisor_id)
    
    # Combine all filtered tickets into a single list
    all_tickets = list(admin_tickets) + list(hr_tickets) + list(system_tickets) + list(other_tickets)
    
    # Check if any tickets were found
    if not all_tickets:
        return Response({"message": "No tickets found for this supervisor"}, status=status.HTTP_204_NO_CONTENT)
    
    # Serialize the combined list
    serializer = CombinedTicketSerializer(all_tickets, many=True)
    return Response(serializer.data)

#---------------------------------------------------------------------------------------------------------------

@api_view(['GET'])
def hr_ticket_list(request, hr_id):
    # Verify HR exists
    if not Hr.objects.filter(hr_id=hr_id).exists():
        return Response({"error": f"HR with ID {hr_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Filter tickets by hr_id (string field in HR model)
    admin_tickets = AdministrativeTicket.objects.filter(hr__hr_id=hr_id)
    system_tickets = SystemTicket.objects.filter(hr__hr_id=hr_id)
    other_tickets = OtherTicket.objects.filter(hr__hr_id=hr_id)
    
    # Combine all filtered tickets into a single list
    all_tickets = list(admin_tickets) + list(system_tickets) + list(other_tickets)
    
    # Check if any tickets were found
    if not all_tickets:
        return Response({"message": "No tickets found for this HR"}, status=status.HTTP_204_NO_CONTENT)
    
    # Serialize the combined list
    serializer = CombinedTicketSerializer(all_tickets, many=True)
    return Response(serializer.data)


#-------------------------------------------------------------------------------------------------------


@api_view(['GET'])
def employee_ticket_list(request, employee_id):
    # Verify employee exists
    if not Employee.objects.filter(employee_id=employee_id).exists():
        return Response({"error": f"Employee with ID {employee_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Filter tickets by employee_id (string field in ticket models)
    admin_tickets = AdministrativeTicket.objects.filter(employee__employee_id=employee_id)
    hr_tickets = HRTicket.objects.filter(employee__employee_id=employee_id)
    supervisor_tickets = SupervisorTicket.objects.filter(employee__employee_id=employee_id)
    manager_tickets = ManagerTicket.objects.filter(employee__employee_id=employee_id)
    system_tickets = SystemTicket.objects.filter(employee__employee_id=employee_id)
    other_tickets = OtherTicket.objects.filter(employee__employee_id=employee_id)
    
    # Combine all filtered tickets into a single list
    all_tickets = list(admin_tickets) + list(hr_tickets) + list(supervisor_tickets) + list(manager_tickets) + list(system_tickets) + list(other_tickets)
    
    # Check if any tickets were found
    if not all_tickets:
        return Response({"message": "No tickets found for this employee"}, status=status.HTTP_204_NO_CONTENT)
    
    # Serialize the combined list
    serializer = CombinedTicketSerializer(all_tickets, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def helpdesk_manager_list(request):
    try:
        managers = Manager.objects.all()
        serializer = HelpdeskManagerSerializer(managers, many=True)
        logger.info("Successfully retrieved manager list for helpdesk")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error("Error retrieving manager list: %s", str(e))
        return Response({"error": "Failed to retrieve manager list"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def create_manager_ticket(request):
    logger.info("Received data for manager ticket: %s", request.data)
    serializer = ManagerTicketSerializer(data=request.data)
    if serializer.is_valid():
        ticket = serializer.save()
        employee_id = ticket.employee.employee_id if ticket.employee else None
        logger.info("Manager ticket created with ticket_id: %s, employee_id: %s",
                    ticket.ticket_id, employee_id)
        return Response({"ticket_id": ticket.ticket_id, "message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)
    logger.error("Validation errors for manager ticket: %s", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)