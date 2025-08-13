"""
URL configuration for ess project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# add two lines for media
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # path('', include('authentication.urls')),
    # path('', include('attendance.urls')),
    # path('', include('leaves.urls')),
    # path('', include('chat.urls')),
    # path('', include('kpi.urls')),
    # path('', include('payroll.urls')),
    # path('', include('documents.urls')),  
    # path('', include('projectmanagement.urls')),
    # path('pincode/',include('Pincode.urls')),
    # path('item/',include('Create_New_Item.urls')),
    # path('quotation/',include('Quotation_Estimate.urls')),
    # path('saleinv/',include('Sales_Invoice.urls')),
    # path('payment/',include('Payment_In.urls')),
    # path('proformainv/',include('Proforma_Invoice.urls')),
    # path('deliverych/',include('Delivery_Challan.urls')),
    # path('credit/',include('Credit_Note.urls')),
    # path('salesref/',include("Sales_Person.urls")),
    # path('armanagement/', include('armanagement.urls')), 

     path('', include('authentication.urls')),
    path('', include('attendance.urls')),
    path('', include('leaves.urls')),
    path('', include('chat.urls')),
    path('', include('kpi.urls')),
    path('', include('payroll.urls')),
    path('', include('documents.urls')),  
    path('', include('projectmanagement.urls')),
    path('pincode/',include('Pincode.urls')),
    path('item/',include('Create_New_Item.urls')),
    path('quotation/',include('Quotation_Estimate.urls')),
    path('saleinv/',include('Sales_Invoice.urls')),
    path('payment/',include('Payment_In.urls')),
    path('proformainv/',include('Proforma_Invoice.urls')),
    path('deliverych/',include('Delivery_Challan.urls')),
    path('credit/',include('Credit_Note.urls')),
    path('salesref/',include("Sales_Person.urls")),
    path('', include('armanagement.urls')),
    path('', include('Sales_Order.urls')),
    path('', include('purchase_order.urls')),
    path('', include('helpdesk.urls')),

]

# add two lines for media
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
