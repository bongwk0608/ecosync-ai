from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserProfile
from .permissions import IsApprovedUser
from .serializers import LoginSerializer, RegisterSerializer


def user_payload(user):
    profile = getattr(user, "ecosync_profile", None)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": profile.full_name if profile else user.get_full_name(),
        "organization": profile.organization if profile else "",
        "role": profile.role if profile else "",
        "approval_status": profile.approval_status if profile else "approved",
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if not settings.ALLOW_PUBLIC_REGISTRATION:
            return Response(
                {"detail": "Public registration is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_user_model().objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=data["full_name"],
            is_active=False,
        )
        profile = UserProfile.objects.create(
            user=user,
            full_name=data["full_name"],
            organization=data["organization"],
            role=data["role"],
            approval_status="pending",
        )
        group, _created = Group.objects.get_or_create(name=settings.DEFAULT_REGISTERED_USER_GROUP)
        user.groups.add(group)
        return Response(
            {
                "detail": "Registration submitted. You will receive an email after admin review.",
                "user": user_payload(user),
                "application_id": profile.id,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if not user:
            candidate = get_user_model().objects.filter(
                username=serializer.validated_data["username"]
            ).first()
            if not candidate or not candidate.check_password(serializer.validated_data["password"]):
                return Response(
                    {"detail": "Invalid username or password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user = candidate

        profile = getattr(user, "ecosync_profile", None)
        if not user.is_staff and (not profile or profile.approval_status != "approved"):
            approval_status = profile.approval_status if profile else "pending"
            return Response(
                {
                    "detail": f"Application {approval_status}. Please check your email or wait for admin approval.",
                    "approval_status": approval_status,
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if not user.is_active and not user.is_staff:
            return Response(
                {"detail": "Account is not active."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user": user_payload(user)})


class MeView(APIView):
    permission_classes = [IsApprovedUser]

    def get(self, request):
        return Response(user_payload(request.user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({"detail": "Logged out."})
