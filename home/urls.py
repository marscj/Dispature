from django.conf.urls import url, include

from .views import home
from .views import privacy

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^privacy/', privacy, name='privacy'),
]
