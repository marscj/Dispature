from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.translation import gettext, gettext_lazy as _
from jet.admin import CompactInline

from django.db.models import Q
from datetime import date

from jet.admin import CompactInline
from django_object_actions import DjangoObjectActions

from .site import BaseAdminSite
from .base_admin import BaseModelAdmin
import main.forms as MainForm
import main.models as MainModel

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
class StaffAdmin(BaseUserAdmin, PermissionAdmin):

    add_form = MainForm.StaffCreationForm
    form = MainForm.StaffChangeForm

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
                )
            }
        ],

        [
            _('PersonInfo'), {
                'fields': [
                    'photo',
                    'status',
                    'day_pay',
                    'store',
                    'driver',
                    'tourguide',
                    'accept',
                    'introduction'
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
                    'verifycode',
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'name',
        'phone',
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
        'driver',
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
        'tourguide',
        'driver',
    ]

    # other_list_filter = [
    #     'order__start_time',
    #     'order__end_time',
    # ]
    #
    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)
    #
    #     if IS_POPUP_VAR not in request:
    #         start_time = request.GET.get('order__start_time')
    #         end_time = request.GET.get('order__end_time')
    #
    #         if start_time is not None and end_time is not None:
    #             if start_time > end_time:
    #                 start_time, end_time = end_time, start_time
    #
    #             if request.GET.get('driver') or request.GET.get('tourguide'):
    #                 qs = MainModel.Staff.objects.exclude(
    #                     Q(order__start_time__range=(start_time, end_time))
    #                     | Q(order__end_time__range=(start_time, end_time)))
    #
    #                 return qs
    #
    #     if request.user.is_superuser:
    #         return qs
    #
    #     return qs.filter(id=request.user.staff.id)

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
class VehicleAdmin(PermissionAdmin):

    inlines = [
        ImageInline,
    ]

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
                    'store'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'model',
        'exp_date',
        'policy_no',
        'status',
    ]

    list_display_links = [
        '__str__',
        'exp_date',
        'model',
        'policy_no',
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
        'status',
    ]

    # other_list_filter = [
    #     'order__start_time',
    #     'order__end_time'
    # ]

    # def get_queryset(self, request):
    #     qs = super().get_queryset(request)

    #     if IS_POPUP_VAR not in request:
    #         start_time = request.GET.get('order__start_time')
    #         end_time = request.GET.get('order__end_time')

    #         if start_time is not None and end_time is not None:
    #             if start_time > end_time:
    #                 start_time, end_time = end_time, start_time

    #             qs = MainModel.Vehicle.objects.exclude(
    #                 Q(order__start_time__range=(start_time, end_time))
    #                 | Q(order__end_time__range=(start_time, end_time)))
    #             return qs
    #     return qs


@admin.register(MainModel.VehicleModel, site=site)
class VehicleModelAdmin(PermissionAdmin):
    fields = [
        'model',
        'name',
        'num',
        'day_pay',
        'pickup_pay',
        'photo'
    ]

    list_display = [
        '__str__',
        'model',
        'num',
        'day_pay',
        'pickup_pay'
    ]

    list_display_links = [
        '__str__',
        'model',
        'num',
    ]

    list_editable = [
        'day_pay',
        'pickup_pay'
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
        'verifycode'
    ]

    list_display = [
        'name',
        'tel',
        'phone',
        'email',
        'addr',
        'verifycode'
    ]

    list_display_links = [
        'name',
        'tel',
        'phone',
        'email',
        'addr',
        'verifycode'
    ]

    readonly_fields = [
        'verifycode'
    ]

    def change_code(self, request, obj):
        from django.utils.crypto import get_random_string
        if request.user.is_superuser:
            obj.verifycode = get_random_string(
                length=4, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            obj.save()

    change_code.label = "Change Verifycode"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )


@admin.register(MainModel.OrderStaff, site=site)
class OrderStaffAdmin(PermissionAdmin):

    form = MainForm.OrderStaffForm

    add_form = MainForm.OrderStaffCreateForm

    fields = [
        'orderId',
        'amount',
        'start_time',
        'end_time',
        'duration',
        'status',
        'pay_status',
        'staff_confirm',
        'staff',
        'client',
        'remake',
    ]

    add_fields = [
        'start_time',
        'end_time',
        'status',
        'pay_status',
        'staff_confirm',
        'staff',
        'client',
        'remake',
    ]

    list_display = [
        '__str__',
        'staff',
        'client',
        'amount',
        'duration',
        'start_time',
        'end_time',
        'status',
        'pay_status',
        'staff_confirm',
    ]

    list_display_links = [
        '__str__',
        'staff',
        'client',
        'amount',
        'start_time',
        'end_time',
        'duration',
    ]

    list_editable = [
        'status',
        'pay_status',
        'staff_confirm',
    ]

    raw_id_fields = [
        'staff',
        'client'
    ]

    readonly_fields = [
        'duration',
    ]

    date_hierarchy = 'create_time'


@admin.register(MainModel.OrderVehicle, site=site)
class OrderVehicleAdmin(PermissionAdmin):

    form = MainForm.OrderVehicleForm
    add_form = MainForm.OrderVehicleCreateForm

    fields = [
        'orderId',
        'amount',
        'pickup_pay',
        'pickup_type',
        'start_time',
        'end_time',
        'duration',
        'status',
        'pay_status',
        'vehicle',
        'client',
        'remake',
    ]

    add_fields = [
        'pickup_type',
        'start_time',
        'end_time',
        'status',
        'pay_status',
        'vehicle',
        'client',
        'remake',
    ]

    list_display = [
        '__str__',
        'vehicle',
        'client',
        'amount',
        'pickup_pay',
        'duration',
        'start_time',
        'end_time',
        'pickup_type',
        'status',
        'pay_status',
        'remake',
    ]

    list_display_links = [
        '__str__',
        'amount',
        'start_time',
        'end_time',
        'pickup_pay',
        'duration',
        'vehicle',
        'client',
        'remake',
    ]

    list_editable = [
        'pay_status',
        'status',
    ]

    raw_id_fields = [
        'vehicle',
        'client'
    ]

    readonly_fields = [
        'duration',
        'pickup_pay',
    ]

    date_hierarchy = 'create_time'


@admin.register(MainModel.Client, site=site)
class ClientAdmin(BaseUserAdmin, PermissionAdmin):
    add_form = MainForm.ClientCreationForm
    form = MainForm.ClientChangeForm

    add_fieldsets = [
        [
            _('General *'), {
                'classes': ('wide',),
                'fields': [
                    'username',
                    'password1',
                    'password2',
                    'phone',
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
                    'client_type',
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
        'client_type',
        'company'
    ]

    list_display_links = [
        '__str__',
        'phone',
        'is_active',
        'client_type',
        'company'
    ]

    readonly_fields = [
        'client_type',
        'password',
        'username'
    ]

    list_filter = [
        'client_type',
        'company'
    ]


class ClientInline(CompactInline):
    model = MainModel.Client
    extra = 0

    fields = [
        'name',
        'phone',
    ]


@admin.register(MainModel.Company, site=site)
class CompanyAdmin(DjangoObjectActions, PermissionAdmin):

    form = MainForm.CompanyForm

    inlines = [
        ClientInline,
    ]

    list_display = [
        '__str__',
        'contacts',
        'tel',
        'phone',
        'addr',
        'email',
        'account',
        'admin'
    ]

    list_display_links = [
        '__str__',
        'contacts',
        'tel',
        'phone',
        'addr',
        'email',
        'account',
        'admin'
    ]

    raw_id_fields = [
        'admin'
    ]

    readonly_fields = [
        'verifycode'
    ]

    def change_code(self, request, obj):
        from django.utils.crypto import get_random_string
        if request.user.is_superuser:
            obj.verifycode = get_random_string(
                length=4, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            obj.save()

    change_code.label = "Change Verifycode"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )
