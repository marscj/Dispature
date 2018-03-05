from main.models import *
from main.forms import *
from .base import BaseAdminSite
from .admin import (BaseUserAdmin, OtherAdmin, StaffAdmin,
                    VehicleAdmin, TaskAdmin, SettingAdmin, BaseGroupAdmin)

xsite = BaseAdminSite(name='xadmin')
xsite.register(User, BaseUserAdmin)
xsite.register([PPI, DLI, TLI], OtherAdmin)
xsite.register(Staff, StaffAdmin)
xsite.register(Vehicle, VehicleAdmin)
xsite.register(Task, TaskAdmin)
xsite.register(Setting, SettingAdmin)
xsite.register(BaseGroup, BaseGroupAdmin)
