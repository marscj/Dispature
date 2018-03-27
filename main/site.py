from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin.sites import AdminSite

class BaseAdminSite(AdminSite):
    pass
    
admin.site.unregister(User)
admin.site.unregister(Group)
