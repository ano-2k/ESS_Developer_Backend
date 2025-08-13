from django.urls import path
from .views import *

urlpatterns = [
     
     path('api/add-party/', AddPartyAPIView.as_view(), name='add-party'),
     path('party-list/', GetAllPartiesAPIView.as_view(), name='get-all-parties'),  # Get all parties
     path('addresses/<int:party_id>/', AddressListAPIView.as_view(), name='address-list'),
     path('customers/', GetAllCustomersAPIView.as_view(), name='get-all-customers'),
     path('suppliers/', GetAllSuppliersAPIView.as_view(), name='get-all-suppliers'),
############################
     path('party/update/<int:party_id>/', UpdatePartyAPIView.as_view(), name='update-party'),  # Update Party (PUT)
     path('party/delete/<int:party_id>/', DeletePartyAPIView.as_view(), name='delete-party'),  # Delete Party (DELETE)
     path("party/<int:party_id>/", GetPartyAPIView.as_view(), name="get-party"), 

     path('add-billing-address/', BillingAddressView.as_view(), name='billing-address'),
     path("billing-address/<int:party_id>/", GetBillingAddressAPIView.as_view(), name="get-billing-address"),  # GET (Retrieve by ID)
     path("billing-address/update/<int:party_id>/", UpdateBillingAddressAPIView.as_view(), name="update-billing-address"),  # PUT (Update)
     path("billing-address/delete/<int:party_id>/", DeleteBillingAddressAPIView.as_view(), name="delete-billing-address"),  # DELETE (Delete)
     
     path('add-shipping-address/', ShippingAddressView.as_view(), name='shipping-address'),
     path("shipping-address/<int:party_id>/", GetShippingAddressAPIView.as_view(), name="get-shipping-address"),  # GET (Retrieve by Party ID)
     path("shipping-address/update/<int:party_id>/", UpdateShippingAddressAPIView.as_view(), name="update-shipping-address"),  # PUT (Update)
     path("shipping-address/delete/<int:party_id>/", DeleteShippingAddressAPIView.as_view(), name="delete-shipping-address"),  # DELETE (Delete)
   
     path('total-amount/', TotalAmountView.as_view(), name='total-amount'),
     path('party/general-details/', GeneralDetailsAPIView.as_view(), name='general-details'),
     path('party/business-details/', BusinessDetailsAPIView.as_view(), name='business-details'),
     path('party/credit-details/', CreditDetailsAPIView.as_view(), name='credit-details'),
     path('party/details/', PartyDetailsView.as_view(), name='party-details'),
     path('api/add-party-address/', CombinedPartyAddressView.as_view(), name='add-party-address'),
     path("party-address/update/<int:party_id>/", UpdateCombinedPartyAddressView.as_view(), name="update-combined-party-address"),
     path('bank-details/create/<int:party_id>/', CreateBankDetailsAPIView.as_view(), name='create-bank-details'),
     path('bank-details/<int:party_id>/', GetBankDetailsAPIView.as_view(), name='get-bank-details'),
     path('salesperson/<int:id>/parties/', SalesPersonWithPartiesView.as_view(), name='salesperson_with_parties'),
     path('party-categories/', PartyCategoryListAPIView.as_view(), name='party-category-list'),


     path('employee-parties/<str:employee_id>/', GetEmployeePartiesAPIView.as_view(), name='employee-parties'),
     
]