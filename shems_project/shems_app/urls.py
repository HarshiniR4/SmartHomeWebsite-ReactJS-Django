# shems_app/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import register_user, login_user, dashboard_user, service_location, add_service_location, CustomerViewSet, add_device, DeviceModelViewSet, get_devices_for_location_and_customer, get_devices_count_for_all_locations, customer_detail, service_location_detail, edit_device_view, AverageMonthlyEnergyConsumptionView, DeviceEnergyConsumptionView, EnergyPriceView, delete_device_view, delete_service_location_view, energy_consumption_by_location, upload_profile_photo

urlpatterns = [
    # Other URL patterns
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/dashboard/<int:id>', dashboard_user, name='dashboard_user'),
    path('api/service-locations/user/<int:id>', service_location, name='service_location'),
    path('api/service-locations/add/<int:id>/', add_service_location, name='add_device'),
    path('api/device/add/<int:id>/', add_device, name='add_service_location'),
    path('api/devices/<int:customer_id>/<int:location_id>/', get_devices_for_location_and_customer, name='get_devices_for_location_and_customer'),
    path('api/devices/count/<int:customer_id>', get_devices_count_for_all_locations, name ='get_devices_count_for_all_locations'),
    path('api/customers/', CustomerViewSet.as_view({'get': 'list'})),
    path('api/device-models/', DeviceModelViewSet.as_view({'get': 'list'})),
    path('api/customer/<int:customer_id>/', customer_detail, name='customer_detail'),
    path('api/service-location/<int:customer_id>/<int:location_id>/', service_location_detail, name='service_location_detail'),
    path('api/devices/edit/<int:device_id>/', edit_device_view, name='edit_device'),
    path('api/average_monthly_energy_consumption/<int:customer_id>/<int:location_id>/<int:device_id>/', AverageMonthlyEnergyConsumptionView.as_view(), name='average_monthly_energy_consumption'),
    path('api/device_energy_consumption/<int:customer_id>/<int:location_id>/', DeviceEnergyConsumptionView.as_view(), name='device_energy_consumption'),
    path('api/energy-price/<int:customer_id>/', EnergyPriceView.as_view(), name='energy_price'),
    path('api/delete_devices/<int:device_id>/', delete_device_view, name='delete_device_view'),
    path('api/delete_service_location/<int:location_id>/', delete_service_location_view, name='delete_service_location'),
    path('api/energy-consumption/<int:customer_id>/', energy_consumption_by_location, name='energy_consumption_by_location'),
    path('api/upload-profile-photo/<int:customer_id>/', upload_profile_photo, name='upload_profile_photo'),
]

# Serving the media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)