from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permission class for Admin users only"""

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                hasattr(request.user, 'role') and
                request.user.role and
                request.user.role.name in ['admin', 'superadmin']  # Include superadmin
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """Permission class for Manager and Admin users"""

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                hasattr(request.user, 'role') and
                request.user.role and
                request.user.role.name in ['admin', 'manager', 'superadmin']  # Include superadmin
        )


class CanManageUser(permissions.BasePermission):
    """Permission to check if user can manage another user"""

    def has_object_permission(self, request, view, obj):
        # Users can always view/edit their own profile
        if request.user == obj:
            return True

        # Admin and superadmin can manage any user
        if request.user.is_admin:
            return True

        # Manager can manage employees but not admins/superadmins
        if request.user.is_manager:
            return not obj.is_admin

        return False


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access to owners of the object or admin users"""

    def has_object_permission(self, request, view, obj):
        # Admin and superadmin can access everything
        if request.user.is_admin:
            return True

        # Users can only access their own data
        return obj == request.user