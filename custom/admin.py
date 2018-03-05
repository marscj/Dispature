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

from main.models import *
from main.forms import *
from .base import BaseAdminSite
from .model_admin import BaseModelAdmin

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
        elif request.user.staff.is_admin:
            return ('username', 'is_superuser')

        return self.readonly_fields

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.staff.is_admin:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.staff.is_admin:
            return True
        return False


class PermissionAdmin(BaseModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return ()
        elif request.user.is_superuser or request.user.staff.is_admin:
            return ()
        return [f.name for f in self.model._meta.fields] + self.readonly_fields

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.staff.is_admin:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.staff.is_admin:
            return True
        return False


@admin.register(PPI, DLI, TLI, site=site)
class OtherAdmin(PermissionAdmin):
    pass


class ImageInline(GenericTabularInline):
    model = Image
    extra = 1


class TLIInline(admin.StackedInline):
    model = TLI
    extra = 1


class DLIInline(admin.StackedInline):
    model = DLI
    extra = 1


class PPIInline(admin.StackedInline):
    model = PPI
    extra = 1


class TaskInline(CompactInline):
    pass


@admin.register(Staff, site=site)
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
        'is_staff',
        'is_superuser',
        'is_admin',
        'is_active',
        'is_driver',
        'is_tourguide',
        'is_operator',
    ]

    fieldsets = [
        [
            None, {
                'fields': (
                    'username',
                    'password',
                    'phone',
                    'full_name',
                )
            }
        ],

        [
            _('PersonInfo'), {
                'fields': [
                    'email',
                    'wechart_account',
                    'whatsup_account',
                    'photo',
                    'is_driver',
                    'is_tourguide',
                    'is_operator',
                    'status',
                    'group'
                ]
            }
        ],
        [
            _('Permissions'), {
                'fields': [
                    'is_active',
                    'is_staff',
                    'is_admin'
                ]
            }
        ],
        [
            _('Important dates'), {
                'fields': [
                    'last_login',
                    'date_joined'
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
                    'full_name',
                    'phone',
                    'code'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'phone',
        'is_driver',
        'is_tourguide',
        'is_operator',
        'wechart_account',
        'whatsup_account',
        'status',
        'is_active'
    ]

    list_display_links = [
        '__str__',
        'phone',
        'wechart_account',
        'whatsup_account',
        'is_driver',
        'is_tourguide',
        'is_operator',
    ]

    list_editable = [
        'status',
        'is_active',
    ]

    search_fields = [
        'first_name',
        'last_name',
    ]

    list_filter = [
        'status',
        'is_tourguide',
        'is_driver',
        'is_operator',
        'group',
    ]

    other_list_filter = [
        'driver_task__start_time',
        'driver_task__end_time',
        'tourguide_task__start_time',
        'tourguide_task__end_time'
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if IS_POPUP_VAR not in request:
            start_time = request.GET.get('driver_task__start_time') or request.GET.get(
                'tourguide_task__start_time')
            end_time = request.GET.get('driver_task__end_time') or request.GET.get(
                'tourguide_task__end_time')

            if start_time is not None and end_time is not None:
                if start_time > end_time:
                    start_time, end_time = end_time, start_time

                if request.GET.get('is_driver') or request.GET.get('is_tourguide'):
                    qs = Staff.objects.exclude(
                        Q(driver_task__start_time__range=(start_time, end_time))
                        | Q(driver_task__end_time__range=(start_time, end_time))
                        | Q(tourguide_task__start_time__range=(start_time, end_time))
                        | Q(tourguide_task__end_time__range=(start_time, end_time)))

                    return qs

        if request.user.is_superuser or request.user.staff.is_admin:
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


@admin.register(Vehicle, site=site)
class VehicleAdmin(PermissionAdmin):

    inlines = [
        ImageInline,
    ]

    fieldsets = [
        [
            _('General *'), {
                'fields': [
                    'model_name',
                    'model_year',
                    'num_of_pass',
                    'eng_no',
                    'chassis_no',
                    'traffic_plate_no',
                    'exp_date',
                    'reg_date',
                    'ins_exp',
                    'policy_no',
                    'rate',
                    'photo',
                    'status',
                    'group'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'model_name',
        'model_year',
        'num_of_pass',
        'exp_date',
        'policy_no',
        'rate',
        'status',
    ]

    list_display_links = [
        '__str__',
        'model_name',
        'model_year',
        'num_of_pass',
        'exp_date',
        'policy_no',
    ]

    list_editable = [
        'rate',
        'status',
    ]

    search_fields = [
        'traffic_plate_no',
        'model_name',
        'model_year',
        'policy_no',
        'exp_date',
        'num_of_pass'
    ]

    ordering = [
        'model_year',
    ]

    list_filter = [
        'model_name',
        'model_year',
        'num_of_pass',
        'status',
        'group',
    ]

    other_list_filter = [
        'vehicle_task__start_time',
        'vehicle_task__end_time'
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if IS_POPUP_VAR not in request:
            start_time = request.GET.get('vehicle_task__start_time')
            end_time = request.GET.get('vehicle_task__end_time')

            if start_time is not None and end_time is not None:
                if start_time > end_time:
                    start_time, end_time = end_time, start_time

                qs = Vehicle.objects.exclude(
                    Q(vehicle_task__start_time__range=(start_time, end_time))
                    | Q(vehicle_task__end_time__range=(start_time, end_time)))
                return qs
        return qs


@admin.register(Task, site=site)
class TaskAdmin(PermissionAdmin):

    form = TaskForm

    class Media:
        js = [
            'admin/js/setup_time.js'
        ]

    date_hierarchy = 'start_time'

    readonly_fields = [
        'author'
    ]

    raw_id_fields = [
        'vehicle',
        'driver',
        'tourguide',
        'author'
    ]

    fieldsets = [
        [
            _('General *'), {
                'fields': [
                    'start_addr',
                    'end_addr',
                    'start_time',
                    'end_time',
                    'remake',

                    'vehicle',
                    'driver',
                    'tourguide',
                    'operator',
                    'author'
                ]
            }
        ],
    ]

    list_display = [
        '__str__',
        'start_time_in',
        'end_time_in',
        'vehicle',
        'driver',
        'tourguide',
        'start_addr',
        'end_addr',
    ]

    list_filter = [
        'start_time',
        'end_time',
        'vehicle',
        'driver',
        'tourguide',
        'operator'
    ]

    list_display_links = [
        '__str__',
        'start_addr',
        'end_addr',
        'start_time_in',
        'end_time_in',
        'vehicle',
        'driver',
        'tourguide'
    ]

    search_fields = [
        'create_time',
        'driver__full_name',
        'tourguide__full_name',
        'vehicle__traffic_plate_no',
        'start_time',
        'end_time',
        'operator__full_name',
        'author__full_name'
    ]

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.staff.is_admin or request.user.staff.is_operator:
            return True
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        if request.user.staff.is_admin:
            return ('author')
        if obj is None or obj.author == request.user.staff:
            return ('author')
        if request.user.staff in obj.operator.all():
            return ('author', 'operator')

        return [f.name for f in self.model._meta.fields] + ['operator']

    def save_model(self, request, obj, form, change):
        if not obj.author and not request.user.is_superuser:
            obj.author = request.user.staff
        super().save_model(request, obj, form, change)


@admin.register(Setting, site=site)
class SettingAdmin(DjangoObjectActions, PermissionAdmin):
    fields = [
        'verifycode'
    ]

    list_display = [
        'verifycode'
    ]

    list_display_links = [
        'verifycode'
    ]

    readonly_fields = [
        'verifycode'
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return 'verifycode'

    def change_code(self, request, obj):
        if request.user.is_superuser or request.user.staff.is_admin:
            obj.verifycode = Tools.get_code()
            obj.save()

    change_code.label = "Change"
    change_code.short_description = "Change verifycode"
    change_actions = ('change_code', )


@admin.register(BaseGroup, site=site)
class BaseGroupAdmin(PermissionAdmin):

    fields = [
        'name',
        'type_name'
    ]

    list_display = [
        '__str__',
        'type_name'
    ]
