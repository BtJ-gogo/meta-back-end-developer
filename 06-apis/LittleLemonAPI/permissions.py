from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser and request.user.is_authenticated


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Manager").exists()
            and request.user.is_authenticated
        )


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Delivery crew").exists()
            and request.user.is_authenticated
        )


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Customer").exists()
            and request.user.is_authenticated
        )
