from rest_framework.permissions import BasePermission

# for admin
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated 
                and request.user.is_superuser
                )

# for manager
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_staff
            and not request.user.is_superuser
            )


# for admin and manager
class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated 
            and request.user.is_staff
            )