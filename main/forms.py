from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.contenttypes.models import ContentType

import main.models as main
from .validators import verifycode_validate

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

class StaffCreationForm(UserCreationForm):
    verifycode = forms.CharField(max_length=4, required=True,widget=forms.TextInput, help_text='company verifycode')
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=False,
        initial='+971'
    )

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

class CompanyForm(forms.ModelForm):

    tel = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Tel number',
        required=False,
        initial='+971'
    )

    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=False,
        initial='+971'
    )

    class Meta:
        model = main.Company
        fields = '__all__'
