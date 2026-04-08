from django.shortcuts import render

from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, UserSerializer
from .utils import get_tokens_for_user
from .permissions import IsAdmin, IsManager, IsAdminOrManager


# RegisterView
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response({
                "user": UserSerializer(user).data,
                "tokens": tokens
            },status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=400)


# LoginView
class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)

            return Response({
                "user": UserSerializer(user).data,
                "tokens": tokens
            })

        return Response({"error": "Invalid credentials"}, status=401)


# ProfileView
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


# Refresh Token View
class RefreshView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)

            return Response({
                "access": str(token.access_token)
            })
        except:
            return Response({"error": "Invalid token"}, status=400)


# Logout (Blacklist) View
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out"}, status=200)
        except:
            return Response({"error": "Invalid token"}, status=400)


# Change Password View
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Wrong password"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated"}, status=200)


# Admin Only API
class AdminOnlyView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response({"message": "Admin access"})


# Manager Only API
class ManagerOnlyView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        return Response({"message": "Manager access"})


# Admin + Manager API
class DashboardView(APIView):
    permission_classes = [IsAdminOrManager]

    def get(self, request):
        return Response({"message": "Admin or Manager access"})