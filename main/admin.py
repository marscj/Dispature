from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.translation import gettext, gettext_lazy as _
from jet.admin import CompactInline

from datetime import date

from django_object_actions import DjangoObjectActions

from .site import BaseAdminSite
from .base_admin import BaseModelAdmin
import main.forms as MainForm 
import main.models as MainModel
from main.order_helper import OrderHelper

site = BaseAdminSite(name='admin')


class BaseUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions'
                                       )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'email', 'is_staff')

    def get_readonly_fields(self, request, obj=None):

        if obj is None or request.user.is_superuser:
            return ()

        return self.readonly_fields

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


class PermissionAdmin(BaseModelAdmin):
    readonly_fields = []
    add_form = None
    add_fields = []

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()

        return self.readonly_fields
        # return [f.name for f in self.model._meta.fields] + self.readonly_fields

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None and self.add_form:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

    def get_fields(self, request, obj=None):
        if not obj and self.add_fields:
            return self.add_fields
        return super().get_fields(request, obj)


@admin.register(MainModel.PPI, MainModel.DLI, MainModel.TLI, site=site)
class OtherAdmin(PermissionAdmin):
    pass


class ImageInline(GenericTabularInline):
    model = MainModel.Image
    extra = 1


class TLIInline(admin.StackedInline):
    model = MainModel.TLI
    extra = 1


class DLIInline(admin.StackedInline):
    model = MainModel.DLI
    extra = 1


class PPIInline(admin.StackedInline):
    model = MainModel.PPI
    extra = 1


@admin.register(MainModel.Staff, site=site)
class StaffAdmin(BaseUserAdmin, PermissionAdmin, OrderHelper):

    form = MainForm.StaffForm
    add_form = MainForm.StaffCreationForm

    inlines = [
        PPIInline,
        DLIInline,
        TLIInline,
        ImageInline,
    ]

    readonly_fields = [
        'username',
        'name'
    ]

    fieldsets = [
        [
            None, {
                'fields': (
                    'username',
                    'password',
                    'phone',
                    'name',
                    'store',
                )
            }
        ],

        [
            _('PersonInfo'), {
                'fields': [
                    'photo',
                    'status',
                    'driver',
                    'tourguide',
                    'accept',
                    'model'
                ]
            }
        ],
        [
            _('Permissions'), {
                'fields': [
                    'is_active',
                    'is_staff',
                ]
            }
        ],
    ]

    add_fieldsets = [
        [
            _('General *'), {
                'classes': ('wide',),
                'fields': [
                    'username',
                    'password1',
                    'password2',
                    'name',
                    'phone',
                    'store',
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'name',
        'phone',
        'store',
        'model',
        'driver',
        'tourguide',
        'status',
        'accept',
        'is_active'
    ]

    list_display_links = [
        '__str__',
        'name',
        'phone',
        'store',
        'driver',
        'model',
        'tourguide',
    ]

    list_editable = [
        'status',
        'accept',
        'is_active',
    ]

    list_filter = [
        'status',
        'accept',
        'store',
        'tourguide',
        'driver',
        'model__name',
    ]

    raw_id_fields = ['model']

    other_list_filter = [
        'order__start_time',
        'order__end_time',
        'order__order_type',
        'order__orderId'
    ]
    
    def get_queryset(self, request):
        
        if IS_POPUP_VAR in request.GET:
            orderId = request.GET.get('order__orderId')
            orderType = request.GET.get('order__order_type')
            start_time = request.GET.get('order__start_time')
            end_time = request.GET.get('order__end_time')

            return self.order_queryset(orderType, start_time, end_time, orderId)
    
        return super().get_queryset(request)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, PPIInline) and obj is None:
                continue

            if isinstance(inline, DLIInline) and obj is None:
                continue

            if isinstance(inline, TLIInline) and obj is None:
                continue

            if isinstance(inline, ImageInline) and obj is None:
                continue

            yield inline.get_formset(request, obj), inline


@admin.register(MainModel.Vehicle, site=site)
class VehicleAdmin(PermissionAdmin, OrderHelper):

    # inlines = [
    #     ImageInline,
    # ]

    fieldsets = [
        [
            _('General *'), {
                'fields': [
                    'eng_no',
                    'chassis_no',
                    'traffic_plate_no',
                    'exp_date',
                    'reg_date',
                    'ins_exp',
                    'policy_no',
                    'status',
                    'model',
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'model',
        'exp_date',
        'status', 
    ]

    list_display_links = [
        '__str__',
        'exp_date',
        'model',
    ]

    list_editable = [
        'status',
    ]

    search_fields = [
        'traffic_plate_no',
        'policy_no',
        'exp_date',
    ]

    list_filter = [
        'model',
        'status', 
    ]

    other_list_filter = [
        'order__start_time',
        'order__end_time',
        'order__order_type',
        'order__orderId'
    ]

    def get_queryset(self, request):
    
        if IS_POPUP_VAR in request.GET:
            orderId = request.GET.get('order__orderId')
            orderType = request.GET.get('order__order_type')
            start_time = request.GET.get('order__start_time')
            end_time = request.GET.get('order__end_time')

            return self.order_queryset(orderType, start_time, end_time, orderId)
    
        return super().get_queryset(request)


@admin.register(MainModel.VehicleModel, site=site)
class VehicleModelAdmin(PermissionAdmin):

    inlines = [
        ImageInline,
    ]


    fields = [
        'model',
        'name',
        'seats',
        'automatic',
        'daily_charge',
        'premium_charge',
        'special_daily_charge',
        'store',
        'photo'
    ]

    list_display = [
        '__str__',
        'store',
        'model',
        'seats',
        'automatic',
        'daily_charge',
        'premium_charge',
        'special_daily_charge',
    ]

    list_display_links = [
        '__str__',
        'model',
        'seats',
        'automatic',
        'store'
    ]

    list_editable = [
        'daily_charge',
        'premium_charge',
        'special_daily_charge',
    ]


@admin.register(MainModel.Store, site=site)
class StoreAdmin(DjangoObjectActions, PermissionAdmin):

    form = MainForm.StoreForm

    fields = [
        'name',
        'tel',
        'phone',
        'email',
        'addr',
        'open_time',
        'close_time',
        'driver_daily_charge',
        'tourguide_daily_charge',
        'dt_daily_charge',
        'home_service_charge',
        'service_charge',
        'latitude',
        'longitude',
        'verify'
    ]

    list_display = [
        'name',
        'tel',
        'phone',
        'email',
        'addr',
        'verify'
    ]

    list_display_links = [
        'name',
        'tel',
        'phone',
        'email',
        'addr',
        'verify'
    ]

    readonly_fields = [
        'verify'
    ]

    def change_code(self, request, obj):
        from django.utils.crypto import get_random_string
        if request.user.is_superuser:
            obj.verify = get_random_string(
                length=4, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            obj.save()

    change_code.label = "Change Verifycode"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )

class AccountDetailInline(admin.StackedInline):
    model = MainModel.AccountDetail
    extra = 0

    readonly_fields = [
        'amount',
        'detail_type',
        'explanation',
        'company'
    ]

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(MainModel.Order, site=site)
class OrderAdmin(PermissionAdmin):

    add_form = MainForm.OrderCreateForm 
    form = MainForm.OrderfForm

    class Media:
        js = [
            'admin/js/new_order.js'
        ]

    inlines = [
        AccountDetailInline
    ]

    add_fields = [
        'start_time',
        'end_time',
        'order_type',
        'service_type',
        'pick_up_addr',
        'drop_off_addr',
        'staff_status',
        'staff',
        'vehicle',
        'client',
        'remake',
    ]

    list_display = [
        '__str__',
        'start_time',
        'end_time',
        'duration',
        'order_status',
        'pay_status',
        'staff_status',
        'order_type',
        'service_type',
        'staff',
        'vehicle',
        'client',
        'store',
        'company',
    ]

    list_display_links = [
        '__str__',
        'start_time',
        'end_time',
        'duration',
        'order_status',
        'pay_status',
        'staff_status',
        'order_type',
        'service_type',
        'staff',
        'vehicle',
        'client',
        'store',
        'company'
    ]

    raw_id_fields = [
        'staff',
        'client',
        'company',
        'store',
        'vehicle'
    ]

    readonly_fields = [
        'orderId',
        'duration',
        'order_type',
        'start_time',
        'end_time',
        # 'service_type',
        # 'staff',
        # 'vehicle',
        'client',
        'store',
        'company'
    ]

    list_filter = [
        'order_type',
        'company',
        'staff',
        'vehicle',
        'service_type'
    ]

    search_fields = [
        'orderId'
    ]

    date_hierarchy = 'create_time'

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
            
        _readonly = []

        if obj.order_status != 0:
            _readonly = [f.name for f in self.model._meta.fields] #_readonly + ['order_status']

        if obj.pay_status != 3:
            if 'pay_status' in _readonly:
                _readonly.remove('pay_status')

        return self.readonly_fields + _readonly
    
    def get_fields(self, request, obj=None):
        if not obj and self.add_fields:
            return self.add_fields
        else:
            if obj.order_type == 0:
                return [
                    'orderId',
                    'start_time',
                    'end_time',
                    'duration',
                    'order_status',
                    'pay_status',
                    'order_type',
                    'service_type',
                    'pick_up_addr',
                    'drop_off_addr',
                    'vehicle',
                    'client',
                    'store',
                    'company',
                    'remake',
                ]
            else:
                return [
                    'orderId',
                    'start_time',
                    'end_time',
                    'duration',
                    'order_status',
                    'pay_status',
                    'order_type',
                    'staff',
                    'staff_status',
                    'client',
                    'store',
                    'company',
                    'remake',
                ]

@admin.register(MainModel.Client, site=site)
class ClientAdmin(BaseUserAdmin, PermissionAdmin):

    form = MainForm.ClientForm
    add_form = MainForm.ClientCreateForm

    add_fieldsets = [
        [
            _('General *'), {
                'classes': ('wide',),
                'fields': [
                    'username',
                    'password1',
                    'password2',
                    'phone',
                    'name',
                    'company'
                ]
            }
        ],
    ]

    fieldsets = [
        [
            None, {
                'fields': (
                    'username',
                    'password',
                    'phone',
                    'company',
                    'name',
                    'is_active',
                )
            }
        ],
    ]

    list_display = [
        '__str__',
        'phone',
        'is_active',
        'company'
    ]

    list_display_links = [
        '__str__',
        'phone',
        'is_active',
        'company'
    ]

    readonly_fields = [
        'password',
        'username'
    ]

    list_filter = [
        'company',
        'is_active',
    ]

    def get_queryset(self, request):
    
        if IS_POPUP_VAR in request.GET:
            return MainModel.Client.objects.exclude(company=None)
    
        return super().get_queryset(request)


@admin.register(MainModel.Company, site=site)
class CompanyAdmin(DjangoObjectActions, PermissionAdmin):

    form = MainForm.CompanyForm

    list_display = [
        '__str__',
        'contacts',
        'tel',
        'phone',
        'addr',
        'email',
        'balance',
        'discount',
        'admin',
        'status'
    ]

    list_display_links = [
        '__str__',
        'contacts',
        'tel',
        'phone',
        'addr',
        'email',
        'balance',
        'discount',
        'admin',
        'status'
    ]

    raw_id_fields = [
        'admin'
    ]

    readonly_fields = [
        'verify',
        'name',
        'balance'
    ]

    def change_code(self, request, obj):
        from django.utils.crypto import get_random_string
        if request.user.is_superuser:
            obj.verify = get_random_string(
                length=4, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            obj.save()

    change_code.label = "Change Verifycode"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )

@admin.register(MainModel.AccountRecharge, site=site)
class AccountRechargeAdmin(PermissionAdmin):

    add_form = MainForm.AccountRechargeCreateForm

    list_display = [
        '__str__',
        'amount',
        'create_time',
        'recharge_type',
        'serial_number',
    ]

    list_display_links = [
        '__str__',
        'amount',
        'create_time',
        'recharge_type',
        'serial_number',
    ]

    readonly_fields = [
        'amount',
        'create_time',
        'recharge_type',
        'serial_number',
        'company'
    ]

    list_filter =[
        'company__name'
    ]

    date_hierarchy = 'create_time'

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def get_form(self, request, obj=None, **kwargs):
        defaults = {}
        if obj is None and self.add_form:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

@admin.register(MainModel.AccountDetail, site=site)
class AccountDetailAdmin(PermissionAdmin):

    add_form = MainForm.AccountDetailCreateForm

    fields = [
        'create_time',
        'detail_type',
        'amount',
        'order',
        'company',
        'explanation'
    ]

    add_fields = [
        'detail_type',
        'amount',
        'order',
        'explanation'
    ]

    list_display = [
        '__str__',
        'amount',
        'detail_type',
        'order',
    ]

    list_display_links =[
        '__str__',
        'amount',
        'detail_type',
        'order',
    ]

    readonly_fields = [
        'company',
        'amount',
        'detail_type',
        'order',
        'create_time'
    ]

    list_filter =[
        'company__name',
        'detail_type'
    ]

    raw_id_fields = [
        'order',
        'company'
    ]

    date_hierarchy = 'create_time'
    
    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True