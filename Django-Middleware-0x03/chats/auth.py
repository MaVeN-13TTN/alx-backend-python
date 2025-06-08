from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT Token serializer that includes additional user information
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["email"] = user.email
        token["user_id"] = str(user.user_id)
        token["is_staff"] = user.is_staff

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user information to response
        data["user"] = {
            "user_id": str(self.user.user_id),
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "is_online": self.user.is_online,
            "profile_picture": self.user.profile_picture,
        }

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT Token view with additional user information
    """

    serializer_class = CustomTokenObtainPairSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user and return JWT tokens
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        # Generate JWT tokens for the new user
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access_token = refresh.access_token

        return Response(
            {
                "user": {
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user with username/email and password, return JWT tokens
    """
    username_or_email = request.data.get("username") or request.data.get("email")
    password = request.data.get("password")

    if not username_or_email or not password:
        return Response(
            {"error": "Username/email and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Try to find user by username or email
    try:
        if "@" in username_or_email:
            user = User.objects.get(email=username_or_email)
            username = user.username
        else:
            username = username_or_email
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    # Authenticate user
    user = authenticate(username=username, password=password)

    if user:
        # Update user online status
        user.is_online = True
        user.save()

        # Generate JWT tokens
        refresh = CustomTokenObtainPairSerializer.get_token(user)
        access_token = refresh.access_token

        return Response(
            {
                "user": {
                    "user_id": str(user.user_id),
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_online": user.is_online,
                    "profile_picture": user.profile_picture,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(access_token),
                },
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def logout_user(request):
    """
    Logout user by setting online status to False
    """
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.save()

        return Response(
            {"message": "Successfully logged out"}, status=status.HTTP_200_OK
        )

    return Response(
        {"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["GET"])
def user_profile(request):
    """
    Get current user's profile information
    """
    if request.user.is_authenticated:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(
        {"error": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED
    )
