# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response({"detail": "Logged in successfully"}, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Logged out successfully"}, status=status.HTTP_200_OK)
