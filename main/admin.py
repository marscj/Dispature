from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.admin import GenericTabularInline, GenericStackedInline
from django.contrib.admin.options import IS_POPUP_VAR
from django.utils.translation import gettext, gettext_lazy as _

from django.db.models import Q
from datetime import date

from jet.admin import CompactInline
from django_object_actions import DjangoObjectActions

from .site import BaseAdminSite
from .base_admin import BaseModelAdmin
from main.forms import StaffCreationForm
import main.models as main

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

    def get_readonly_fields(self, request, obj=None):
        if obj is None or request.user.is_superuser:
            return ()

        return [f.name for f in self.model._meta.fields] + self.readonly_fields

    def has_add_permission(self, request):
        if request.user.is_superuser:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        return False


@admin.register(main.PPI, main.DLI, main.TLI, site=site)
class OtherAdmin(PermissionAdmin):
    pass


class ImageInline(GenericTabularInline):
    model = main.Image
    extra = 1


class TLIInline(admin.StackedInline):
    model = main.TLI
    extra = 1


class DLIInline(admin.StackedInline):
    model = main.DLI
    extra = 1


class PPIInline(admin.StackedInline):
    model = main.PPI
    extra = 1


class TaskInline(CompactInline):
    pass


@admin.register(main.Staff, site=site)
class StaffAdmin(BaseUserAdmin, PermissionAdmin):

    add_form = StaffCreationForm

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
                    'nickname',
                    'email',
                    'photo',
                    'driver',
                    'tourguide',
                    'status',
                    'work_status',
                    'hour_pay',
                    'company',
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
                    'verifycode'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'phone',
        'driver',
        'tourguide',
        'status',
        'is_active'
    ]

    list_display_links = [
        '__str__',
        'phone',
        'driver',
        'tourguide',
    ]

    list_editable = [
        'status',
        'is_active',
    ]

    list_filter = [
        'status',
        'tourguide',
        'driver',
    ]

    other_list_filter = [
        'order__start_time',
        'order__end_time',
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if IS_POPUP_VAR not in request:
            start_time = request.GET.get('order__start_time')
            end_time = request.GET.get('order__end_time')

            if start_time is not None and end_time is not None:
                if start_time > end_time:
                    start_time, end_time = end_time, start_time

                if request.GET.get('driver') or request.GET.get('tourguide'):
                    qs = main.Staff.objects.exclude(
                        Q(order__start_time__range=(start_time, end_time))
                        | Q(order__end_time__range=(start_time, end_time)))

                    return qs

        if request.user.is_superuser:
            return qs

        return qs.filter(id=request.user.staff.id)

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


@admin.register(main.Vehicle, site=site)
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
                    'company'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'exp_date',
        'policy_no',
        'status',
    ]

    list_display_links = [
        '__str__',
        'exp_date',
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

    other_list_filter = [
        'order__start_time',
        'order__end_time'
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if IS_POPUP_VAR not in request:
            start_time = request.GET.get('order__start_time')
            end_time = request.GET.get('order__end_time')

            if start_time is not None and end_time is not None:
                if start_time > end_time:
                    start_time, end_time = end_time, start_time

                qs = main.Vehicle.objects.exclude(
                    Q(order__start_time__range=(start_time, end_time))
                    | Q(order__end_time__range=(start_time, end_time)))
                return qs
        return qs


@admin.register(main.VehicleModel, site=site)
class VehicleModelAdmin(PermissionAdmin):
    fields = [
        'model',
        'name',
        'num',
        'amount',
        'photo'
    ]

    list_display = [
        '__str__',
        'model',
        'num',
        'amount',
    ]

    list_display_links = [
        '__str__',
        'model',
        'num',
    ]

    list_editable = [
        'amount'
    ]


@admin.register(main.Company, site=site)
class CompanyAdmin(DjangoObjectActions, PermissionAdmin):
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
            obj.verifycode = get_random_string(length=4)
            obj.save()

    change_code.label = "Change Verifycode"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )


@admin.register(main.OrderStaff, site=site)
class OrderStaffAdmin(DjangoObjectActions, PermissionAdmin):
    fields = [
        'order_id',
        'amount',
        'start_time',
        'end_time',
        'status',
        'settle_status',
        'pay_status',
        'staff_confirm',
        'staff',
        'remake',
    ]

    raw_id_fields = [
        'staff',
    ]

@admin.register(main.OrderVehicle, site=site)
class OrderVehicleAdmin(DjangoObjectActions, PermissionAdmin):

    fields = [
        'order_id',
        'amount',
        'start_time',
        'end_time',
        'status',
        'pay_status',
        'vehicle',
        'remake',
    ]

    raw_id_fields = [
        'vehicle',
    ]