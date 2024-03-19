# shems_app/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, ServiceLocation, DeviceModel, EnrolledDevice, DeviceHistory, EnergyPrice, UserSession, UserProfile
from .serializers import CustomerSerializer, LoginSerializer, ServiceLocationSerializer, EnrolledDeviceSerializer, DeviceModelSerializer
from rest_framework import viewsets
from django.db.models import Avg, Sum
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone
from django.views import View
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_http_methods
from django.conf import settings

@api_view(['POST', 'OPTIONS'])
# Register a new customer
def register_user(request):
    if request.method == 'POST':
        print(request.data)
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            saved_customer = serializer.save()
            customer_id = saved_customer.CustomerID
            return Response({'success': True, 'customer_id': customer_id}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'OPTIONS':
        # Handle preflight OPTIONS request
        return Response(status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# return all the customer details
class CustomerViewSet(viewsets.ModelViewSet):
        queryset = Customer.objects.all()
        serializer_class = CustomerSerializer

@api_view(['POST'])
def login_user(request):
    if request.method == 'POST':
        phone_number = request.data.get('PhoneNumber')
        try:
            customer = Customer.objects.get(PhoneNumber=phone_number)
        except Customer.DoesNotExist:
            return Response({'error': 'Invalid phone number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check for multiple sessions and get session count
        has_multiple_sessions, active_sessions_count = invalidate_previous_sessions(customer)
        print(active_sessions_count)
        if has_multiple_sessions:
            return Response({'error': 'Multiple active sessions detected.', 'active_sessions': active_sessions_count}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            session_key = request.session.session_key
            if not session_key:
                # Create a new session if it doesn't exist
                request.session.create()
                session_key = request.session.session_key

            UserSession.objects.create(user=customer, session_key=session_key)
            return Response({
                'success': True,
                'customer_id': customer.CustomerID,
                'active_sessions': active_sessions_count,  
                'data': serializer.data,
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
def invalidate_previous_sessions(customer, max_allowed_sessions=1):
    user_sessions = UserSession.objects.filter(user=customer)
    active_sessions_count = len(user_sessions)

    if active_sessions_count > max_allowed_sessions:
        # Invalidate all but the most recent session
        for user_session in user_sessions.order_by('-created')[:max_allowed_sessions]:
            session_key = user_session.session_key
            try:
                session = Session.objects.get(session_key=session_key)
                session.delete()
            except Session.DoesNotExist:
                pass
            user_session.delete()

        return True, active_sessions_count  # Return True and count to indicate multiple sessions exist

    return False, active_sessions_count  # Return False and count if within limit

    
@api_view(['GET', 'OPTIONS'])
# gives the view for user details in dashboard
def dashboard_user(request, id):
    print("dashboard_user")
    if request.method=='GET':
        user = Customer.objects.get(CustomerID=id)
        serializer = CustomerSerializer(user)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
    
#  returns locatrion details for user
@api_view(['GET'])
def service_location(request, id):
    if request.method == 'GET':
        # Retrieve all service locations for the given customer
        service_locations = ServiceLocation.objects.filter(Customer=id)
        
        # Serialize the list of service locations
        serializer = ServiceLocationSerializer(service_locations, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'User not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
      
@api_view(['POST'])
def add_service_location(request, id):
    if request.method == 'POST':
        # Get the Customer instance
        try:
            customer = Customer.objects.get(CustomerID=id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create a new service location
        serializer = ServiceLocationSerializer(data=request.data)
        if serializer.is_valid():
            # Assign the Customer instance to the Customer field
            serializer.save(Customer=customer)
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

@api_view(['POST'])
def add_device(request, id):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(CustomerID=id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = EnrolledDeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(Customer=customer)

            return Response({'success': True}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = DeviceModel.objects.all()
    serializer_class = DeviceModelSerializer

@api_view(['GET'])
def get_devices_for_location_and_customer(request, location_id, customer_id):
    try:
        # Get devices based on location and customer
        devices = EnrolledDevice.objects.filter(Location=location_id, Customer=customer_id)

        # Serialize the queryset
        serializer = EnrolledDeviceSerializer(devices, many=True)

        # Return serialized data
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except EnrolledDevice.DoesNotExist:
        return Response({"error": "Devices not found for the specified location and customer."},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_devices_count_for_all_locations(request, customer_id):
    try:
        # Get all service locations for the customer
        locations = ServiceLocation.objects.filter(Customer=customer_id)

        # Create a dictionary to store device counts per location
        devices_count_dict = {}

        # Iterate over each location and get the device count
        for location in locations:
            devices_count = EnrolledDevice.objects.filter(Location=location.LocationID, Customer=customer_id).count()
            devices_count_dict[location.LocationID] = devices_count

        # Return the devices count dictionary
        return Response(devices_count_dict, status=status.HTTP_200_OK)

    except ServiceLocation.DoesNotExist:
        return Response({"error": "Service locations not found for the specified customer."},
                        status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET', 'PUT'])
# displays specific customer profile + edit profile
def customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(CustomerID=customer_id)

        if request.method == 'GET':
            print('get')
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET', 'PUT'])
def service_location_detail(request, customer_id, location_id):
    try:
        service_location = ServiceLocation.objects.get(LocationID=location_id)

        if request.method == 'GET':
            serializer = ServiceLocationSerializer(service_location)
            return Response(serializer.data)

        elif request.method == 'PUT':
            try:
                customer = Customer.objects.get(CustomerID=customer_id)
            except Customer.DoesNotExist:
                return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ServiceLocationSerializer(service_location, data=request.data)
            if serializer.is_valid():
                serializer.save(Customer= customer)
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    except ServiceLocation.DoesNotExist:
        return Response({"error": "Service Location not found."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET', 'PUT'])
def edit_device_view(request, device_id):
    try:
        # Retrieve the device instance
        device = EnrolledDevice.objects.get(DeviceID=device_id)

        if request.method == 'GET':
            # Serialize the device data for GET request
            serializer = EnrolledDeviceSerializer(device)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            # Update the device details with the data from the request
            serializer = EnrolledDeviceSerializer(device, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except EnrolledDevice.DoesNotExist:
        return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AverageMonthlyEnergyConsumptionView(View):
    def get(self, request, customer_id, location_id, device_id):
        start_month = request.GET.get('start_month')  # Format: 'YYYY-MM'
        end_month = request.GET.get('end_month')  # Format: 'YYYY-MM'

        # Parse the start and end months to datetime objects
        start_month_start = datetime.strptime(start_month + '-01', '%Y-%m-%d')
        end_month_end = datetime.strptime(end_month + '-01', '%Y-%m-%d') + timedelta(days=31)

        # Calculate average monthly energy consumption per device type
        result = (
            DeviceHistory.objects
            .filter(
                DeviceID=device_id,
                CustomerID=customer_id,
                LocationID=location_id,
                Timestamp__range=(start_month_start, end_month_end)
            )
            .values('EventLabel')
            .annotate(average_consumption=Avg('EnergyConsumption'))
        )

        # Convert the result to a list for JsonResponse
        result_list = list(result)
        print(result_list)
        return JsonResponse({
            'startMonth': start_month,
            'endMonth': end_month,
            'averageConsumption': result_list
        }, safe=False)

class DeviceEnergyConsumptionView(View):
    def get(self, request, customer_id, location_id, start_month=None, end_month=None):
        # Parse the start and end months to datetime objects
        start_month_start = datetime.strptime(start_month + '-01', '%Y-%m-%d') if start_month else None
        end_month_end = datetime.strptime(end_month + '-01', '%Y-%m-%d') + timedelta(days=31) if end_month else None

        # Filter based on the specified location and time range
        filter_params = {
            'CustomerID': customer_id,
            'LocationID': location_id,
        }

        if start_month_start and end_month_end:
            filter_params['Timestamp__range'] = (start_month_start, end_month_end)

        # Fetch device energy consumption for the specified location and time range
        result = (
            DeviceHistory.objects
            .filter(**filter_params)
            .values('DeviceID')
            .annotate(total_consumption=Sum('EnergyConsumption'))
        )

        # Convert the result to a list for JsonResponse
        result_list = list(result)
        print(result_list)
        return JsonResponse(result_list, safe=False)

class EnergyPriceView(View):
    def get(self, request, customer_id):
        current_datetime = timezone.now()
        try:
            customer = Customer.objects.get(CustomerID=customer_id)
            zip_code = customer.Zipcode
            try:
                energy_price = EnergyPrice.objects.filter(
                    ZipCode=zip_code,
                    Timestamp__lte=current_datetime,
                    EndDate__gte=current_datetime.date()
                ).latest('Timestamp')
                
                response_data = {
                    'ZipCode': energy_price.ZipCode,
                    'Timestamp': energy_price.Timestamp.isoformat(),
                    'HourlyRate': energy_price.HourlyRate,
                    'EndDate': energy_price.EndDate.isoformat(),
                }

                return JsonResponse(response_data)
            except EnergyPrice.DoesNotExist:
                return JsonResponse({'error': 'No energy price available for the current date and time.'}, status=404)
        except Customer.DoesNotExist:
            return Response({"error": "Customer not found."}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
@api_view(['DELETE'])
def delete_device_view(request, device_id):
    try:
        # Retrieve the device instance
        device = EnrolledDevice.objects.get(DeviceID=device_id)

        if request.method == 'DELETE':
            # Delete the device
            device.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    except EnrolledDevice.DoesNotExist:
        return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_service_location_view(request, location_id):
    try:
        # Retrieve the service location instance
        service_location = ServiceLocation.objects.get(LocationID=location_id)

        if request.method == 'DELETE':
            # Delete the service location
            service_location.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    except ServiceLocation.DoesNotExist:
        return Response({"error": "Service location not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def energy_consumption_by_location(request, customer_id):
    try:
        locations = ServiceLocation.objects.filter(Customer__CustomerID=customer_id)
        data = []

        for location in locations:
            total_consumption = DeviceHistory.objects.filter(
                CustomerID=customer_id, 
                LocationID=location
            ).aggregate(Sum('EnergyConsumption'))['EnergyConsumption__sum'] or 0

            device_count = EnrolledDevice.objects.filter(
                Location=location
            ).count()

            data.append({
                'location_id': location.LocationID,
                'address': location.Address,
                'total_energy_consumption': total_consumption,
                'device_count': device_count
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@api_view(['GET', 'PUT'])
def upload_profile_photo(request, customer_id):
    try:
        user = Customer.objects.get(CustomerID=customer_id)
        print(user.CustomerID)
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        if request.method == 'PUT':
            file = request.FILES.get('profile_photo')
            if not file:
                return JsonResponse({'error': 'No file provided.'}, status=400)

            # Save the file to the user's profile
            user_profile.photo.save(file.name, file)
            user_profile.save()

            return JsonResponse({'message': 'File uploaded successfully.'})

        elif request.method == 'GET':
            if user_profile.photo:
                photo_url = request.build_absolute_uri(settings.MEDIA_URL + user_profile.photo.name)
                print(photo_url)
                return JsonResponse({'photo_url': photo_url})
            else:
                return JsonResponse({'error': 'No profile photo found.'}, status=404)

    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found.'}, status=404)