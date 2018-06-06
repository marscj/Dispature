from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Permission, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django_countries.fields import CountryField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django.utils.html import format_html
from django.core.exceptions import ObjectDoesNotExist

from phonenumber_field.modelfields import PhoneNumberField

import time
import uuid
import datetime

from .utils import Tools
import main.constants as Constants


class Image(models.Model):
    image = models.ImageField(upload_to="images")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='images')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.image)


class TLI(models.Model):
    license_no = models.CharField(max_length=64, unique=True, verbose_name='TourGuide No.')
    date_of_expiry = models.DateField()

    staff = models.OneToOneField('Staff', on_delete=models.CASCADE, related_name='tli')

    class Meta:
        verbose_name = 'TourGuide License Infomation'
        verbose_name_plural = 'TourGuide License Info'

    def __str__(self):
        return self.license_no


class DLI(models.Model):
    driving_license_no = models.CharField(max_length=32, unique=True, verbose_name='Driving License No.',)
    driver_code = models.CharField(max_length=16)
    date_of_issue = models.DateField()
    date_of_expiry = models.DateField()

    staff = models.OneToOneField('Staff', on_delete=models.CASCADE, related_name='dli')

    class Meta:
        verbose_name = 'Driver License Infomation'
        verbose_name_plural = 'Driver License Info'

    def __str__(self):
        return self.driving_license_no


class PPI(models.Model):
    passport_no = models.CharField(max_length=32, unique=True, verbose_name='Passport No.')
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.IntegerField(choices=Constants.GENDER, default=0)
    country = CountryField(blank_label='(select country)')
    date_of_birth = models.DateField()
    date_of_issue = models.DateField()
    date_of_expiry = models.DateField()

    staff = models.OneToOneField('Staff', on_delete=models.CASCADE, related_name='ppi')

    class Meta:
        verbose_name = 'Passport Infomation'
        verbose_name_plural = 'Passport Info'

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class StoreManager(models.Manager):
    pass


class Store(models.Model):
    name = models.CharField(max_length=128, unique=True)
    tel = PhoneNumberField(unique=True)
    phone = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)
    addr = models.CharField(max_length=256)
    open_time = models.TimeField(default='09:00')
    close_time = models.TimeField(default='18:00')
    driver_day_pay = models.FloatField(default=120.0, verbose_name='driver day pay')  # 日薪
    tourguide_day_pay = models.FloatField(default=120.0, verbose_name='tourguide day pay')  # 日薪
    dt_day_pay = models.FloatField(default=240.0, verbose_name='driver&Tourguide day pay')
    latitude = models.FloatField()
    longitude = models.FloatField()
    verifycode = models.CharField(max_length=4, unique=True, default=Tools.get_code, help_text='For The Staff Regist')

    objects = StoreManager

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Store'

    def __str__(self):
        return self.name


class Staff(User):
    userId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True, help_text='name')  # 姓名
    phone = PhoneNumberField()  # 电话
    photo = models.ImageField(upload_to='photos', null=True, blank=True)  # 头像
    status = models.IntegerField(default=0, choices=Constants.STATUS) # 状态
    accept = models.BooleanField(default=False)
    driver = models.BooleanField(default=False, verbose_name='Driver ?')  # 是否 司机
    tourguide = models.BooleanField(default=False, verbose_name='TourGuide ?')  # 是否 导游
    update_time = models.DateTimeField(default=timezone.now, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='staff')
    model = models.ForeignKey('VehicleModel', blank=True, null=True, on_delete=models.CASCADE, related_name='staff')

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

    def __str__(self):
        return self.username

class VehicleModelManager(models.Manager):
    pass

class VehicleModel(models.Model):
    model = models.IntegerField(default=0,choices=Constants.MODEL)  # 类型
    name = models.CharField(max_length=64)  # 名称
    automatic = models.BooleanField(default=True)
    seats = models.IntegerField(default=5, verbose_name='passengers')  # 乘坐人数
    day_pay = models.IntegerField(default=120)  # 价格
    photo = models.ImageField(upload_to='vehicle', blank=True)  # 图片
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='model')
    
    objects = VehicleModelManager

    class Meta:
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Model'

    def __str__(self):
        return self.name


class VehicleManager(models.Manager):
    pass


class Vehicle(models.Model):
    eng_no = models.CharField(max_length=16, unique=True)               # 发动机号
    chassis_no = models.CharField(max_length=32, unique=True)           # 车架号
    traffic_plate_no = models.CharField(max_length=16, unique=True)     # 车牌号
    exp_date = models.DateField()                                       # 有效期
    reg_date = models.DateField()                                       # 注册日期
    ins_exp = models.DateField()                                        # 日期
    policy_no = models.CharField(max_length=32, unique=True)            # 保险号
    status = models.IntegerField(default=0, choices=Constants.STATUS)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='vehicle')

    objects = VehicleManager

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicle'

    def __str__(self):
        return self.traffic_plate_no


class AbstractOrder(models.Model):
    orderId = models.CharField(max_length=32, unique=True)
    amount = models.FloatField(default=0.0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration = models.CharField(max_length=128, default='')
    status = models.IntegerField(default=0, choices=Constants.ORDER_STATUS)
    pay_status = models.IntegerField(default=0, choices=Constants.PAY_STATUS)
    remake = models.TextField(blank=True, max_length=256)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.orderId


class OrderStaffManager(models.Manager):
    pass


class OrderStaff(AbstractOrder):
    staff_confirm = models.IntegerField(default=0, choices=Constants.STAFF_CONFIRM)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='order', limit_choices_to={'status': 1, 'accept': True})
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='order_staff')

    objects = OrderStaffManager

    class Meta:
        verbose_name = 'Order Staff'
        verbose_name_plural = 'Order Staff'


class OrderVehicleManager(models.Manager):
    pass


class OrderVehicle(AbstractOrder):
    pickup_type = models.IntegerField(default=0, choices=Constants.PICK_TYPE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='order', limit_choices_to={'status': 1})
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='order_vehicle')

    objects = OrderVehicleManager

    class Meta:
        verbose_name = 'Order Vehicle'
        verbose_name_plural = 'Order Vehicle'


class Company(models.Model):
    name = models.CharField(max_length=128, unique=True)
    contacts = models.CharField(max_length=32)
    tel = PhoneNumberField(unique=True)
    phone = PhoneNumberField(unique=True)
    addr = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    verifycode = models.CharField(max_length=4, unique=True, default=Tools.get_code, help_text='For The Client Regist')
    account = models.FloatField(default=0.0)
    status = models.IntegerField(default=0, choices=Constants.STATUS)
    admin = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='admin', blank=True, null=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'

    def __str__(self):
        return self.name


class Client(User):
    userId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64, unique=True)  # 昵称
    phone = PhoneNumberField(unique=True, verbose_name='Phone number')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='client', blank=True, null=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Client'

    def __str__(self):
        return self.name
