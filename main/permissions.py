from rest_framework.permissions import BasePermission
import logging

logger = logging.getLogger('django')


class AllowAny(BasePermission):

    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsAdminOrIsSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_superuser and request.user == obj

class IsStaff(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsStaffAdmin(BasePermission):

    def has_permission(self, request, view):
        try:
            return request.user and request.user.is_active and (request.user.is_superuser or request.user.staff.is_admin)
        except Exception as e:
            logger.info(e)

        return False


class IsStaffSelf(BasePermission):

    def has_object_permission(self, request, view, obj):
        try:
            return request.user and request.user.is_active and (request.user.id == obj.id or request.user.is_superuser or request.user.staff.is_admin)
        except Exception as e:
            logger.info(e)

        return False

class IsClientAdmin(BasePermission):

    def has_permission(self, request, view):
        try:
            return request.user and request.user.is_active and (request.user.client.company.admin == request.user.client)
        except Exception as e:
            logger.info(e)

        return False