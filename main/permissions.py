from rest_framework.permissions import BasePermission


class AllowAny(BasePermission):
    def has_permission(self, request, view):
        return True


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view)


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsStaff(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
