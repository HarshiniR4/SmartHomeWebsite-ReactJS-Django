# shems_app/admin.py
from django.contrib import admin
from .models import Customer, ServiceLocation, DeviceModel, EnrolledDevice, DeviceHistory, EnergyPrice

admin.site.register(Customer)
admin.site.register(ServiceLocation)
admin.site.register(DeviceModel)
admin.site.register(EnrolledDevice)
admin.site.register(DeviceHistory)
admin.site.register(EnergyPrice)