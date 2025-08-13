from django.urls import path
from .views import *

urlpatterns = [
    path('salespersons/', SalesPersonListView.as_view(), name='salesperson-list'),
    path('salespersons/create/', SalesPersonCreateView.as_view(), name='salesperson-create'),
    path('salespersons/<int:pk>/', SalesPersonDetailView.as_view(), name='salesperson-detail'),
    path("salesperson/<int:id>/invoices/", SalesPersonInvoicesView.as_view(), name="salesperson-invoices"),
   
    
]
