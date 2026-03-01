from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the task
        return obj.user == request.user