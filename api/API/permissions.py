from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit.
    Retrieve - all users
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS

    def has_permission(self, request, view):
        return request.user.is_superuser if request.method == 'POST' else True


class IsAdminOrCreateOnly(IsAdminOrReadOnly):
    """
    Custom permission to only allow admins to edit.
    All authenticated users can retrieve and create.
    Make sure you use filter_backends to allow users retrieve only their own objects
    """
    def has_permission(self, request, view):
        if request.method in ['GET', 'POST']:
            return request.user.is_authenticated
        return request.user.is_superuser


class IsAdminOrCreateOnlyOrReadOwnForOrder(permissions.BasePermission):
    """
    Custom permission:
    admin - only retrieve;
    authenticated users - create and get only own objects (queryset in viewset has to be filtered by user)
    """
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and \
               (request.user.is_superuser or obj.customer == request.user)

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.user.is_authenticated:
            return request.method == 'POST' or request.method in permissions.SAFE_METHODS


class IsAdminOrCreateOnlyForUsers(permissions.BasePermission):
    """
    Custom permission:
    admin - only retrieve and create;
    user - create and get only own objects (queryset in viewset has to be filtered by user)
    """
    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS and (request.user.is_superuser or obj.pk == request.user.pk)

    def has_permission(self, request, view):
        return request.user.is_authenticated or (not request.user.is_authenticated and request.method == 'POST')
