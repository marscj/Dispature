from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from account import views as accounts_views

# home
urlpatterns = [
    url('', include('home.urls'))
]

# account
urlpatterns = urlpatterns + [
    url('', include('account.urls'))
]

# custom
urlpatterns = urlpatterns + [
    url('', include('custom.urls'))
]

# jet
urlpatterns = urlpatterns + [
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r'^jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
]

# OAUTH2
urlpatterns = urlpatterns + [
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

# static files
urlpatterns = urlpatterns + \
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
