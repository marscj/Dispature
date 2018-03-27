from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Permission, UserManager
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django_countries.fields import CountryField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from django.utils.html import format_html

import time
import uuid
import datetime

from custom.utils import Tools
from .validators import verifycode_validate
from .constants import GROUP, STATUS, GENDER, LANGUAGE


class Image(models.Model):
    image = models.ImageField(upload_to="images")
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='images')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.id)


class TLI(models.Model):
    # TourGuide License Infomation
    license_no = models.CharField(
        max_length=64, unique=True, verbose_name='TourGuide No.')
    language = models.IntegerField(choices=LANGUAGE)
    date_of_expiry = models.DateField()

    staff = models.OneToOneField(
        'Staff', on_delete=models.CASCADE, related_name='TLI')

    class Meta:
        verbose_name = 'TourGuide License Infomation'
        verbose_name_plural = 'TourGuide License Info'

    def __str__(self):
        return self.license_no

    def save(self):
        self.staff.is_tourguide = True
        self.staff.save()

    def delete(self):
        self.staff.is_tourguide = False
        self.staff.save()


class DLI(models.Model):
    # Driver's License Infomation
    driving_license_no = models.CharField(
        max_length=32, unique=True, verbose_name='Driving License No.',)
    driver_code = models.CharField(max_length=16)
    date_of_issue = models.DateField()
    date_of_expiry = models.DateField()

    staff = models.OneToOneField(
        'Staff', on_delete=models.CASCADE, related_name='DLI')

    class Meta:
        verbose_name = 'Driver License Infomation'
        verbose_name_plural = 'Driver License Info'

    def __str__(self):
        return self.driving_license_no

    def save(self):
        self.staff.is_driver = True
        self.staff.save()

    def delete(self):
        self.staff.is_driver = False
        self.staff.save()


class PPI(models.Model):
    # Passport Infomation
    passport_no = models.CharField(
        max_length=32, unique=True, verbose_name='Passport No.')
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    gender = models.IntegerField(choices=GENDER)
    country = CountryField(blank_label='(select country)')
    date_of_birth = models.DateField()
    date_of_issue = models.DateField()
    date_of_expiry = models.DateField()

    staff = models.OneToOneField(
        'Staff', on_delete=models.CASCADE, related_name='PPI')

    class Meta:
        verbose_name = 'Passport Infomation'
        verbose_name_plural = 'Passport Info'

    def __str__(self):
        return self.first_name + ' ' + self.last_name


class Staff(User):
    full_name = models.CharField(
        max_length=64, unique=True, help_text='full name')
    phone = models.CharField(
        max_length=16, unique=True, help_text='your phone')
    wechart_account = models.CharField(max_length=64, null=True, blank=True)
    whatsup_account = models.CharField(max_length=64, null=True, blank=True)
    photo = models.ImageField(upload_to='photos', null=True, blank=True)
    status = models.CharField(max_length=16, default='enabled',
                              blank=True, null=True, choices=STATUS)
    is_driver = models.BooleanField(default=False, verbose_name='Driver ?')
    is_tourguide = models.BooleanField(
        default=False, verbose_name='TourGuide ?')
    is_operator = models.BooleanField(default=False, verbose_name='Operator ?')
    is_admin = models.BooleanField(
        default=False, verbose_name='Admin', help_text='This user has permission to add or delete')
    group = models.ManyToManyField(
        'BaseGroup', blank=True, related_name='staff', limit_choices_to={'type_name': 'staff'})

    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'

    def __str__(self):
        return self.full_name

    # def save(self, *args, **kwargs):
    #     super(Staff, self).save(*args, **kwargs)

    # def save(self, **kwargs):
    #     super(Staff, self).save(**kwargs)

    def save(self):
        super().save() 


class Vehicle(models.Model):
    model_name = models.CharField(max_length=64)
    model_year = models.IntegerField(
        default=2010, choices=Tools.get_year())  # 年份
    num_of_pass = models.IntegerField(
        default=5, verbose_name='number of passenger')  # 乘坐人数
    eng_no = models.CharField(max_length=16, unique=True)  # 发动机号
    chassis_no = models.CharField(max_length=32, unique=True)  # 车架号
    traffic_plate_no = models.CharField(max_length=16, unique=True)  # 车牌号
    exp_date = models.DateField()  # 有效期
    reg_date = models.DateField()  # 注册日期
    ins_exp = models.DateField()
    policy_no = models.CharField(max_length=32, unique=True)  # 保险号
    rate = models.FloatField(blank=True, default=0.0, help_text='Rent per day')
    status = models.CharField(
        max_length=16, default='enabled', blank=True, null=True, choices=STATUS)
    photo = models.ImageField(upload_to='photos', blank=True)
    group = models.ManyToManyField(
        'BaseGroup', blank=True, related_name='vehicle', limit_choices_to={'type_name': 'vehicle'})

    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.traffic_plate_no

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicle'


class Task(models.Model):
    uuid = models.UUIDField(
        auto_created=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_addr = models.CharField(max_length=256)
    end_addr = models.CharField(max_length=256)
    remake = models.TextField(blank=True, max_length=256)

    vehicle = models.ForeignKey(
        Vehicle, null=True, blank=True, on_delete=models.CASCADE, related_name='vehicle_task', to_field='traffic_plate_no', limit_choices_to={'status': 'enabled'})
    driver = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.CASCADE, related_name='driver_task', to_field='full_name', limit_choices_to={'is_driver': True, 'is_active': True, 'status': 'enabled'})
    tourguide = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.CASCADE, related_name='tourguide_task', to_field='full_name', limit_choices_to={'is_tourguide': True, 'is_active': True, 'status': 'enabled'})
    operator = models.ManyToManyField(
        Staff, blank=True, related_name='operator_task', limit_choices_to={'is_operator': True, 'is_active': True, 'status': 'enabled'})
    author = models.ForeignKey(
        Staff, null=True, blank=True, on_delete=models.CASCADE, related_name='author_task', to_field='full_name', limit_choices_to={'is_operator': True, 'is_active': True, 'status': 'enabled'})

    create_time = models.DateTimeField(auto_now_add=True)

    def start_time_in(self):
        time = self.start_time.strftime('%Y-%m-%d %H:%M')
        now = timezone.now().strftime('%Y-%m-%d %H:%M')

        if time >= now:
            color_code = 'green'
        else:
            color_code = 'red'

        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            time,
        )
    start_time_in.short_description = 'start time'
    start_time_in.admin_order_field = 'start_time'

    def end_time_in(self):
        time = self.end_time.strftime('%Y-%m-%d %H:%M')
        now = timezone.now().strftime('%Y-%m-%d %H:%M')

        if time >= now:
            color_code = 'green'
        else:
            color_code = 'red'

        return format_html(
            '<span style="color: {};">{}</span>',
            color_code,
            time,
        )
    end_time_in.short_description = 'end time'
    end_time_in.admin_order_field = 'end_time'

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Task'

    def __str__(self):
        # str(self.uuid)[:8]
        return self.create_time.strftime('%Y-%m-%d-%H-%M-%S')

    def clean_vehicle(self):
        if self.vehicle:
            qs = Task.objects.exclude(id=self.id).filter(vehicle=self.vehicle).filter(
                Q(start_time__lte=self.start_time,
                  end_time__gte=self.start_time)
                | Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
                | Q(start_time__gte=self.start_time, end_time__lte=self.end_time))

            if qs:
                raise ValidationError(
                    '%s is busy' % qs[0].vehicle.traffic_plate_no)

    def clean_driver(self):
        if self.driver:
            qs = Task.objects.exclude(id=self.id).filter(driver=self.driver).filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time)
                | Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
                | Q(start_time__gte=self.start_time, end_time__lte=self.end_time))
            if qs:
                raise ValidationError(
                    '%s is busy' % qs[0].driver.full_name)

        if self.driver and self.driver.is_tourguide:
            qs = Task.objects.exclude(id=self.id).filter(tourguide=self.driver).filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time)
                | Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
                | Q(start_time__gte=self.start_time, end_time__lte=self.end_time))
            if qs:
                raise ValidationError(
                    '%s is busy' % qs[0].tourguide.full_name)

    def clean_tourguide(self):
        if self.driver:
            qs = Task.objects.exclude(id=self.id).filter(tourguide=self.tourguide).filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time)
                | Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
                | Q(start_time__gte=self.start_time, end_time__lte=self.end_time))
            if qs:
                raise ValidationError(
                    '%s is busy' % qs[0].tourguide.full_name)

        if self.tourguide and self.tourguide.is_driver:
            qs = Task.objects.exclude(id=self.id).filter(driver=self.tourguide).filter(
                Q(start_time__lte=self.start_time, end_time__gte=self.start_time)
                | Q(start_time__lte=self.end_time, end_time__gte=self.end_time)
                | Q(start_time__gte=self.start_time, end_time__lte=self.end_time))
            if qs:
                raise ValidationError(
                    '%s is busy' % qs[0].driver.full_name)

    def clean(self):
        super().clean()

        if self.start_time is not None and self.end_time is not None:
            if self.start_time > self.end_time:
                raise ValidationError('the end time must be after start time')

            self.clean_vehicle()
            self.clean_driver()
            self.clean_tourguide()