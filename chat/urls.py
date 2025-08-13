# chat/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import AddMembersToGroupAPIView, AdminChatAPIView, BroadcastChatRoomAPIView, ChatRoomAPIView, CreateGroupAPIView, CustomGroupChatRoomAPIView, EmployeeChatView, GroupChatRoomAPIView, LeaveGroupAPIView, MDChatView, ManagerChatAPIView, SendBroadcastMessageAPIView, SendGroupChatMessageAPIView, SendGroupMessageAPIView, SendMessageAPIView, SupervisorChatView

urlpatterns = [
    path('employee-chat/', EmployeeChatView.as_view(), name='employee_chat'),
     path('supervisor-chat/', SupervisorChatView.as_view(), name='supervisor_chat'),
      path('manager-chat/', ManagerChatAPIView.as_view(), name='manager_chat_api'),
      path('api/admin-chat/', AdminChatAPIView.as_view(), name='admin-chat-api'),
      path('md-chat/', MDChatView.as_view(), name='md_chat'),
      path('broadcast_chat/', BroadcastChatRoomAPIView.as_view(), name='broadcast_chat_room'),
    path('send_broadcast/', SendBroadcastMessageAPIView.as_view(), name='send_broadcast_message'),
     path('group_chat/', GroupChatRoomAPIView.as_view(), name='group_chat_room'),
    path('send_group_message/', SendGroupMessageAPIView.as_view(), name='send_group_message'),
     path('create_group/', CreateGroupAPIView.as_view(), name='create_group'),
     path('group_chat/<int:group_id>/', CustomGroupChatRoomAPIView.as_view(), name='custom_group_chat_room'),
    path('send_message/<int:group_id>/', SendGroupChatMessageAPIView.as_view(), name='send_groupchat_message'),
     path('groups/<int:group_id>/leave/', LeaveGroupAPIView.as_view(), name='leave_group'),
    path('groups/<int:group_id>/add_members/', AddMembersToGroupAPIView.as_view(), name='add_members_to_group'),
    path('chat/<int:user_id>/', ChatRoomAPIView.as_view(), name='chat_room'),
    path('chat/<int:user_id>/send/', SendMessageAPIView.as_view(), name='send_message'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
