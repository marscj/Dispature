import main.models as main

from .site import BaseAdminSite
from .admin import (BaseUserAdmin, OtherAdmin, StaffAdmin,
                    VehicleAdmin, VehicleModelAdmin, StoreAdmin, OrderStaffAdmin, OrderVehicleAdmin, ClientAdmin, CompanyAdmin)

from oauth2_provider.admin import (Application, Grant, AccessToken, RefreshToken,
                                   ApplicationAdmin, GrantAdmin, AccessTokenAdmin, RefreshTokenAdmin)

xsite = BaseAdminSite(name='xadmin')
xsite.register(main.User, BaseUserAdmin)
xsite.register([main.PPI, main.DLI, main.TLI], OtherAdmin)
xsite.register(main.Staff, StaffAdmin)
xsite.register(main.Vehicle, VehicleAdmin)
xsite.register(main.VehicleModel, VehicleModelAdmin)
xsite.register(main.Store, StoreAdmin)
xsite.register(main.OrderStaff, OrderStaffAdmin)
xsite.register(main.OrderVehicle, OrderVehicleAdmin)
xsite.register(main.Client, ClientAdmin)
xsite.register(main.Company, CompanyAdmin)

xsite.register(Application, ApplicationAdmin)
xsite.register(Grant, GrantAdmin)
xsite.register(AccessToken, AccessTokenAdmin)
xsite.register(RefreshToken, RefreshTokenAdmin)
