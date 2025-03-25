from rest_framework import permissions


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser and request.user.is_authenticated

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.group.filter(name="Managers").exists():
            return True


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.group.filter(name="Delivery Crew").exists():
            return True

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.groups.filter(name="Customer").exists()
            and request.user.is_authenticated
        )
