from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (ManagerDocumentListAPIView, 
ManagerUpdateDocumentAPIView, 
ManagerUploadDocumentAPIView,
SupervisorDocumentListAPIView, 
SupervisorUpdateDocumentAPIView,
SupervisorUploadDocumentAPIView, 
UploadDocumentAPIView,
DocumentListAPIView,
UpdateDocumentAPIView)

urlpatterns = [
    path('documents/upload/', UploadDocumentAPIView.as_view(), name='upload_document'),
    path('documents/', DocumentListAPIView.as_view(), name='document_list'),
    path('documents/<int:document_id>/update/', UpdateDocumentAPIView.as_view(), name='update_document'),
    path('manager/documents/upload/', ManagerUploadDocumentAPIView.as_view(), name='manager_upload_document'),
    path('manager/documents/', ManagerDocumentListAPIView.as_view(), name='manager_document_list'),
    path('manager/documents/<int:user_id>/update/', ManagerUpdateDocumentAPIView.as_view(), name='manager_update_document'),
    path('supervisor/documents/upload/', SupervisorUploadDocumentAPIView.as_view(), name='supervisor_upload_document'),
    path('supervisor/documents/', SupervisorDocumentListAPIView.as_view(), name='supervisor_document_list'),
    path('supervisor/documents/<int:user_id>/update/', SupervisorUpdateDocumentAPIView.as_view(), name='supervisor_update_document'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
