# shems_app/models.py
from django.db import models
from django.conf import settings

class Customer(models.Model):
    CustomerID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    BillingAddressL1 = models.CharField(max_length=255)
    BillingAddressL2 = models.CharField(max_length=255)
    Zipcode = models.CharField(max_length=10)
    Email = models.EmailField()
    PhoneNumber = models.CharField(max_length=15)

# Define other models similarly
class ServiceLocation(models.Model):
    LocationID = models.AutoField(primary_key=True)
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    Address = models.CharField(max_length=255)
    UnitNumber = models.CharField(max_length=10, blank=True)
    MoveInDate = models.DateField()
    SquareFoot = models.IntegerField()
    Bedrooms = models.IntegerField()
    Occupants = models.IntegerField()

class DeviceModel(models.Model):
    ModelID = models.AutoField(primary_key=True)
    Type = models.CharField(max_length=255)
    ModelNumber = models.CharField(max_length=255)

class EnrolledDevice(models.Model):
    DeviceID = models.AutoField(primary_key=True)
    Location = models.ForeignKey(ServiceLocation, on_delete=models.CASCADE)
    Model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    Customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

class DeviceHistory(models.Model):
    DeviceID = models.ForeignKey(EnrolledDevice, on_delete=models.CASCADE)
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    LocationID = models.ForeignKey(ServiceLocation, on_delete=models.CASCADE)
    Timestamp = models.DateTimeField()
    EventLabel = models.CharField(max_length=255)
    EnergyConsumption = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

class EnergyPrice(models.Model):
    ZipCode = models.CharField(max_length=10)
    Timestamp = models.DateTimeField()
    HourlyRate = models.FloatField()
    EndDate = models.DateField()

class UserSession(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Link to Customer model
    session_key = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.CustomerID + " - " + self.session_key

class UserProfile(models.Model):
    user = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='profile')
    photo = models.ImageField(upload_to='profile_photos/')

    def __str__(self):
        return self.user.CustomerID