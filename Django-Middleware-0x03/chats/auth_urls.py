from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .auth import (
    CustomTokenObtainPairView,
    register_user,
    login_user,
    logout_user,
    user_profile,
)

urlpatterns = [
    # JWT Token endpoints
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Authentication endpoints
    path("register/", register_user, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
    path("profile/", user_profile, name="user_profile"),
]

# Available authentication endpoints:
# POST /api/auth/token/ - Obtain JWT token pair (access + refresh)
# POST /api/auth/token/refresh/ - Refresh access token using refresh token
# POST /api/auth/token/verify/ - Verify token validity
# POST /api/auth/register/ - Register new user and get tokens
# POST /api/auth/login/ - Login user and get tokens
# POST /api/auth/logout/ - Logout user (set offline status)
# GET /api/auth/profile/ - Get current user profile
