from django.conf.urls import url, include
from django.urls import path

from .admin import site
from .xadmin import xsite

urlpatterns = [
    path('admin/', site.urls),
    path('xadmin/', xsite.urls),
]
