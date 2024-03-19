from rest_framework import serializers
from .models import Customer, ServiceLocation, DeviceModel, EnrolledDevice
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__' 

class ServiceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceLocation
        fields = '__all__' 
        


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'Name',
            'BillingAddressL1',
            'BillingAddressL2',
            'Zipcode',
            'Email',
            'PhoneNumber',
        ]

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'PhoneNumber',
            'Zipcode',
        ]
        
class DeviceModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceModel
        fields = ['ModelID', 'Type', 'ModelNumber']

class EnrolledDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnrolledDevice
        fields = ['DeviceID', 'Location', 'Model', 'Customer']