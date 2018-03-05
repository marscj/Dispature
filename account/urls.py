from django.conf.urls import url, include

from .views import signup

urlpatterns = [
    url(r'^signup/$', signup, name='signup'),
]
