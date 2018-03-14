from django.urls import path
from django.urls import reverse_lazy
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, Group
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core import serializers

import json

from .forms import TaskForm
from main.models import *
from main.forms import StaffCreationForm


class BaseAdminSite(AdminSite):

    def get_urls(self):
        urlpatterns = [
            path('signup/', self.signup, name='signup'),

            path('resource/', self.resource, name='resource'),
            path('vehicle/', self.vehicle, name='vehicle'),

            url(r'^reset/$', auth_views.PasswordResetView.as_view(
                template_name='admin/password_reset.html',
                email_template_name='admin/password_reset_email.html',
                subject_template_name='admin/password_reset_subject.txt',
                success_url=reverse_lazy('admin:password_reset_done')
            ), name='password_reset'),

            url(r'^reset/done/$',
                auth_views.PasswordResetDoneView.as_view(
                    template_name='admin/password_reset_done.html'),
                name='password_reset_done'),

            url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                auth_views.PasswordResetConfirmView.as_view(
                    template_name='admin/password_reset_confirm.html',
                    success_url=reverse_lazy('admin:password_reset_complete')
                ),
                name='password_reset_confirm'),

            url(r'^reset/complete/$',
                auth_views.PasswordResetCompleteView.as_view(
                    template_name='admin/password_reset_complete.html'),
                name='password_reset_complete'),
        ]

        return urlpatterns + super().get_urls()

    @never_cache
    def signup(self, request, extra_context=None):
        if request.method == 'POST':
            form = StaffCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin:index')
        else:
            form = StaffCreationForm()

        return render(request, 'admin/signup.html', {'form': form})

    @method_decorator(staff_member_required)
    def resource(self, request):
        task = TaskForm(request.POST)

        if task.is_valid():
            driver = Staff.objects.filter(
                is_driver=True, is_active=True, status='Enabled')
            tourguide = Staff.objects.filter(
                is_tourguide=True, is_active=True, status='Enabled')
            vehicle = Vehicle.objects.filter(status='Enabled')

            context = {'driver': serializers.serialize('json', driver), 'tourguide': serializers.serialize(
                'json', tourguide), 'vehicle': serializers.serialize('json', vehicle)}
            return HttpResponse(json.dumps(context), content_type='application/json')
            # return HttpResponse(serializers.serialize('json', driver), content_type='application/json')
        else:
            return HttpResponse(task.errors, content_type='application/json')

    @method_decorator(staff_member_required)
    def vehicle(self, request):
        start_time = request.GET.get('start_time')
        end_time = request.GET.get('end_time')

        vehicle = Vehicle.objects.filter(status='Enabled')

        data = serializers.serialize('json', vehicle)
        return HttpResponse(data, content_type='application/json')


admin.site.unregister(User)
admin.site.unregister(Group)
