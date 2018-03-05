from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

from .models import *
from .validators import verifycode_validate


class StaffCreationForm(UserCreationForm):
    code = forms.CharField(max_length=4, required=True,
                           widget=forms.TextInput, help_text='verification code')

    class Meta:
        model = Staff
        fields = ('username', 'password1', 'password2',
                  'full_name', 'phone', 'code')

    def clean_code(self):
        code = self.cleaned_data['code']
        verifycode_validate(code)
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.save()

        content_query = ContentType.objects.filter(app_label='main')
        for content in content_query:
            permission_query = Permission.objects.filter(
                content_type_id=content.id)
            for permission in permission_query:
                user.user_permissions.add(permission.id)

        return user


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = '__all__'
        ordering = '-start_time'

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
