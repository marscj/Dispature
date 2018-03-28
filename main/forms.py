from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

import main.models as main
from .validators import verifycode_validate


class StaffCreationForm(UserCreationForm):
    verifycode = forms.CharField(max_length=4, required=True,widget=forms.TextInput, help_text='company verifycode')

    class Meta:
        model = main.Staff
        fields = ('username', 'password1', 'password2','name', 'phone', 'verifycode')

    def clean_code(self):
        verifycode = self.cleaned_data['verifycode']
        verifycode_validate(verifycode)
        return verifycode

    def save(self, commit=True):
        user = super().save(commit=False)
        verifycode = self.cleaned_data['verifycode']
        company = main.Company.objects.get(verifycode=verifycode)
        user.company = company
        return user
