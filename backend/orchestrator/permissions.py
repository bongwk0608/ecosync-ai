from __future__ import annotations

from rest_framework.permissions import BasePermission


class IsApprovedUser(BasePermission):
    message = "Your account is not approved yet."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or user.is_superuser:
            return True
        profile = getattr(user, "ecosync_profile", None)
        return bool(profile and profile.approval_status == "approved" and user.is_active)


class IsApprovedUserOrAdminWrite(BasePermission):
    message = "You do not have permission for this dataset action."

    def has_permission(self, request, view):
        if not IsApprovedUser().has_permission(request, view):
            return False
        if request.method == "DELETE":
            return bool(request.user and request.user.is_staff)
        return True
