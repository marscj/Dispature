from django import forms
from django.forms.models import ModelForm
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ValidationError

import main.models as MainModel
from .validators import verifycode_validate

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .utils import Tools
import datetime


class StaffChangeForm(UserChangeForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Staff
        fields = '__all__'


class StaffCreationForm(UserCreationForm):
    verify = forms.CharField(max_length=4, required=True,
                                 widget=forms.TextInput, help_text='verify code')
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Staff
        fields = ('username', 'password1', 'password2', 'name', 'phone', 'verify')

    def clean_code(self):
        verify = self.cleaned_data['verify']
        verifycode_validate(verify)
        return verify

    def save(self, commit=True):
        user = super().save(commit=False)
        verify = self.cleaned_data['verify']
        store = MainModel.Store.objects.get(verify=verify)
        if store:
            user.store = store

        return user


class ClientCreationForm(UserCreationForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number*',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Client
        fields = '__all__'


class ClientForm(UserChangeForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number*',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Client
        fields = '__all__'

    def save(self, commit=True):
        user = super().save(commit=False)

        return user


class StoreForm(forms.ModelForm):

    tel = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Tel number',
        required=True,
        initial='+971'
    )

    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Store
        fields = '__all__'


class CompanyForm(forms.ModelForm):

    tel = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Tel number*',
        required=False,
        initial='+971'
    )

    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number*',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Company
        fields = '__all__'

    def clean_admin(self):
        admin = self.cleaned_data['admin']

        if admin:
            if admin.company:
                if admin.company.name != self.cleaned_data['name']:
                    raise ValidationError(
                        '%s is not this company' % admin.name)
            else:
                raise ValidationError('%s is personal' % admin.name)

        return admin

# def get_amount(self, duration, pay):
#         days, hours, minutes = Tools.convert_timedelta(duration, 8)
#         return days, hours, minutes, round((pay * days) + (pay / 24 * hours) + (pay / 8 / 60 * minutes), 2)

class AccountRechargeAddForm(forms.ModelForm):
    
    class Meta:
        model = MainModel.AccountRecharge
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        
        if amount <= 0:
            return ValidationError('Enter a number')

        return amount

    def save(self, commit=True):
        account = super().save(commit=False)
        account.company.balance = account.company.balance + account.amount
        account.company.save()
        MainModel.AccountDetail.objects.create(amount=account.amount, detail_type=0, order=None, company=account.company)
        
        account.save()
        return account

    
