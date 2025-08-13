# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Employee, Manager, Supervisor, Admin, ManagingDirector, Group, Message, UnreadMessage, GroupChatMessage, MessageStatus
from .serializers import GroupSerializer, EmployeeSerializer, ManagerSerializer, SupervisorSerializer, AdminSerializer, ManagingDirectorSerializer, MessageSerializer, UnreadMessageSerializer

class EmployeeChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_employee_id = request.user.id  # Assuming user is authenticated via token/session

        # Fetch all entities (Employees, Managers, Supervisors, Admins, MDs)
        employees = Employee.objects.all()
        managers = Manager.objects.all()
        supervisors = Supervisor.objects.all()
        admins = Admin.objects.all()
        mds = ManagingDirector.objects.all()

        # Fetch groups where the current employee is a member
        groups = Group.objects.filter(employees__employee_id=current_employee_id)

        # Process data for employees using the existing EmployeeSerializer
        employee_data = EmployeeSerializer(employees, many=True).data
        for employee in employee_data:
            unread_count = Message.objects.filter(receiver_id=current_employee_id, sender_id=employee['id'], is_read=False).count()
            employee['unread_count'] = unread_count

            last_received_message = Message.objects.filter(receiver_id=current_employee_id, sender_id=employee['id']).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_employee_id, receiver_id=employee['id']).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None
            
            # Update the employee data with the last message details
            employee['last_message'] = last_message.content if last_message else None
            employee['last_message_sent_by_current_user'] = last_message is not None and (last_message.sender_id == current_employee_id)
            if last_message:
                employee['last_message_is_read'] = last_message.is_read
                employee['last_message_delivered'] = last_message.is_delivered
            else:
                employee['last_message_is_read'] = False
                employee['last_message_delivered'] = False

        # Similarly process managers, supervisors, admins, and MDs using their respective serializers
        manager_data = ManagerSerializer(managers, many=True).data
        supervisor_data = SupervisorSerializer(supervisors, many=True).data
        admin_data = AdminSerializer(admins, many=True).data
        md_data = ManagingDirectorSerializer(mds, many=True).data

        # Fetch unread messages in the group chat
        unread_group_count = UnreadMessage.objects.filter(user_id=current_employee_id).count()
        last_group_message = Message.objects.filter(chat_type='group_chat').order_by('-timestamp').first()

        # Serialize groups using the GroupSerializer
        group_data = GroupSerializer(groups, many=True).data

        # Prepare the final response data
        response_data = {
            'employees': employee_data,
            'managers': manager_data,
            'supervisors': supervisor_data,
            'admins': admin_data,
            'mds': md_data,
            'groups': group_data,
            'unread_count': unread_group_count,
            'last_group_message': last_group_message.content if last_group_message else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class SupervisorChatView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        if request.user.role != 'supervisor':  # Check if the user is a supervisor
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        current_supervisor_id = request.user.id  # Assuming user is authenticated and has 'id' and 'role' attributes

        # Fetch all employees and managers
        employees = Employee.objects.all()
        managers = Manager.objects.all()
        supervisors = Supervisor.objects.all()
        admins = Admin.objects.all()
        mds = ManagingDirector.objects.all()

        # Fetch groups where the current supervisor is a member
        groups = Group.objects.filter(supervisors__supervisor_id=current_supervisor_id)

        # Process employees, managers, supervisors, admins, and mds with their last message data
        employee_data = EmployeeSerializer(employees, many=True).data
        manager_data = ManagerSerializer(managers, many=True).data
        supervisor_data = SupervisorSerializer(supervisors, many=True).data
        admin_data = AdminSerializer(admins, many=True).data
        md_data = ManagingDirectorSerializer(mds, many=True).data

        # Update employees' last message, unread count, and other details
        for employee in employee_data:
            unread_count = Message.objects.filter(receiver_id=current_supervisor_id, sender_id=employee['id'], is_read=False).count()
            employee['unread_count'] = unread_count

            last_received_message = Message.objects.filter(receiver_id=current_supervisor_id, sender_id=employee['id']).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_supervisor_id, receiver_id=employee['id']).order_by('-timestamp').first()

            last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp) if last_received_message and last_sent_message else last_received_message or last_sent_message
            employee['last_message'] = last_message.content if last_message else None
            employee['last_message_sent_by_current_user'] = last_message and last_message.sender_id == current_supervisor_id
            if last_message:
                employee['last_message_is_read'] = last_message.is_read
                employee['last_message_delivered'] = last_message.is_delivered
            else:
                employee['last_message_is_read'] = False
                employee['last_message_delivered'] = False

        # Similarly update other data for managers, supervisors, admins, and MDs

        for manager in manager_data:
            unread_count = Message.objects.filter(receiver_id=current_supervisor_id, sender_id=manager['id'], is_read=False).count()
            manager['unread_count'] = unread_count
            last_received_message = Message.objects.filter(receiver_id=current_supervisor_id, sender_id=manager['id']).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_supervisor_id, receiver_id=manager['id']).order_by('-timestamp').first()

            last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp) if last_received_message and last_sent_message else last_received_message or last_sent_message
            manager['last_message'] = last_message.content if last_message else None
            manager['last_message_sent_by_current_user'] = last_message and last_message.sender_id == current_supervisor_id
            if last_message:
                manager['last_message_is_read'] = last_message.is_read
                manager['last_message_delivered'] = last_message.is_delivered
            else:
                manager['last_message_is_read'] = False
                manager['last_message_delivered'] = False

        # Add similar updates for supervisors, admins, and mds...

        # Get the unread message count in the group chat
        unread_count = UnreadMessage.objects.filter(user_id=current_supervisor_id).count()

        # Get the last message in the common group chat
        last_group_message = Message.objects.filter(chat_type='group_chat').order_by('-timestamp').first()

        # Process groups to get the last message for each group
        group_data = GroupSerializer(groups, many=True).data
        for group in group_data:
            last_custom_group_message = GroupChatMessage.objects.filter(group=group['id']).order_by('-timestamp').first()
            group['last_message'] = last_custom_group_message.message if last_custom_group_message else "No messages yet."
            group['last_message_sent_by_current_user'] = last_custom_group_message and last_custom_group_message.sender_id == current_supervisor_id

        # Iterate through each group and count unread messages
        for group in group_data:
            group['unread_group_count'] = MessageStatus.objects.filter(
                user_id=current_supervisor_id,
                message__group=group['id'],  # Filter by current group
                is_read=False
            ).count()

        # Prepare the response data
        response_data = {
            'employees': employee_data,
            'managers': manager_data,
            'supervisors': supervisor_data,
            'admins': admin_data,
            'mds': md_data,
            'groups': group_data,
            'unread_count': unread_count,
            'last_group_message': last_group_message.content if last_group_message else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Employee, Manager, Supervisor, Admin, ManagingDirector, Message, Group, GroupChatMessage, MessageStatus, UnreadMessage

class ManagerChatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'manager':
            return Response({'detail': 'Unauthorized'}, status=401)

        current_manager_id = request.user.id  # assuming the manager's ID is in the user object

        # Fetch all employees, managers, supervisors, admins, and mds
        employees = Employee.objects.all()
        managers = Manager.objects.all()
        supervisors = Supervisor.objects.all()
        admins = Admin.objects.all()
        mds = ManagingDirector.objects.all()

        # Fetch groups where the current manager is a member
        groups = Group.objects.filter(managers__manager_id=current_manager_id)

        # Process employees
        employee_data = []
        for employee in employees:
            unread_count = Message.objects.filter(receiver_id=current_manager_id, sender_id=employee.employee_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_manager_id, sender_id=employee.employee_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_manager_id, receiver_id=employee.employee_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            employee_data.append({
                'employee_id': employee.employee_id,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_manager_id if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Process supervisors
        supervisor_data = []
        for supervisor in supervisors:
            unread_count = Message.objects.filter(receiver_id=current_manager_id, sender_id=supervisor.supervisor_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_manager_id, sender_id=supervisor.supervisor_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_manager_id, receiver_id=supervisor.supervisor_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            supervisor_data.append({
                'supervisor_id': supervisor.supervisor_id,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_manager_id if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Process managers
        manager_data = []
        for manager in managers:
            unread_count = Message.objects.filter(receiver_id=current_manager_id, sender_id=manager.manager_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_manager_id, sender_id=manager.manager_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_manager_id, receiver_id=manager.manager_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            manager_data.append({
                'manager_id': manager.manager_id,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_manager_id if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Process admins
        admin_data = []
        for admin in admins:
            unread_count = Message.objects.filter(receiver_id=current_manager_id, sender_id=admin.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_manager_id, sender_id=admin.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_manager_id, receiver_id=admin.username).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            admin_data.append({
                'admin_id': admin.username,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_manager_id if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Process MDs
        md_data = []
        for md in mds:
            unread_count = Message.objects.filter(receiver_id=current_manager_id, sender_id=md.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_manager_id, sender_id=md.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_manager_id, receiver_id=md.username).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            md_data.append({
                'md_id': md.username,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_manager_id if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Process groups
        group_data = []
        for group in groups:
            last_custom_group_message = GroupChatMessage.objects.filter(group=group).order_by('-timestamp').first()
            unread_group_count = MessageStatus.objects.filter(user_id=current_manager_id, message__group=group, is_read=False).count()

            group_data.append({
                'id': group.id,
                'last_message': last_custom_group_message.message if last_custom_group_message else "No messages yet.",
                'last_message_sent_by_current_user': last_custom_group_message and last_custom_group_message.sender_id == current_manager_id,
                'unread_group_count': unread_group_count,
            })

        unread_count = UnreadMessage.objects.filter(user_id=current_manager_id).count()

        # Combine the response data
        response_data = {
            'employees': employee_data,
            'supervisors': supervisor_data,
            'managers': manager_data,
            'admins': admin_data,
            'mds': md_data,
            'groups': group_data,
            'unread_count': unread_count,
        }

        return Response(response_data)

class AdminChatAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if 'user' not in request.session or request.session.get('role') != 'admin':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        current_admin_username = request.session.get('user')

        # Fetch all employees, managers, supervisors, admins, and mds
        employees = Employee.objects.all()
        managers = Manager.objects.all()
        supervisors = Supervisor.objects.all()
        admins = Admin.objects.all()
        mds = ManagingDirector.objects.all()

        # Fetch groups where the current admin is a member
        groups = Group.objects.filter(admins__username=current_admin_username)

        # Initialize the response data
        response_data = {
            "employees": [],
            "managers": [],
            "supervisors": [],
            "admins": [],
            "mds": [],
            "groups": [],
        }

        # Process employees
        for employee in employees:
            unread_count = Message.objects.filter(receiver_id=current_admin_username, sender_id=employee.employee_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_admin_username, sender_id=employee.employee_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_admin_username, receiver_id=employee.employee_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            response_data['employees'].append({
                "employee_id": employee.employee_id,
                "unread_count": unread_count,
                "last_message": last_message.content if last_message else None,
                "last_message_sent_by_current_user": last_message is not None and (last_message.sender_id == current_admin_username),
                "last_message_is_read": last_message.is_read if last_message else False,
                "last_message_delivered": last_message.is_delivered if last_message else False
            })

        # Process managers
        for manager in managers:
            unread_count = Message.objects.filter(receiver_id=current_admin_username, sender_id=manager.manager_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_admin_username, sender_id=manager.manager_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_admin_username, receiver_id=manager.manager_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            response_data['managers'].append({
                "manager_id": manager.manager_id,
                "unread_count": unread_count,
                "last_message": last_message.content if last_message else None,
                "last_message_sent_by_current_user": last_message is not None and (last_message.sender_id == current_admin_username),
                "last_message_is_read": last_message.is_read if last_message else False,
                "last_message_delivered": last_message.is_delivered if last_message else False
            })

        # Process supervisors
        for supervisor in supervisors:
            unread_count = Message.objects.filter(receiver_id=current_admin_username, sender_id=supervisor.supervisor_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_admin_username, sender_id=supervisor.supervisor_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_admin_username, receiver_id=supervisor.supervisor_id).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            response_data['supervisors'].append({
                "supervisor_id": supervisor.supervisor_id,
                "unread_count": unread_count,
                "last_message": last_message.content if last_message else None,
                "last_message_sent_by_current_user": last_message is not None and (last_message.sender_id == current_admin_username),
                "last_message_is_read": last_message.is_read if last_message else False,
                "last_message_delivered": last_message.is_delivered if last_message else False
            })

        # Process admins (this admin itself will be excluded based on context)
        for admin in admins:
            if admin.username == current_admin_username:
                continue  # Skip the current admin (the one who requested the data)
            unread_count = Message.objects.filter(receiver_id=current_admin_username, sender_id=admin.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_admin_username, sender_id=admin.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_admin_username, receiver_id=admin.username).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            response_data['admins'].append({
                "admin_id": admin.id,
                "unread_count": unread_count,
                "last_message": last_message.content if last_message else None,
                "last_message_sent_by_current_user": last_message is not None and (last_message.sender_id == current_admin_username),
                "last_message_is_read": last_message.is_read if last_message else False,
                "last_message_delivered": last_message.is_delivered if last_message else False
            })

        # Process managing directors (mds)
        for md in mds:
            unread_count = Message.objects.filter(receiver_id=current_admin_username, sender_id=md.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_admin_username, sender_id=md.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_admin_username, receiver_id=md.username).order_by('-timestamp').first()

            last_message = None
            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message

            response_data['mds'].append({
                "md_id": md.id,
                "unread_count": unread_count,
                "last_message": last_message.content if last_message else None,
                "last_message_sent_by_current_user": last_message is not None and (last_message.sender_id == current_admin_username),
                "last_message_is_read": last_message.is_read if last_message else False,
                "last_message_delivered": last_message.is_delivered if last_message else False
            })

        # Process groups
        for group in groups:
            last_custom_group_message = GroupChatMessage.objects.filter(group=group).order_by('-timestamp').first()
            last_message = last_custom_group_message.message if last_custom_group_message else "No messages yet."

            response_data['groups'].append({
                "group_name": group.name,
                "last_message": last_message,
                "last_message_sent_by_current_user": last_custom_group_message and last_custom_group_message.sender_id == current_admin_username,
            })

        # Unread message count and last group message
        unread_count = UnreadMessage.objects.filter(user_id=current_admin_username).count()
        last_group_message = Message.objects.filter(chat_type='group_chat').order_by('-timestamp').first()

        return Response({
            **response_data,
            'unread_count': unread_count,
            'last_group_message': last_group_message.content if last_group_message else None,
        })
        
# views.py
from rest_framework import status, views
from rest_framework.response import Response
from .models import Employee, Manager, Admin, Supervisor, ManagingDirector, Group, Message, GroupChatMessage, MessageStatus
from .serializers import EmployeeSerializer, ManagerSerializer, AdminSerializer, SupervisorSerializer, GroupSerializer


class MDChatView(views.APIView):
    def get(self, request, *args, **kwargs):
        # Authentication check for MD role
        if 'user' not in request.session or request.session.get('role') != 'md':
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        
        current_md_username = request.session.get('user')

        # Fetch employees, managers, admins, supervisors, and managing directors
        employees = Employee.objects.all()
        managers = Manager.objects.all()
        admins = Admin.objects.all()
        supervisors = Supervisor.objects.all()
        mds = ManagingDirector.objects.all()

        # Fetch groups where the current MD is a member
        groups = Group.objects.filter(mds__username=current_md_username)

        # Processing employees and messages
        employee_data = []
        for employee in employees:
            unread_count = Message.objects.filter(receiver_id=current_md_username, sender_id=employee.employee_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_md_username, sender_id=employee.employee_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_md_username, receiver_id=employee.employee_id).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None

            employee_data.append({
                'id': employee.id,
                'name': employee.name,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_md_username if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Processing supervisors and messages
        supervisor_data = []
        for supervisor in supervisors:
            unread_count = Message.objects.filter(receiver_id=current_md_username, sender_id=supervisor.supervisor_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_md_username, sender_id=supervisor.supervisor_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_md_username, receiver_id=supervisor.supervisor_id).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None

            supervisor_data.append({
                'id': supervisor.id,
                'name': supervisor.name,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_md_username if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Processing managers and messages
        manager_data = []
        for manager in managers:
            unread_count = Message.objects.filter(receiver_id=current_md_username, sender_id=manager.manager_id, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_md_username, sender_id=manager.manager_id).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_md_username, receiver_id=manager.manager_id).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None

            manager_data.append({
                'id': manager.id,
                'name': manager.name,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_md_username if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Processing admins and messages
        admin_data = []
        for admin in admins:
            unread_count = Message.objects.filter(receiver_id=current_md_username, sender_id=admin.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_md_username, sender_id=admin.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_md_username, receiver_id=admin.username).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None

            admin_data.append({
                'id': admin.id,
                'name': admin.name,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_md_username if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Processing managing directors and messages
        md_data = []
        for md in mds:
            unread_count = Message.objects.filter(receiver_id=current_md_username, sender_id=md.username, is_read=False).count()
            last_received_message = Message.objects.filter(receiver_id=current_md_username, sender_id=md.username).order_by('-timestamp').first()
            last_sent_message = Message.objects.filter(sender_id=current_md_username, receiver_id=md.username).order_by('-timestamp').first()

            if last_received_message and last_sent_message:
                last_message = max(last_received_message, last_sent_message, key=lambda msg: msg.timestamp)
            elif last_received_message:
                last_message = last_received_message
            elif last_sent_message:
                last_message = last_sent_message
            else:
                last_message = None

            md_data.append({
                'id': md.id,
                'name': md.name,
                'unread_count': unread_count,
                'last_message': last_message.content if last_message else None,
                'last_message_sent_by_current_user': last_message.sender_id == current_md_username if last_message else False,
                'last_message_is_read': last_message.is_read if last_message else False,
                'last_message_delivered': last_message.is_delivered if last_message else False,
            })

        # Processing group messages
        group_data = []
        for group in groups:
            last_custom_group_message = GroupChatMessage.objects.filter(group=group).order_by('-timestamp').first()
            group_data.append({
                'id': group.id,
                'name': group.name,
                'last_message': last_custom_group_message.message if last_custom_group_message else "No messages yet.",
                'last_message_sent_by_current_user': last_custom_group_message.sender_id == current_md_username if last_custom_group_message else False,
                'unread_group_count': MessageStatus.objects.filter(user_id=current_md_username, message__group=group, is_read=False).count(),
            })

        # Combine all data into a response
        data = {
            'employees': employee_data,
            'managers': manager_data,
            'admins': admin_data,
            'supervisors': supervisor_data,
            'mds': md_data,
            'groups': group_data,
            'unread_count': MessageStatus.objects.filter(user_id=current_md_username).count(),
            'last_group_message': GroupChatMessage.objects.filter(group__in=groups).order_by('-timestamp').first().message if groups else None,
        }

        return Response(data)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message, Employee, Manager, Supervisor, Admin, ManagingDirector
from .serializers import MessageSerializer
from collections import defaultdict

class BroadcastChatRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        sender_id = request.session.get('user_id')  # Current logged-in user
        logged_in_role = request.session.get('role')
        
        user_name = None
        if logged_in_role == 'admin':
            user_name = request.session.get('user')
        elif logged_in_role == 'md':
            user_name = request.session.get('user')    
        elif logged_in_role == 'employee':
            user_name = Employee.objects.get(employee_id=sender_id).username
        elif logged_in_role == 'manager':
            user_name = Manager.objects.get(manager_id=sender_id).username
        elif logged_in_role == 'supervisor':
            user_name = Supervisor.objects.get(supervisor_id=sender_id).username

        # Fetch all broadcast messages
        messages = Message.objects.filter(chat_type='broadcast_chat').order_by('timestamp')

        # Create a unique set of messages based on content
        unique_messages = []
        seen_messages = set()

        for message in messages:
            if message.content not in seen_messages:
                unique_messages.append(message)
                seen_messages.add(message.content)

        # Serialize the messages
        serialized_messages = MessageSerializer(unique_messages, many=True)

        # Return the response
        return Response({
            'messages': serialized_messages.data,
            'user_name': user_name,
            'user_id': sender_id  # Pass the user_id to the template for comparison
        })

# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .models import Message, Employee, Manager, Supervisor, Admin, ManagingDirector
from .serializers import MessageSerializer

class SendBroadcastMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message_content = request.data.get('message')

        if not message_content:
            return Response({"detail": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine the sender_id and sender_type based on the logged-in user's role
        sender_id = request.session.get('user_id')  # Get the sender ID from the session
        sender_type = None

        if request.session.get('role') == 'admin':
            sender_id = request.session.get('user')  # Get the admin's username
            sender_type = 'admin'
        elif request.session.get('role') == 'md':
            sender_id = request.session.get('user')  # Get the md's username
            sender_type = 'md'    
        elif Employee.objects.filter(employee_id=sender_id).exists():
            sender_type = 'employee'
        elif Supervisor.objects.filter(supervisor_id=sender_id).exists():
            sender_type = 'supervisor'
        elif Manager.objects.filter(manager_id=sender_id).exists():
            sender_type = 'manager'
        else:
            return Response({"detail": "Invalid sender role."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch all users (employees, managers, and admins), excluding the current sender
        employees = Employee.objects.exclude(employee_id=sender_id)
        supervisors = Supervisor.objects.exclude(supervisor_id=sender_id)
        managers = Manager.objects.exclude(manager_id=sender_id)
        admins = Admin.objects.exclude(username=sender_id)
        mds = ManagingDirector.objects.exclude(username=sender_id)

        # Send the message to each user
        for employee in employees:
            Message.objects.create(
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=employee.employee_id,
                content=message_content,
                chat_type='broadcast_chat'
            )

        for supervisor in supervisors:
            Message.objects.create(
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=supervisor.supervisor_id,
                content=message_content,
                chat_type='broadcast_chat'
            )

        for manager in managers:
            Message.objects.create(
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=manager.manager_id,
                content=message_content,
                chat_type='broadcast_chat'
            )

        for admin in admins:
            Message.objects.create(
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=admin.username,
                content=message_content,
                chat_type='broadcast_chat'
            )
        
        for md in mds:
            Message.objects.create(
                sender_id=sender_id,
                sender_type=sender_type,
                receiver_id=md.username,
                content=message_content,
                chat_type='broadcast_chat'
            )    

        return Response({"detail": "Message sent to all users in the broadcast chat!"}, status=status.HTTP_201_CREATED)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Message, Admin, ManagingDirector, Employee, Supervisor, Manager, UnreadMessage
from .serializers import MessageSerializer
from collections import defaultdict

class GroupChatRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logged_in_user_id = request.session.get('user_id')  # Get user_id from session
        logged_in_role = request.session.get('role')  # Get role from session (admin, employee, manager)

        # Fetch all messages in the group chat
        messages = Message.objects.filter(chat_type='group_chat').order_by('timestamp')

        # Attach the sender's username to each message
        for message in messages:
            if message.sender_type == 'admin':
                sender = Admin.objects.get(username=message.sender_id)
                message.sender_username = sender.username
            elif message.sender_type == 'md':
                sender = ManagingDirector.objects.get(username=message.sender_id)
                message.sender_username = sender.username
            elif message.sender_type == 'employee':
                sender = Employee.objects.get(employee_id=message.sender_id)
                message.sender_username = sender.username
            elif message.sender_type == 'supervisor':
                sender = Supervisor.objects.get(supervisor_id=message.sender_id)
                message.sender_username = sender.username
            elif message.sender_type == 'manager':
                sender = Manager.objects.get(manager_id=message.sender_id)
                message.sender_username = sender.username

        # Mark messages as read for the logged-in user
        if logged_in_role in ['admin', 'md']:
            logged_in_username = request.session.get('user')  # Admin or MD's username
        else:
            logged_in_username = logged_in_user_id  # For employee, manager, or supervisor

        UnreadMessage.objects.filter(user_id=logged_in_username).delete()

        # Serialize the messages
        serialized_messages = MessageSerializer(messages, many=True)

        return Response({'messages': serialized_messages.data})


# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .models import Message, Employee, Manager, Supervisor, Admin, ManagingDirector, UnreadMessage
from .serializers import MessageSerializer

class SendGroupMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message_content = request.data.get('message')

        if not message_content:
            return Response({"detail": "Message content is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Determine the sender_id and sender_type based on the logged-in user's role
        sender_id = request.session.get('user_id')  # Get the sender ID from the session
        sender_type = None

        if request.session.get('role') == 'admin':
            sender_id = request.session.get('user')  # Get the admin's username
            sender_type = 'admin'  # Admin user type
        elif request.session.get('role') == 'md':
            sender_id = request.session.get('user')  # Get the md's username
            sender_type = 'md'  # MD user type
        elif Employee.objects.filter(employee_id=sender_id).exists():
            sender_type = 'employee'
        elif Manager.objects.filter(manager_id=sender_id).exists():
            sender_type = 'manager'
        elif Supervisor.objects.filter(supervisor_id=sender_id).exists():
            sender_type = 'supervisor'
        else:
            return Response({"detail": "Invalid sender role."}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the new group message
        new_message = Message.objects.create(
            sender_id=sender_id,
            sender_type=sender_type,
            receiver_id='all',  # Use a common identifier for group chat
            receiver_type='all',
            content=message_content,
            chat_type='group_chat'  # Set the chat_type to 'group_chat'
        )

        # Add entries to UnreadMessage for all users except the sender
        all_users = list(Employee.objects.values_list('employee_id', flat=True)) + \
                    list(Manager.objects.values_list('manager_id', flat=True)) + \
                    list(Supervisor.objects.values_list('supervisor_id', flat=True)) + \
                    [admin.username for admin in Admin.objects.all() if admin.username != sender_id] + \
                    [md.username for md in ManagingDirector.objects.all() if md.username != sender_id]

        for user in all_users:
            UnreadMessage.objects.create(message=new_message, user_id=user)

        return Response({"detail": "Message sent to the group chat!"}, status=status.HTTP_201_CREATED)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib import messages
from .models import Group, Admin, ManagingDirector, Employee, Manager, Supervisor
from .serializers import GroupSerializer

class CreateGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get the current logged-in user (the creator of the group)
        user_id = request.session.get('user_id')
        user = request.session.get('user')
        user_role = request.session.get('role')

        group_name = request.data.get('group_name')
        member_ids = request.data.get('group_members', [])

        if not group_name or not member_ids:
            return Response({"detail": "Group name and members are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the group
        group = Group.objects.create(name=group_name)

        # Automatically add the creator to the group based on their role
        if user_role == 'admin':
            admin = Admin.objects.get(username=user)
            group.admins.add(admin)
        elif user_role == 'md':
            md = ManagingDirector.objects.get(username=user)
            group.mds.add(md)
        elif user_role == 'manager':
            manager = Manager.objects.get(manager_id=user_id)
            group.managers.add(manager)
        elif user_role == 'supervisor':
            supervisor = Supervisor.objects.get(supervisor_id=user_id)
            group.supervisors.add(supervisor)
        elif user_role == 'employee':
            employee = Employee.objects.get(employee_id=user_id)
            group.employees.add(employee)

        # Add selected members (from Employees, Managers, Admins)
        for member_id in member_ids:
            if Employee.objects.filter(employee_id=member_id).exists():
                employee = Employee.objects.get(employee_id=member_id)
                group.employees.add(employee)
            elif Manager.objects.filter(manager_id=member_id).exists():
                manager = Manager.objects.get(manager_id=member_id)
                group.managers.add(manager)
            elif Supervisor.objects.filter(supervisor_id=member_id).exists():
                supervisor = Supervisor.objects.get(supervisor_id=member_id)
                group.supervisors.add(supervisor)
            elif Admin.objects.filter(username=member_id).exists():
                admin = Admin.objects.get(username=member_id)
                group.admins.add(admin)
            elif ManagingDirector.objects.filter(username=member_id).exists():
                md = ManagingDirector.objects.get(username=member_id)
                group.mds.add(md)

        group.save()

        return Response({"detail": "Group created successfully!"}, status=status.HTTP_201_CREATED)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Group, GroupChatMessage, MessageStatus
from .serializers import GroupSerializer, GroupChatMessageSerializer, MessageStatusSerializer


class CustomGroupChatRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, group_id):
        # Get logged-in user information from the session
        logged_in_user_id = request.session.get('user_id')
        logged_in_username = request.session.get('user')
        user_role = request.session.get('role')

        # Determine the user's timezone
        user_timezone = request.GET.get('timezone')
        if user_timezone:
            try:
                user_tz = pytz.timezone(user_timezone)
            except pytz.UnknownTimeZoneError:
                user_tz = pytz.UTC  # Fallback to UTC if timezone is unknown
        else:
            user_tz = pytz.UTC  # Fallback to UTC if no timezone is provided

        # Get the group object
        group = get_object_or_404(Group, id=group_id)

        # Retrieve group messages
        group_messages = GroupChatMessage.objects.filter(group=group).order_by('timestamp')
        
        # Get message details with read status
        messages_with_details = []
        for message in group_messages:
            read_statuses = MessageStatus.objects.filter(message=message, is_read=True)
            users_who_read = [status.user_id for status in read_statuses]

            messages_with_details.append({
                'content': message.message,
                'timestamp': message.timestamp.astimezone(user_tz).isoformat(),
                'sender_type': message.sender_type,
                'sender_username': message.sender_id,  # This can be expanded with additional logic
                'users_who_read': users_who_read,
            })

        # Group members
        group_members = {
            'employees': group.employees.all(),
            'supervisors': group.supervisors.all(),
            'managers': group.managers.all(),
            'admins': group.admins.all(),
            'mds': group.mds.all(),
        }

        # Serialize the response
        group_serializer = GroupSerializer(group)
        return Response({
            'group': group_serializer.data,
            'group_members': group_members,
            'group_messages': messages_with_details,
        }, status=status.HTTP_200_OK)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Group, GroupChatMessage, MessageStatus
from .serializers import GroupChatMessageSerializer, MessageStatusSerializer


class SendGroupChatMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, group_id):
        message_content = request.data.get('message')
        user_timezone = request.data.get('timezone')

        # Get current time in UTC
        current_time_utc = timezone.now()

        # Convert to user's local timezone if provided
        if user_timezone:
            try:
                user_tz = pytz.timezone(user_timezone)
                current_time_local = current_time_utc.astimezone(user_tz)
            except pytz.UnknownTimeZoneError:
                current_time_local = current_time_utc
        else:
            current_time_local = current_time_utc

        # Get sender ID and type based on the logged-in user
        sender_id = request.session.get('user_id')
        sender_type = None

        if request.session.get('role') == 'admin':
            sender_type = 'admin'
        elif request.session.get('role') == 'md':
            sender_type = 'md'
        elif request.session.get('role') == 'employee':
            sender_type = 'employee'
        elif request.session.get('role') == 'supervisor':
            sender_type = 'supervisor'
        elif request.session.get('role') == 'manager':
            sender_type = 'manager'
        else:
            return Response({"detail": "Invalid user role"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the group
        group = get_object_or_404(Group, id=group_id)

        # Create and save the group message
        group_message = GroupChatMessage.objects.create(
            group=group,
            sender_id=sender_id,
            sender_type=sender_type,
            message=message_content,
            timestamp=current_time_utc,
            is_read=False
        )

        # Create MessageStatus entries for each member of the group
        for member in group.employees.all():
            MessageStatus.objects.create(
                message=group_message,
                user_id=member.employee_id,
                is_read=False,
                is_delivered=True,
            )

        for member in group.managers.all():
            MessageStatus.objects.create(
                message=group_message,
                user_id=member.manager_id,
                is_read=False,
                is_delivered=True,
            )

        for member in group.supervisors.all():
            MessageStatus.objects.create(
                message=group_message,
                user_id=member.supervisor_id,
                is_read=False,
                is_delivered=True,
            )

        for member in group.admins.all():
            MessageStatus.objects.create(
                message=group_message,
                user_id=member.username,
                is_read=False,
                is_delivered=True,
            )

        for member in group.mds.all():
            MessageStatus.objects.create(
                message=group_message,
                user_id=member.username,
                is_read=False,
                is_delivered=True,
            )

        return Response({"detail": "Message sent successfully!"}, status=status.HTTP_201_CREATED)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Group, Employee, Manager, Supervisor, Admin, ManagingDirector
from .serializers import GroupSerializer  # You can create a serializer for Group if needed

class LeaveGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensuring only authenticated users can access this

    def post(self, request, group_id):
        user_id = request.user.id  # Assuming the user is authenticated and `id` is the user's ID
        role = request.user.role  # Assuming role is stored as a field in the user model

        group = get_object_or_404(Group, id=group_id)

        if role == 'employee':
            employee = get_object_or_404(Employee, employee_id=user_id)
            if employee in group.employees.all():
                group.employees.remove(employee)
                return Response({'message': 'You have successfully left the group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'manager':
            manager = get_object_or_404(Manager, manager_id=user_id)
            if manager in group.managers.all():
                group.managers.remove(manager)
                return Response({'message': 'You have successfully left the group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'supervisor':
            supervisor = get_object_or_404(Supervisor, supervisor_id=user_id)
            if supervisor in group.supervisors.all():
                group.supervisors.remove(supervisor)
                return Response({'message': 'You have successfully left the group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'admin':
            admin = get_object_or_404(Admin, username=request.user.username)
            if admin in group.admins.all():
                group.admins.remove(admin)
                return Response({'message': 'You have successfully left the group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        elif role == 'md':
            md = get_object_or_404(ManagingDirector, username=request.user.username)
            if md in group.mds.all():
                group.mds.remove(md)
                return Response({'message': 'You have successfully left the group.'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'You are not a member of this group.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Invalid role or session expired.'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Group, Employee, Manager, Supervisor, Admin, ManagingDirector
from .serializers import GroupSerializer  # You can create a serializer for Group if needed

class AddMembersToGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensuring only authenticated users can access this

    def post(self, request, group_id):
        group = get_object_or_404(Group, id=group_id)
        member_ids = request.data.get('members', [])

        for member_id in member_ids:
            if Employee.objects.filter(employee_id=member_id).exists():
                employee = Employee.objects.get(employee_id=member_id)
                group.employees.add(employee)
            elif Manager.objects.filter(manager_id=member_id).exists():
                manager = Manager.objects.get(manager_id=member_id)
                group.managers.add(manager)
            elif Supervisor.objects.filter(supervisor_id=member_id).exists():
                supervisor = Supervisor.objects.get(supervisor_id=member_id)
                group.supervisors.add(supervisor)
            elif Admin.objects.filter(username=member_id).exists():
                admin = Admin.objects.get(username=member_id)
                group.admins.add(admin)
            elif ManagingDirector.objects.filter(username=member_id).exists():
                md = ManagingDirector.objects.get(username=member_id)
                group.mds.add(md)
            else:
                return Response({'message': f'Member with ID {member_id} does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        group.save()
        return Response({'message': 'Members added to the group successfully!'}, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Message, Employee, Manager, Supervisor, Admin, ManagingDirector
from django.shortcuts import get_object_or_404
from django.db.models import Q
import pytz
from django.utils import timezone

class ChatRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, user_id):
        user_timezone = request.GET.get('timezone', 'UTC')
        
        try:
            user_tz = pytz.timezone(user_timezone)
        except pytz.UnknownTimeZoneError:
            user_tz = pytz.UTC  # Default to UTC if the timezone is invalid

        logged_in_user_id = request.user.id  # Get the logged-in user's ID

        # Fetch user details based on user_id
        user_type = None
        user_name = None

        employee = Employee.objects.filter(employee_id=user_id).first()
        manager = Manager.objects.filter(manager_id=user_id).first()
        admin = Admin.objects.filter(username=user_id).first()
        md = ManagingDirector.objects.filter(username=user_id).first()
        supervisor = Supervisor.objects.filter(username=user_id).first()

        if employee:
            user_type = 'employee'
            user_name = employee.username
        elif manager:
            user_type = 'manager'
            user_name = manager.username
        elif admin:
            user_type = 'admin'
            user_name = admin.username
        elif md:
            user_type = 'md'
            user_name = md.username
        elif supervisor:
            user_type = 'supervisor'
            user_name = supervisor.username
        else:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get the messages between the logged-in user and the selected user
        messages = Message.objects.filter(
            (Q(sender_id=logged_in_user_id) & Q(receiver_id=user_id)) |
            (Q(sender_id=user_id) & Q(receiver_id=logged_in_user_id))
        ).order_by('timestamp')

        # Update the 'is_read' field for messages
        Message.objects.filter(receiver_id=logged_in_user_id, sender_id=user_id, is_read=False).update(is_read=True)

        messages_with_usernames = []
        for message in messages:
            sender = self.get_user_by_type(message.sender_type, message.sender_id)
            receiver = self.get_user_by_type(message.receiver_type, message.receiver_id)

            messages_with_usernames.append({
                'content': message.content,
                'timestamp': message.timestamp.astimezone(user_tz).isoformat(),
                'sender_type': message.sender_type,
                'sender_username': sender.username if sender else 'Unknown',
                'receiver_username': receiver.username if receiver else 'Unknown',
                'is_delivered': message.is_delivered,
                'is_read': message.is_read
            })

        return Response({
            'user_id': user_id,
            'user_name': user_name,
            'user_type': user_type,
            'messages': messages_with_usernames
        })

    def get_user_by_type(self, user_type, user_id):
        """Helper function to get the user object by type"""
        if user_type == 'employee':
            return get_object_or_404(Employee, employee_id=user_id)
        elif user_type == 'manager':
            return get_object_or_404(Manager, manager_id=user_id)
        elif user_type == 'supervisor':
            return get_object_or_404(Supervisor, supervisor_id=user_id)
        elif user_type == 'admin':
            return get_object_or_404(Admin, username=user_id)
        elif user_type == 'md':
            return get_object_or_404(ManagingDirector, username=user_id)
        return None


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Message, Employee, Manager, Supervisor, Admin, ManagingDirector
from django.utils import timezone

class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request, user_id):
        message_content = request.data.get('message')
        user_timezone = request.data.get('timezone', 'UTC')

        # Get the current time in UTC
        current_time_utc = timezone.now()

        # Convert to the user's local timezone if provided
        try:
            user_tz = pytz.timezone(user_timezone)
            current_time_local = current_time_utc.astimezone(user_tz)
        except pytz.UnknownTimeZoneError:
            current_time_local = current_time_utc  # Default to UTC if timezone is invalid

        # Determine sender_id and sender_type based on logged-in user's role
        sender_id = request.user.id
        sender_type = self.get_user_role(sender_id)

        if not sender_type:
            return Response({'error': 'Invalid sender type'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine receiver type based on user_id
        receiver_type = self.get_user_role(user_id)
        if not receiver_type:
            return Response({'error': 'Invalid receiver type'}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save the new message
        Message.objects.create(
            sender_id=sender_id,
            sender_type=sender_type,
            receiver_id=user_id,
            receiver_type=receiver_type,
            content=message_content,
            timestamp=current_time_utc,
            is_read=False
        )

        return Response({'message': 'Message sent successfully!'}, status=status.HTTP_201_CREATED)

    def get_user_role(self, user_id):
        """Helper function to get user role"""
        if Admin.objects.filter(username=user_id).exists():
            return 'admin'
        elif ManagingDirector.objects.filter(username=user_id).exists():
            return 'md'
        elif Supervisor.objects.filter(supervisor_id=user_id).exists():
            return 'supervisor'
        elif Employee.objects.filter(employee_id=user_id).exists():
            return 'employee'
        elif Manager.objects.filter(manager_id=user_id).exists():
            return 'manager'
        return None

              