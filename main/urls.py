from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import StaffViewSet

router = DefaultRouter()
router.register(r'staffs', StaffViewSet, base_name='staff')
router.register(r'tasks', StaffViewSet, base_name='task')
urlpatterns = router.urls
