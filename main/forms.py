from django import forms
from django.forms.models import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.contenttypes.models import ContentType

from django.core.exceptions import ValidationError

import main.models as MainModel
from .validators import verifycode_validate

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
                        '%s is not this company' % admin.name)
            else:
                raise ValidationError('%s is personal' % admin.name)
        return admin

class AccountRechargeCreateForm(forms.ModelForm):
    
    class Meta:
        model = MainModel.AccountRecharge
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount <= 0:
            raise ValidationError('Enter a number')

        return amount

    def create_detail(self, account):
        account.company.balance = account.company.balance + account.amount
        account.company.save()
        MainModel.AccountDetail.objects.create(amount=account.amount, detail_type=0, order=None, company=account.company, balance=account.company.balance)

    def save(self, commit=True):
        account = super().save(commit=False)
        
        self.create_detail(account)
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
                raise ValidationError('This field is required')
            elif start_time is not None and end_time is not None:
                if self.order_vehicle_exsit(start_time, end_time, vehicle):
                    raise ValidationError('vehicle is busy')

        return vehicle

    def clean(self):
        clean_data = super().clean()

        start_time = clean_data.get('start_time')
        end_time = clean_data.get('end_time')

        if start_time is not None and end_time is not None:
            duration = end_time - start_time

            if start_time > end_time:
                raise ValidationError('The end time must be after start time')
            
            if duration.days * 24 * 3600 + duration.seconds < 3600:
                raise ValidationError('The duration is too short')

        return clean_data

class OrderCreateForm(OrderBaseForm):

    staff_status = forms.ChoiceField(required=True, choices=Constants.CREATE_STAFF_STATUS)
    service_type = forms.ChoiceField(required=True, choices=Constants.SERVICE_TYPE)

    class Meta:
        model = MainModel.Order
        fields = '__all__'
    
    def initOrderId(self):
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end_time = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        count = MainModel.Order.objects.filter(create_time__range=(start_time, end_time)).count()
        count = 1 if count == 0 else count + 1
        return '%s-%04d' % (datetime.datetime.now().strftime('%Y-%m-%d'), count)

    def get_amount(self, duration, order_type, store, company, staff=None, vehicle=None, service_type=0):

        days = Tools.convert_timedelta(duration)
        total = 0
        if order_type == 0:
            amount = vehicle.model.daily_charge + vehicle.model.premium_charge
            service = 0 if service_type == 0 else store.home_service_charge
            total = (amount * days) + store.service_charge + service

        elif order_type == 4:
            amount = staff.model.special_daily_charge
            total = amount * days
        
        elif order_type == 1:
            amount = store.driver_daily_charge
            total = amount * days

        elif order_type == 2:
            amount = store.tourguide_daily_charge
            total = amount * days
        
        elif order_type == 2:
            amount = store.dt_daily_charge
            total = amount * days
        
        return total * (1 - company.discount)

    def create_detail(self, order, amount):
        if order.company is not None:
            order.company.balance = order.company.balance - amount
            order.company.save()
            MainModel.AccountDetail.objects.create(amount=amount, detail_type=1, order=order, company=order.company, balance=order.company.balance)    

    def clean_client(self):
        client = self.cleaned_data.get('client')
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        order_type = self.cleaned_data.get('order_type')
        staff = self.cleaned_data.get('staff')
        vehicle = self.cleaned_data.get('vehicle')
        service_type = self.cleaned_data.get('service_type')

        if client is not None:
            if client.company is None:
                raise ValidationError('client is not a company user')        

        if start_time is not None and end_time is not None:
            duration = end_time - start_time
            amount = 0

            if order_type is not None:
                if order_type == 0:
                    if vehicle is not None and service_type is not None and client is not None:
                        amount = self.get_amount(duration, order_type, vehicle.model.store, client.company, None, vehicle, service_type)
                else:
                    if staff is not None and client is not None:
                        amount = self.get_amount(duration, order_type, staff.store, client.company, staff)
            
            if client is not None and client.company is not None:
                if client.company.balance - amount < 0:
                    raise ValidationError('the company no balance')

        return client
    
    def save(self, commit=True):
        order = super().save(commit=False)

        order.orderId = self.initOrderId()
        order.duration = order.end_time - order.start_time
        order.order_status = 0
        order.pay_status = 1     
        
        if order.order_type == 0:
            order.staff_status = None
            order.store = order.vehicle.model.store
            amount = self.get_amount(order.duration, order.order_type, order.store, order.client.company, None, order.vehicle, order.service_type)
        else:
            order.service_type = None
            order.store = order.staff.store
            amount = self.get_amount(order.duration, order.order_type, order.store, order.client.company, order.staff)

        order.company = order.client.company
        order.save()

        self.create_detail(order, amount)

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
        
        if order.order_status == 0:
            if order.staff_status == 2:
                order.order_status = 1
                order.pay_status = 2

        if order.order_status == 1:
            if order.pay_status == 2:
                order.pay_status = 3
                order.save()
                self.refund(order)
                order.save()
            else:
                order.pay_status = 2
                order.save()
        
        return order

class AccountDetailCreateForm(forms.ModelForm):
    
    detail_type = forms.ChoiceField(required=True, choices=Constants.CREATE_DETAIL_TYPE)
    explanation = forms.CharField(required=True, max_length=128)

    class Meta:
        model = MainModel.AccountDetail
        fields = '__all__'

    def clean_order(self):
        order = self.cleaned_data.get('order')

        if order is None:
            raise ValidationError('This field is required')
        else:
            if order.order_status == 1:
                raise ValidationError('Order has been cancelled')
            
        return order

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        
        if amount <= 0:
            raise ValidationError('Enter a number')

        return amount

    def clean(self):
        clean_data = super().clean()

        order = clean_data.get('order')
        amount = clean_data.get('amount')

        if order is not None and amount is not None:
            if order.company.balance - amount < 0:
                raise ValidationError('the company no balance')

        return clean_data

    def save(self, commit=True):
        detail = super().save(commit=False)

        detail.company = detail.order.company

        if detail.company is not None:
            detail.company.balance = detail.company.balance - detail.amount
            detail.company.save()

        detail.save()
        return detail