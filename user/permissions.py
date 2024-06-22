from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a profile to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user
