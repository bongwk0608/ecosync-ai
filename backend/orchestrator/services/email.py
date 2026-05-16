from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_account_status_change_email(profile, previous_status=None):
    if profile.approval_status not in {"pending", "approved", "declined"}:
        return False

    subject = {
        "approved": "EcoSync AI account approved",
        "declined": "EcoSync AI account declined",
        "pending": "EcoSync AI account moved back to pending review",
    }[profile.approval_status]
    transition = (
        f"Your account status changed from {previous_status} to {profile.approval_status}.\n\n"
        if previous_status
        else f"Your current account status is {profile.approval_status}.\n\n"
    )

    if profile.approval_status == "approved":
        message = (
            f"Hello {profile.full_name},\n\n"
            f"{transition}"
            "Your EcoSync AI account has been approved. You can now log in and "
            "access the ecosystem workspace.\n\n"
            "EcoSync AI"
        )
    elif profile.approval_status == "pending":
        message = (
            f"Hello {profile.full_name},\n\n"
            f"{transition}"
            "Your EcoSync AI account is pending admin review. You will receive "
            "another email when the review result changes.\n\n"
            "EcoSync AI"
        )
    else:
        note = f"\n\nAdmin note: {profile.admin_note}" if profile.admin_note else ""
        message = (
            f"Hello {profile.full_name},\n\n"
            f"{transition}"
            "Your EcoSync AI account was declined. Please contact the program "
            f"administrator if you need clarification.{note}\n\n"
            "EcoSync AI"
        )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [profile.user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send registration result email to %s", profile.user.email)
        return False

    profile.result_email_sent_at = timezone.now()
    profile.save(update_fields=["result_email_sent_at", "updated_at"])
    return True


def send_registration_result_email(profile):
    return send_account_status_change_email(profile)
