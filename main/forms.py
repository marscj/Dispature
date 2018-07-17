from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ValidationError

import main.models as MainModel

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .utils import Tools
import datetime
import main.constants as Constants
from main.order_helper import OrderHelper


class StaffForm(UserChangeForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Staff
        fields = '__all__'


class StaffCreationForm(UserCreationForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Staff
        fields = ('username', 'password1', 'password2', 'name', 'phone', 'store')

class ClientForm(UserChangeForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Client
        fields = '__all__'

class ClientCreateForm(UserCreationForm):
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Client
        fields = ['username', 'password1', 'password2', 'name', 'phone', 'company']

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
        required=True,
        initial='+971'
    )

    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        required=True,
        initial='+971'
    )

    class Meta:
        model = MainModel.Company
        fields = '__all__'

    def clean_admin(self):
        admin = self.cleaned_data.get('admin')
        name = self.cleaned_data.get('name')

        if not self.instance._state.adding:
            name = self.instance.name

        if admin:
            if admin.company:
                if admin.company.name != name:
                    raise ValidationError(
                        '%s is not this company.' % admin.name)
            else:
                raise ValidationError('%s is personal.' % admin.name)
        return admin

class AccountRechargeCreateForm(forms.ModelForm, OrderHelper):
    
    class Meta:
        model = MainModel.AccountRecharge
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount <= 0:
            raise ValidationError('Enter a number.')

        return amount

    def save(self, commit=True):
        account = super().save(commit=False)

        self.create_account_detail(account.amount, 0, None, account.company)
        account.balance = account.company.balance
        account.save()
        return account

class OrderBaseForm(forms.ModelForm, OrderHelper):

    def clean_staff(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        order_type = self.cleaned_data.get('order_type')
        staff = self.cleaned_data.get('staff')

        if order_type != 0:
            if staff is None:
                raise ValidationError('This field is required')
            elif start_time is not None and end_time is not None:
                if self.order_staff_exsit(start_time, end_time, staff):
                    raise ValidationError('staff is busy')

        return staff
    
    def clean_vehicle(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        order_type = self.cleaned_data.get('order_type')
        vehicle = self.cleaned_data.get('vehicle')

        if order_type == 0:
            if vehicle is None:
                raise ValidationError('This field is required.')
            elif start_time is not None and end_time is not None:
                if self.order_vehicle_exsit(start_time, end_time, vehicle):
                    raise ValidationError('vehicle is busy.')

        return vehicle

    def clean(self):
        clean_data = super().clean()

        start_time = clean_data.get('start_time')
        end_time = clean_data.get('end_time')

        if start_time is not None and end_time is not None:
            duration = end_time - start_time

            if start_time > end_time:
                raise ValidationError('The end time must be after start time.')
            
            if duration.days * 24 * 3600 + duration.seconds < 3600:
                raise ValidationError('The duration is too short.')

        

        return clean_data

class OrderCreateForm(OrderBaseForm, OrderHelper):

    staff_status = forms.ChoiceField(required=True, choices=Constants.CREATE_STAFF_STATUS)
    service_type = forms.ChoiceField(required=True, choices=Constants.SERVICE_TYPE)

    class Meta:
        model = MainModel.Order
        fields = '__all__'    

    def clean(self):
        clean_data = super().clean()
        client = clean_data.get('client')
        start_time = clean_data.get('start_time')
        end_time = clean_data.get('end_time')
        order_type = clean_data.get('order_type')
        staff = clean_data.get('staff')
        vehicle = clean_data.get('vehicle')
        service_type = clean_data.get('service_type')

        if client is not None:
            if client.company is None:
                raise ValidationError('Client is not a company user.')
            elif client.company.status == 0:
                raise ValidationError('Company is disabled.')

        if start_time is not None and end_time is not None:
            days = Tools.convert_timedelta(end_time - start_time)

            if order_type is not None:
                if order_type == 0:
                    if vehicle is not None and service_type is not None and client is not None:
                        total, amount, premium_charge, service_charge, home_service_charge = self.get_order_charge(order_type, days, vehicle.model.store, vehicle.model, client.company.discount, service_type=service_type)

                        if client.company.balance - total < 0:
                            raise ValidationError('The company no balance.')
                else:
                    if staff is not None and client is not None:
                        total, amount = self.get_order_charge(order_type, days, staff.store, staff.model, client.company.discount)

                        if client.company.balance - total < 0:
                            raise ValidationError('The company no balance.')        

        return clean_data
    
    def save(self, commit=True):
        order = super().save(commit=False)

        order.orderId = self.create_order_id()
        order.duration = order.end_time - order.start_time
        order.order_status = 0
        order.pay_status = 1     
        
        if order.order_type == 0:
            order.staff_status = None
            order.store = order.vehicle.model.store
            total, amount, premium_charge, service_charge, home_service_charge = self.get_order_charge(order.order_type, Tools.convert_timedelta(order.duration), order.vehicle.model.store, order.vehicle.model, order.client.company.discount, service_type=order.service_type)
        else:
            order.service_type = None
            order.store = order.staff.store
            total, amount = self.get_order_charge(order.order_type, Tools.convert_timedelta(order.duration), order.staff.store, order.staff.model, order.client.company.discount)

        order.company = order.client.company
        order.save()

        self.create_account_detail(total, 1, order, order.company)

        return order


class OrderfForm(OrderBaseForm):
    
    class Meta:
        model = MainModel.Order
        fields = '__all__'

    def clean(self):
        clean_data = super().clean()

        return clean_data

    def save(self, commit=True):
        order = super().save(commit=False)
        
        if order.staff is not None:
            order.store = order.staff.store
        elif order.vehicle is not None:
            order.store = order.vehicle.model.store
        
        if order.order_status == 1:
            if order.pay_status == 1:
                order.pay_status = 2
                order.save()
        
        return order

class AccountDetailCreateForm(forms.ModelForm, OrderHelper):
    
    detail_type = forms.ChoiceField(required=True, choices=Constants.CREATE_DETAIL_TYPE)
    explanation = forms.CharField(required=True, max_length=128)

    class Meta:
        model = MainModel.AccountDetail
        fields = '__all__'

    def clean_order(self):
        order = self.cleaned_data.get('order')
        detail_type = self.cleaned_data.get('detail_type')

        if order is None:
            raise ValidationError('This field is required.')
        else:
            if detail_type == '2':
                if order.order_status != 1:
                    raise ValidationError('Please cancel the order.')
                elif order.pay_status == 0:
                    raise ValidationError('Order not paid.')
                elif order.pay_status == 3:
                    raise ValidationError('Order has been refunded.')
            else:
                if order.order_status == 1:
                    raise ValidationError('Order has been cancelled.')
            
        return order

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        detail_type = self.cleaned_data.get('detail_type')
        
        if detail_type is not None:
            if detail_type == 3:
                if amount <= 0:
                    raise ValidationError('Enter a number.')

        return amount

    def clean(self):
        clean_data = super().clean()

        order = clean_data.get('order')
        amount = clean_data.get('amount')
        detail_type = clean_data.get('detail_type')

        if detail_type == '3':
            if order is not None and amount is not None:
                if order.company.balance - amount < 0:
                    raise ValidationError('The company no balance.')

        return clean_data

    def save(self, commit=True):
        detail = super().save(commit=False)

        detail.company = detail.order.company

        if detail.detail_type == 2:
            detail.amount = self.get_refund_amount(detail.order)
            detail.company.balance = round(detail.company.balance + detail.amount, 2)
            detail.company.save()

            detail.order.pay_status = 3
            detail.order.save()
        else :
            detail.company.balance = round(detail.company.balance - detail.amount, 2)
            detail.company.save()
        
        detail.balance = detail.order.company.balance
        detail.save()
        return detail