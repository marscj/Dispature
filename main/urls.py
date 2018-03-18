from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import (StaffViewSet, TaskViewSet, VehicleViewSet,
                    GroupViewSet, DLIViewSet, TLIViewSet, PPIViewSet,StaffSigup)

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, base_name='staff')
router.register(r'vehicles', VehicleViewSet, base_name='vehicle')
router.register(r'tasks', TaskViewSet, base_name='task')
router.register(r'groups', GroupViewSet, base_name='group')
router.register(r'dlis', DLIViewSet, base_name='DLI')
router.register(r'tlis', TLIViewSet, base_name='TLI')
router.register(r'ppis', PPIViewSet, base_name='PPI')

urlpatterns = [
    url(r'staffs/regist/', StaffSigup.as_view()),
] + router.urls
