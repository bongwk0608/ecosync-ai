from __future__ import annotations

from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ("program_manager", "Program manager"),
        ("ecosystem_partner", "Ecosystem partner"),
        ("admin_operator", "Admin operator"),
    ]
    APPROVAL_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ecosync_profile",
    )
    full_name = models.CharField(max_length=150)
    organization = models.CharField(max_length=150)
    role = models.CharField(max_length=40, choices=ROLE_CHOICES)
    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="pending",
    )
    admin_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_ecosync_profiles",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    result_email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.user.username}) - {self.approval_status}"
