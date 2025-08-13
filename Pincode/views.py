from django.shortcuts import redirect, render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from .models import *
from .serializers import *
from django.db import transaction 


# Render Add Party Form
def add_party_form(request):
    if request.method == 'POST':
        data = request.POST
        # Create Party from form data
        party_serializer = AddPartySerializer(data=data)
        if party_serializer.is_valid():
            party = party_serializer.save()
        return redirect('add-party', party_id=party.id)
    return render(request, 'add_party_form.html', {'party': party})

# ✅ Create a Party
class AddPartyAPIView(APIView):
    def post(self, request):
        serializer = AddPartySerializer(data=request.data)
        if serializer.is_valid():
            party = serializer.save()
            return Response({"party_id": party.id, "message": "Party added successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetAllPartiesAPIView(APIView):
    """API to retrieve all parties"""
    def get(self, request):
        parties = AddParty.objects.all()  # Fetch all parties
        if not parties.exists():
            return Response({"message": "No parties found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the data
        serializer = AddPartySerializer(parties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# API to get all customers
class GetAllCustomersAPIView(APIView):
    def get(self, request):
        customers = AddParty.objects.filter(party_type='customer')
        if not customers.exists():
            return Response({"message": "No customers found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddPartySerializer(customers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# API to get all suppliers
class GetAllSuppliersAPIView(APIView):
    def get(self, request):
        suppliers = AddParty.objects.filter(party_type='supplier')
        if not suppliers.exists():
            return Response({"message": "No suppliers found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddPartySerializer(suppliers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
class GetPartyAPIView(APIView):
    """API to retrieve a Party by ID"""
    def get(self, request, party_id):
        party = get_object_or_404(AddParty, id=party_id)
        serializer = AddPartySerializer(party)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdatePartyAPIView(APIView):
    """API to update an existing party"""
    def put(self, request, party_id):
        party = get_object_or_404(AddParty, id=party_id)
        serializer = AddPartySerializer(party, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Party updated successfully!", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeletePartyAPIView(APIView):
    """API to delete an existing party by ID"""
    def delete(self, request, party_id):
        party = get_object_or_404(AddParty, id=party_id)
        party.delete()
        return Response({"message": "Party deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)

# Billing Address View - Create or Update Billing Address
class BillingAddressView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            billing_data = request.data
            party_id = billing_data.get("party")  # Fetch from JSON body
            
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = BillingAddressSerializer(data=billing_data)

            if serializer.is_valid():
                billing_address = serializer.save()
                return Response({"message": "Billing Address created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class GetBillingAddressAPIView(APIView):
    """API to retrieve a Billing Address by party ID"""
    def get(self, request, party_id):
        try:
            # Try to get the BillingAddress for the given party_id
            billing_address = BillingAddress.objects.get(party_id=party_id)
            serializer = BillingAddressSerializer(billing_address)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except BillingAddress.DoesNotExist:
            # Return a custom message if the BillingAddress doesn't exist for the given party_id
            return Response({"message": "Party does not have a billing address."}, status=status.HTTP_404_NOT_FOUND)


class UpdateBillingAddressAPIView(APIView):
    """API to update an existing Billing Address"""
    def put(self, request, party_id):
        billing_address = get_object_or_404(BillingAddress, party_id=party_id)
        serializer = BillingAddressSerializer(billing_address, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Billing Address updated successfully!", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteBillingAddressAPIView(APIView):
    """API to delete a Billing Address by ID"""
    def delete(self, request, party_id):
        billing_address = get_object_or_404(BillingAddress, party_id=party_id)
        billing_address.delete()
        return Response({"message": "Billing Address deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)



# Shipping Address View - Create or Update Shipping Address
class ShippingAddressView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            shipping_data = request.data
            party_id = shipping_data.get("party")  # Get party_id from JSON body
            
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # If the shipping address is same as billing, auto-copy billing info
            if shipping_data.get('is_same_as_billing_address', False):
                try:
                    billing_address = BillingAddress.objects.get(party_id=party_id)
                    shipping_data['street'] = billing_address.street
                    shipping_data['state'] = billing_address.state
                    shipping_data['pincode'] = billing_address.pincode
                    shipping_data['city'] = billing_address.city
                except BillingAddress.DoesNotExist:
                    return Response({"error": "Billing address not found for the given party"}, status=status.HTTP_404_NOT_FOUND)

            # If pincode is provided, fetch city using the pincode
            if shipping_data.get('pincode'):
                shipping_data['city'] = fetch_city_from_pincode(shipping_data.get('pincode'))

            # Serialize and save shipping address
            serializer = ShippingAddressSerializer(data=shipping_data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Shipping Address created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetShippingAddressAPIView(APIView):
    """API to retrieve a Shipping Address by Party ID"""
    def get(self, request, party_id):
        try:
            # Try to get the ShippingAddress for the given party_id
            shipping_address = ShippingAddress.objects.get(party_id=party_id)
            serializer = ShippingAddressSerializer(shipping_address)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ShippingAddress.DoesNotExist:
            # Return a custom message if the ShippingAddress doesn't exist for the given party_id
            return Response({"message": "Party does not have a shipping address."}, status=status.HTTP_404_NOT_FOUND)


class UpdateShippingAddressAPIView(APIView):
    """API to update an existing Shipping Address"""
    def put(self, request, party_id):
        shipping_address = get_object_or_404(ShippingAddress, party_id=party_id)
        serializer = ShippingAddressSerializer(shipping_address, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Shipping Address updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteShippingAddressAPIView(APIView):
    """API to delete a Shipping Address by Party ID"""
    def delete(self, request, party_id):
        shipping_address = get_object_or_404(ShippingAddress, party_id=party_id)
        shipping_address.delete()
        return Response({"message": "Shipping Address deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        
class TotalAmountView(APIView):
    def get(self, request):
        # Get total 'to_collect' amount
        to_collect_total = AddParty.objects.filter(opening_balance="to_collect").aggregate(Sum('opening_balance_amount'))['opening_balance_amount__sum'] or 0.00
        
        # Get total 'to_pay' amount
        to_pay_total = AddParty.objects.filter(opening_balance="to_pay").aggregate(Sum('opening_balance_amount'))['opening_balance_amount__sum'] or 0.00
        
        # Return the response with both totals
        return Response({
            'total_to_collect': to_collect_total,
            'total_to_pay': to_pay_total
        }, status=status.HTTP_200_OK)
        
        
class GeneralDetailsAPIView(APIView):
    def post(self, request):
        try:
            party_id = request.data.get("party")  # Get party_id from JSON body
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            party = AddParty.objects.get(id=party_id)
            serializer = GeneralDetailsSerializer(party)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AddParty.DoesNotExist:
            return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)


class BusinessDetailsAPIView(APIView):
    def post(self, request):
        try:
            party_id = request.data.get("party")
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            party = AddParty.objects.get(id=party_id)
            serializer = BusinessDetailsSerializer(party)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AddParty.DoesNotExist:
            return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)


class CreditDetailsAPIView(APIView):
    def post(self, request):
        try:
            party_id = request.data.get("party")
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            party = AddParty.objects.get(id=party_id)
            serializer = CreditDetailsSerializer(party)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AddParty.DoesNotExist:
            return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)


class PartyDetailsView(APIView):
    def post(self, request):
        try:
            party_id = request.data.get("party")
            if not party_id:
                return Response({"error": "party ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            party = AddParty.objects.get(id=party_id)
            serializer = PartyDetailsSerializer(party)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AddParty.DoesNotExist:
            return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)

class PartyListAPIView(APIView):
    def get(self, request):
        parties = AddParty.objects.filter(opening_balance__in=['to_pay', 'to_collect']) 
        serializer = PartyListSerializer(parties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AddressListAPIView(APIView):
    def get(self, request, party_id, *args, **kwargs):
        try:
            # Retrieve the party by party_id
            party = AddParty.objects.get(id=party_id)
            
            # Initialize address data
            address_data = {}

            # Check if billing address exists
            if hasattr(party, 'billing_address'):
                billing_address = party.billing_address
                billing_address_serializer = BillingAddressSerializer(billing_address)
                address_data['billing_address'] = billing_address_serializer.data
            else:
                address_data['billing_address'] = None

            # Check if shipping address exists
            if hasattr(party, 'shipping_address'):
                shipping_address = party.shipping_address
                shipping_address_serializer = ShippingAddressSerializer(shipping_address)
                address_data['shipping_address'] = shipping_address_serializer.data
            else:
                address_data['shipping_address'] = None

            # Check if both addresses are missing
            if not address_data['billing_address'] and not address_data['shipping_address']:
                return Response({"message": "Party does not have any address."}, status=status.HTTP_200_OK)
            
            return Response(address_data, status=status.HTTP_200_OK)

        except AddParty.DoesNotExist:
            return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)
  

# class CombinedPartyAddressView(APIView):
#     def post(self, request, *args, **kwargs):
#         try:
#             with transaction.atomic():
#                 party_data = request.data.get('party')
#                 if not party_data:
#                     return Response({"error": "Party data is required"}, status=status.HTTP_400_BAD_REQUEST)

#                 # Handling salesperson as ID instead of the full serializer
#                 salesperson_id = party_data.get('sales_person')
#                 salesperson = None
#                 if salesperson_id:
#                     try:
#                         salesperson = SalesPerson.objects.get(id=salesperson_id)
#                     except SalesPerson.DoesNotExist:
#                         return Response({"error": "Salesperson not found"}, status=status.HTTP_400_BAD_REQUEST)
#                 party_data['sales_person'] = salesperson.id if salesperson else None
                
#                 # Party creation
#                 party_serializer = AddPartySerializer(data=party_data)
#                 if not party_serializer.is_valid():
#                     return Response(party_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 party = party_serializer.save()

#                 # Handle billing address creation
#                 billing_data = request.data.get('billing_address')
#                 if not billing_data:
#                     return Response({"error": "Billing address data is required"}, status=status.HTTP_400_BAD_REQUEST)
#                 billing_data['party'] = party.id
#                 billing_serializer = BillingAddressSerializer(data=billing_data)
#                 if not billing_serializer.is_valid():
#                     return Response(billing_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 billing_address = billing_serializer.save()

#                 # Handle shipping address creation
#                 shipping_data = request.data.get('shipping_address')
#                 if not shipping_data:
#                     return Response({"error": "Shipping address data is required"}, status=status.HTTP_400_BAD_REQUEST)
#                 shipping_data['party'] = party.id
#                 shipping_serializer = ShippingAddressSerializer(data=shipping_data)
#                 if not shipping_serializer.is_valid():
#                     return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#                 shipping_address = shipping_serializer.save()

#                 # Return response with salesperson details
#                 return Response({
#                     "message": "Party, Billing Address, and Shipping Address created successfully",
#                     "party_id": party.id,
#                     "billing_address": billing_serializer.data,
#                     "shipping_address": shipping_serializer.data,
#                     "salesperson": SalesPersonSerializer(salesperson).data if salesperson else None
#                 }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CombinedPartyAddressView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                party_data = request.data.get('party')
                if not party_data:
                    return Response({"error": "Party data is required"}, status=status.HTTP_400_BAD_REQUEST)

                # Get logged-in employee ID from request data
                employee_id = request.data.get('employee_id')
                if not employee_id:
                    return Response({"error": "Employee ID is required"}, status=status.HTTP_400_BAD_REQUEST)

                # Find the employee
                try:
                    employee = Employee.objects.get(employee_id=employee_id)
                except Employee.DoesNotExist:
                    return Response({"error": "Employee not found"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if employee is already a salesperson
                salesperson, created = SalesPerson.objects.get_or_create(
                    employee=employee,
                    defaults={
                        'name': employee.employee_name,
                        'email': employee.email,
                        'phone': employee.phone_number or '',
                        'employee_code': employee.employee_id,
                    }
                )

                party_data = party_data.copy()  # Create mutable copy
                party_data['sales_person_id'] = salesperson.id  # Match serializer field name

                # Party creation
                party_serializer = AddPartySerializer(data=party_data)
                if not party_serializer.is_valid():
                    return Response(party_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                party = party_serializer.save()

                # Handle billing address creation
                billing_data = request.data.get('billing_address')
                if not billing_data:
                    return Response({"error": "Billing address data is required"}, status=status.HTTP_400_BAD_REQUEST)
                billing_data['party'] = party.id
                billing_serializer = BillingAddressSerializer(data=billing_data)
                if not billing_serializer.is_valid():
                    return Response(billing_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                billing_address = billing_serializer.save()

                # Handle shipping address creation
                shipping_data = request.data.get('shipping_address')
                if not shipping_data:
                    return Response({"error": "Shipping address data is required"}, status=status.HTTP_400_BAD_REQUEST)
                shipping_data['party'] = party.id
                shipping_serializer = ShippingAddressSerializer(data=shipping_data)
                if not shipping_serializer.is_valid():
                    return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                shipping_address = shipping_serializer.save()

                # Return response with salesperson details
                return Response({
                    "message": "Party, Billing Address, and Shipping Address created successfully",
                    "party_id": party.id,
                    "billing_address": billing_serializer.data,
                    "shipping_address": shipping_serializer.data,
                    "salesperson": SalesPersonSerializer(salesperson).data
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



      
class UpdateCombinedPartyAddressView(APIView):
    def put(self, request, party_id):
        try:
            with transaction.atomic():
                # Fetch the Party instance
                try:
                    party = AddParty.objects.get(pk=party_id)
                except AddParty.DoesNotExist:
                    return Response({"error": "Party not found"}, status=status.HTTP_404_NOT_FOUND)

                # Update Party
                party_data = request.data.get("party")
                if not party_data:
                    return Response({"error": "Party data is required"}, status=status.HTTP_400_BAD_REQUEST)

                party_serializer = AddPartySerializer(party, data=party_data, partial=True)
                if not party_serializer.is_valid():
                    return Response(party_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                party_serializer.save()

                # Update Billing Address
                billing_data = request.data.get("billing_address")
                if billing_data:
                    billing_address, _ = BillingAddress.objects.get_or_create(party=party)
                    billing_data["party"] = party.id
                    billing_serializer = BillingAddressSerializer(billing_address, data=billing_data, partial=True)
                    if not billing_serializer.is_valid():
                        return Response(billing_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    billing_serializer.save()

                # Update Shipping Address
                shipping_data = request.data.get("shipping_address")
                if shipping_data:
                    shipping_address, _ = ShippingAddress.objects.get_or_create(party=party)
                    shipping_data["party"] = party.id

                    if shipping_data.get("is_same_as_billing_address", False):
                        # Use billing address data
                        billing_address = BillingAddress.objects.filter(party=party).first()
                        if billing_address:
                            shipping_data.update({
                                "street": billing_address.street,
                                "state": billing_address.state,
                                "pincode": billing_address.pincode,
                                "city": billing_address.city,
                            })
                    elif shipping_data.get("pincode"):
                        shipping_data["city"] = fetch_city_from_pincode(shipping_data["pincode"])

                    shipping_serializer = ShippingAddressSerializer(shipping_address, data=shipping_data, partial=True)
                    if not shipping_serializer.is_valid():
                        return Response(shipping_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    shipping_serializer.save()

                return Response({
                    "message": "Party, Billing Address, and Shipping Address updated successfully",
                    "party_id": party.id
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CreateBankDetailsAPIView(APIView):
    def post(self, request, party_id):
        try:
            party = AddParty.objects.get(id=party_id)
        except AddParty.DoesNotExist:
            return Response({"error": "Party not found."}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(party, 'bank_details'):
            return Response({"error": "Bank details already exist for this party."}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['party'] = party.id
        serializer = BankDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetBankDetailsAPIView(APIView):
    def get(self, request, party_id):
        try:
            bank_details = BankDetails.objects.get(party__id=party_id)
            serializer = BankDetailsSerializer(bank_details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BankDetails.DoesNotExist:
            return Response({"error": "Bank details not found for this party."}, status=status.HTTP_404_NOT_FOUND)

class SalesPersonWithPartiesView(APIView):
    def get(self, request, id):
        try:
            salesperson = SalesPerson.objects.get(id=id)
        except SalesPerson.DoesNotExist:
            return Response({"detail": "SalesPerson not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all parties associated with the salesperson
        parties = AddParty.objects.filter(sales_person=salesperson)
        party_serializer = AddPartySerializer(parties, many=True)

        # Serialize the salesperson along with the party details
        salesperson_data = SalesPersonSerializer(salesperson).data
        salesperson_data['parties'] = party_serializer.data

        return Response(salesperson_data, status=status.HTTP_200_OK)
    
class PartyCategoryListAPIView(APIView):
    def get(self, request):
        categories = AddParty.objects.values_list('party_category', flat=True).distinct()
        return Response({"party_categories": list(categories)})
    



class GetEmployeePartiesAPIView(APIView):
    """API to retrieve parties created by the specified employee"""
    def get(self, request, employee_id):
        parties = AddParty.objects.filter(sales_person__employee_code=employee_id)
        serializer = AddPartySerializer(parties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
		
