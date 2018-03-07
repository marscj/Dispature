from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import StaffViewSet, TaskViewSet, VehicleViewSet, GroupViewSet

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, base_name='staff')
router.register(r'vehicles', VehicleViewSet, base_name='vehicle')
router.register(r'tasks', TaskViewSet, base_name='task')
router.register(r'groups', GroupViewSet, base_name='group')
urlpatterns = router.urls
