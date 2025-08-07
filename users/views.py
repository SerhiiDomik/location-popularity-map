from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiResponse


@extend_schema(
    summary="Реєстрація нового користувача",
    responses={201: RegisterSerializer},
)
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@extend_schema(
    summary="Вхід користувача (login)",
    request=LoginSerializer,
    responses={200: OpenApiResponse(description="Logged in successfully")},
)
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"detail": "Logged in successfully"}, status=status.HTTP_200_OK)


@extend_schema(
    summary="Вихід користувача (logout)",
    responses={200: OpenApiResponse(description="Logged out successfully")},
)
class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"detail": "Logged out successfully"}, status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Надіслати лист для скидання паролю",
    request=PasswordResetSerializer,
    responses={200: OpenApiResponse(description="Password reset email sent.")},
)
class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset email sent."}, status=status.HTTP_200_OK
        )


@extend_schema(
    summary="Підтвердити скидання паролю",
    request=PasswordResetConfirmSerializer,
    responses={200: OpenApiResponse(description="Password has been reset.")},
)
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password has been reset."}, status=status.HTTP_200_OK
        )
