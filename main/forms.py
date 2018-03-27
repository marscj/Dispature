from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

import main.models as main
from .validators import verifycode_validate


class StaffCreationForm(UserCreationForm):
    code = forms.CharField(max_length=4, required=True,widget=forms.TextInput, help_text='verification code')

    class Meta:
        model = main.Staff
        fields = ('username', 'password1', 'password2','name', 'phone', 'code')

    def clean_code(self):
        code = self.cleaned_data['code']
        verifycode_validate(code)
        return code
