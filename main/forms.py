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
    verifycode = forms.CharField(max_length=4, required=True,
                                 widget=forms.TextInput, help_text='verifycode')
    phone = PhoneNumberField(
        widget=PhoneNumberPrefixWidget(),
        label='Phone number',
        required=False,
        initial='+971'
    )

    class Meta:
        model = MainModel.Staff
        fields = ('username', 'password1', 'password2', 'name', 'phone', 'verifycode')

    def clean_code(self):
        verifycode = self.cleaned_data['verifycode']
        verifycode_validate(verifycode)
        return verifycode

    def save(self, commit=True):
        user = super().save(commit=False)
        verifycode = self.cleaned_data['verifycode']
        store = MainModel.Store.objects.get(verifycode=verifycode)
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

    def save(self, commit=True):
        user = super().save(commit=True)

        user.name = '用户%08d' % user.userId

        return user


class ClientChangeForm(UserChangeForm):
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


class OrderStaffCreateForm(forms.ModelForm):

    # orderId = forms.CharField(max_length=32)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['orderId'].initial = self.initOrderId()

    class Meta:
        modle = MainModel.OrderStaff
        fields = '__all__'

    def initOrderId(self):
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end_time = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        count = MainModel.OrderStaff.objects.filter(create_time__range=(start_time, end_time)).count()
        count = 1 if count == 0 else count + 1
        return '%s-%04d' % (datetime.datetime.now().strftime('%Y-%m-%d'), count)

    def get_amount(self, duration, pay):
        days, hours, minutes = Tools.convert_timedelta(duration, 8)
        return days, hours, minutes, round((pay * days) + (pay / 24 * hours) + (pay / 8 / 60 * minutes), 2)

    def clean(self):
        super().clean()

        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time > end_time:
            raise ValidationError('the end time must be after start time')

        qs = MainModel.OrderStaff.objects.filter(
            Q(start_time__lte=start_time, end_time__gte=start_time)
            | Q(start_time__lte=end_time, end_time__gte=end_time)
            | Q(start_time__gte=start_time, end_time__lte=end_time))
        if qs:
            raise ValidationError('%s is busy' % qs[0].staff.name)

    def save(self, commit=True):
        order = super().save(commit=False)
    #     days, hours, minutes, amount = self.get_amount(
    #         self.cleaned_data['end_time'] - self.cleaned_data['start_time'], order.staff.day_pay)

    #     order.duration = '%02d:%02d:%02d' % (days, hours, minutes)
    #     order.amount = amount
        order.orderId = self.initOrderId()

        return order

class OrderStaffForm(forms.ModelForm):
    
    class Meta:
        modle = MainModel.OrderStaff
        fields = '__all__'

    def get_amount(self, duration, pay):
        days, hours, minutes = Tools.convert_timedelta(duration, 8)
        return days, hours, minutes, round((pay * days) + (pay / 24 * hours) + (pay / 8 / 60 * minutes), 2)

    def clean(self):
        super().clean()

        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time > end_time:
            raise ValidationError('the end time must be after start time')

        qs = MainModel.OrderStaff.objects.exclude(orderId=self.cleaned_data['orderId']).filter(
            Q(start_time__lte=start_time, end_time__gte=start_time)
            | Q(start_time__lte=end_time, end_time__gte=end_time)
            | Q(start_time__gte=start_time, end_time__lte=end_time))
        if qs:
            raise ValidationError('%s is busy' % qs[0].staff.name)

    # def save(self, commit=True):
    #     order = super().save(commit=False)
    #     days, hours, minutes, amount = self.get_amount(
    #         self.cleaned_data['end_time'] - self.cleaned_data['start_time'], order.staff.day_pay)

    #     order.duration = '%02d:%02d:%02d' % (days, hours, minutes)
    #     order.amount = amount

    #     return order

class OrderVehicleCreateForm(forms.ModelForm):

    # orderId = forms.CharField(max_length=32)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['orderId'].initial = self.initOrderId()

    class Meta:
        model = MainModel.OrderVehicle
        exclude = '__all__'

    def initOrderId(self):
        now = datetime.datetime.now()
        start_time = datetime.datetime(now.year, now.month, now.day, 0, 0, 0)
        end_time = datetime.datetime(now.year, now.month, now.day, 23, 59, 59)
        count = MainModel.OrderVehicle.objects.filter(create_time__range=(start_time, end_time)).count()
        count = 1 if count == 0 else count + 1
        return '%s-%04d' % (datetime.datetime.now().strftime('%Y-%m-%d'), count)

    def get_amount(self, duration, pay):
        days, hours, minutes = Tools.convert_timedelta(duration, 24)
        return days, hours, minutes, round((pay * days) + (pay / 24 * hours), 2)

    def clean(self):
        super().clean()

        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time > end_time:
            raise ValidationError('the end time must be after start time')

        qs = MainModel.OrderVehicle.objects.filter(
            Q(start_time__lte=start_time, end_time__gte=start_time)
            | Q(start_time__lte=end_time, end_time__gte=end_time)
            | Q(start_time__gte=start_time, end_time__lte=end_time))
        if qs:
            raise ValidationError('%s is busy' %
                                  qs[0].vehicle.traffic_plate_no)

    def save(self, commit=True):
        order = super().save(commit=False)

    #     days, hours, minutes, amount = self.get_amount(
    #         self.cleaned_data['end_time'] - self.cleaned_data['start_time'], order.vehicle.model.day_pay)

    #     order.duration = '%02d:%02d:%02d' % (days, hours, minutes)

    #     if order.pickup_type == 0:
    #         order.amount = amount
    #     else:
    #         order.amount = amount + order.vehicle.model.pickup_pay

        order.orderId = self.initOrderId()

        return order

class OrderVehicleForm(forms.ModelForm):

    class Meta:
        model = MainModel.OrderVehicle
        exclude = '__all__'

    def get_amount(self, duration, pay):
        days, hours, minutes = Tools.convert_timedelta(duration, 24)
        return days, hours, minutes, round((pay * days) + (pay / 24 * hours), 2)

    def clean(self):
        super().clean()

        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time > end_time:
            raise ValidationError('the end time must be after start time')

        qs = MainModel.OrderVehicle.objects.exclude(orderId=self.cleaned_data['orderId']).filter(
            Q(start_time__lte=start_time, end_time__gte=start_time)
            | Q(start_time__lte=end_time, end_time__gte=end_time)
            | Q(start_time__gte=start_time, end_time__lte=end_time))
        if qs:
            raise ValidationError('%s is busy' %
                                  qs[0].vehicle.traffic_plate_no)

    # def save(self, commit=True):
    #     order = super().save(commit=False)

    #     days, hours, minutes, amount = self.get_amount(
    #         self.cleaned_data['end_time'] - self.cleaned_data['start_time'], order.vehicle.model.day_pay)

    #     order.duration = '%02d:%02d:%02d' % (days, hours, minutes)

    #     if order.pickup_type == 0:
    #         order.amount = amount
    #     else:
    #         order.amount = amount + order.vehicle.model.pickup_pay

    #     return order