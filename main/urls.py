from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (StaffViewSet, CompanyViewSet, ClientViewSet, OrderStaffViewSet, StaffSigup, StoreViewSet, VehicleModelSellViewSet, StaffModelViewSet, UpLoadFile)

from .admin import site
from .xadmin import xsite

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, base_name='staff')
router.register(r'companys', CompanyViewSet, base_name='company')
router.register(r'clients', ClientViewSet, base_name='client')
router.register(r'order_staff', OrderStaffViewSet, base_name='order_staff')
router.register(r'stores', StoreViewSet, base_name='store')
router.register(r'modelsell', VehicleModelSellViewSet, base_name='store')
router.register(r'special', StaffModelViewSet, base_name='special')

urlpatterns = [
    url(r'staffs/regist/', StaffSigup.as_view()),
    url(r'upload/',UpLoadFile.as_view()),
    path('admin/', site.urls),
    path('xadmin/', xsite.urls),
] + router.urls
