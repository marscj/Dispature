from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (StaffViewSet, VehicleViewSet, OrderStaffViewSet, StaffSigup)

from .admin import site
from .xadmin import xsite

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, base_name='staff')
router.register(r'vehicles', VehicleViewSet, base_name='vehicle')
router.register(r'order_staff', OrderStaffViewSet, base_name='order_staff')

urlpatterns = [
    url(r'staffs/regist/', StaffSigup.as_view()),
    path('admin/', site.urls),
    path('xadmin/', xsite.urls),
] + router.urls
