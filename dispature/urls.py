from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

# home
urlpatterns = [
    url('', include('home.urls'))
]

# main
urlpatterns = urlpatterns + [
    url('', include('main.urls'))
]

# jet
urlpatterns = urlpatterns + [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
]

# rest_framework
if settings.DEBUG:
    urlpatterns = urlpatterns + [
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]


# static files
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
