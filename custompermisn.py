
from rest_framework import permissions


class IsSuperUser(permissions.BasePermission):

    # edit_methods = ("PUT", "PATCH")

    def has_permission(self, request, view):
        
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return False
        return False
