from __future__ import annotations

from django.contrib import admin, messages
from django.utils import timezone

from .models import UserProfile
from .services.email import send_account_status_change_email


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "organization",
        "role",
        "approval_status",
        "reviewed_by",
        "reviewed_at",
        "result_email_sent_at",
    )
    list_filter = ("approval_status", "role", "organization", "created_at")
    search_fields = ("full_name", "organization", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at", "reviewed_by", "reviewed_at", "result_email_sent_at")
    actions = (
        "approve_applications",
        "decline_applications",
        "move_applications_to_pending",
        "resend_result_email",
    )

    def email(self, obj):
        return obj.user.email

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = UserProfile.objects.get(pk=obj.pk).approval_status

        status_changed = change and obj.approval_status != previous_status
        if status_changed:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            obj.user.is_active = obj.approval_status == "approved"
            obj.user.is_staff = obj.user.is_staff or obj.role == "admin_operator"
            obj.user.save(update_fields=["is_active", "is_staff"])
            obj.result_email_sent_at = None

        super().save_model(request, obj, form, change)

        if status_changed:
            sent = send_account_status_change_email(obj, previous_status=previous_status)
            if sent:
                self.message_user(request, "Account status change email sent.", messages.SUCCESS)
            else:
                self.message_user(
                    request,
                    "Status change saved, but email was not sent. Check Gmail SMTP settings.",
                    messages.WARNING,
                )

    @admin.action(description="Approve selected applications")
    def approve_applications(self, request, queryset):
        self._bulk_set_status(request, queryset, "approved")

    @admin.action(description="Decline selected applications")
    def decline_applications(self, request, queryset):
        self._bulk_set_status(request, queryset, "declined")

    @admin.action(description="Move selected applications back to pending")
    def move_applications_to_pending(self, request, queryset):
        self._bulk_set_status(request, queryset, "pending")

    @admin.action(description="Resend registration result email")
    def resend_result_email(self, request, queryset):
        sent_count = 0
        for profile in queryset:
            if send_account_status_change_email(profile):
                sent_count += 1
        self.message_user(request, f"Sent {sent_count} result email(s).", messages.INFO)

    def _bulk_set_status(self, request, queryset, status):
        sent_count = 0
        changed_count = 0
        skipped_count = 0
        now = timezone.now()
        for profile in queryset:
            previous_status = profile.approval_status
            if previous_status == status:
                skipped_count += 1
                continue
            profile.approval_status = status
            profile.reviewed_by = request.user
            profile.reviewed_at = now
            profile.result_email_sent_at = None
            profile.user.is_active = status == "approved"
            profile.user.is_staff = profile.user.is_staff or profile.role == "admin_operator"
            profile.user.save(update_fields=["is_active", "is_staff"])
            profile.save()
            changed_count += 1
            if send_account_status_change_email(profile, previous_status=previous_status):
                sent_count += 1
        self.message_user(
            request,
            (
                f"Changed {changed_count} application(s), skipped {skipped_count} unchanged "
                f"application(s), sent {sent_count} email(s)."
            ),
            messages.INFO,
        )
