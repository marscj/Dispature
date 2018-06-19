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

class AccountRechargeCreateForm(forms.ModelForm):
    
    class Meta:
        model = MainModel.AccountRecharge
        fields = '__all__'

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        
        if amount <= 0:
            raise ValidationError('Enter a number')

        return amount

    def create_detail(self, account):
        account.company.balance = account.company.balance + account.amount
        account.company.save()
        MainModel.AccountDetail.objects.create(amount=account.amount, detail_type=0, order=None, company=account.company)

    def save(self, commit=True):
        account = super().save(commit=False)
        
        self.create_detail(account)
        account.save()
        return account

class OrderBaseForm(forms.ModelForm, OrderHelper):
    staff_status = forms.ChoiceField(required=True, choices=Constants.CREATE_STAFF_STATUS)
    delivery_type = forms.ChoiceField(required=True, choices=Constants.DELIVERY_TYPE)

    class Meta:
        model = MainModel.Order
        fields = '__all__'

    def clean_staff(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        order_type = self.cleaned_data.get('order_type')
        staff = self.cleaned_data.get('staff')

        if order_type != 0:
            if staff is None:
                raise ValidationError('This field is required')
            elif start_time is not None and end_time is not None:
                count = self.staff_queryset(start_time, end_time, staff)
                if count['count'] > 0:
                    raise ValidationError('staff is busy')

        return staff
    
    def clean_vehicle(self):
        start_time = self.cleaned_data.get('start_time')
        end_time = self.cleaned_data.get('end_time')
        order_type = self.cleaned_data.get('order_type')
        vehicle = self.cleaned_data['vehicle']

        if order_type == 0:
            if vehicle is None:
                raise ValidationError('This field is required')
            elif start_time is not None and end_time is not None:
                count = self.vehicle_queryset(start_time, end_time, vehicle)
                if count['count'] > 0:
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
    
    def initOrderId(self):
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end_time = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        count = MainModel.Order.objects.filter(create_time__range=(start_time, end_time)).count()
        count = 1 if count == 0 else count + 1
        return '%s-%04d' % (datetime.datetime.now().strftime('%Y-%m-%d'), count)

    def get_amount(self, duration, pay):
        days = Tools.convert_timedelta(duration, 5)
        return pay * days

    def create_detail(self, order, amount):
        order.company.balance = order.company.balance - amount
        order.company.save()
        MainModel.AccountDetail.objects.create(amount=amount, detail_type=1, order=order, company=order.company)
    
    def save(self, commit=True):
        order = super().save(commit=False)

        order.orderId = self.initOrderId()
        order.duration = order.end_time - order.start_time
        order.order_status = 0
        order.pay_status = 1     
        
        if order.order_type == 0:
            order.staff_status = None
            order.store = order.vehicle.model.store
        else:
            order.delivery_type = None
            order.store = order.staff.store

        order.company = order.client.company

        order.save()

        self.create_detail(order, self.get_amount(order.duration, 100))

        return order


class OrderfForm(OrderBaseForm):
    
    def save(self, commit=True):
        order = super().save(commit=False)
        
        if order.staff is not None:
            order.store = order.staff.store
        elif order.vehicle is not None:
            order.store = order.vehicle.model.store

        order.save()

        return order

    