import logging
from datetime import datetime, timedelta
import os
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponse
from collections import defaultdict
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class RequestLoggingMiddleware:
    """
    Middleware to log each user's requests to a file.
    Logs timestamp, user, and request path for each incoming request.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.

        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

        # Set up logging configuration
        self.setup_logger()

    def setup_logger(self):
        """
        Configure the logger to write to requests.log file.
        """
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(settings.BASE_DIR, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure logger
        self.logger = logging.getLogger("request_logger")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create file handler
        log_file = os.path.join(settings.BASE_DIR, "requests.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter("%(message)s")
        file_handler.setFormatter(formatter)

        # Add handler to logger
        self.logger.addHandler(file_handler)

        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False

    def __call__(self, request):
        """
        Process the request and log user information.

        Args:
            request: The Django request object

        Returns:
            The response from the next middleware or view
        """
        # Get user information
        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else "Anonymous"
        )

        # Create log message
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        # Log the request
        self.logger.info(log_message)

        # Continue processing the request
        response = self.get_response(request)

        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the messaging app during certain hours.
    Denies access outside of 6 AM to 9 PM with 403 Forbidden response.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.

        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and check if access is allowed based on current time.

        Args:
            request: The Django request object

        Returns:
            403 Forbidden response if outside allowed hours, otherwise continues processing
        """
        # Get current hour (24-hour format)
        current_hour = datetime.now().hour

        # Debug: Print current time and hour for testing
        print(f"DEBUG: Current time: {datetime.now()}, Hour: {current_hour}")

        # Define allowed hours: 6 AM (6) to 9 PM (21)
        start_hour = 6  # 6 AM
        end_hour = 21  # 9 PM

        # Check if current time is outside allowed hours
        if current_hour < start_hour or current_hour >= end_hour:
            print(
                f"DEBUG: Access BLOCKED - Time {current_hour} is outside allowed hours {start_hour}-{end_hour}"
            )
            # Return 403 Forbidden response with error message
            return HttpResponseForbidden(
                "Access to the messaging app is restricted. "
                "Please access between 6:00 AM and 9:00 PM."
            )

        print(
            f"DEBUG: Access ALLOWED - Time {current_hour} is within allowed hours {start_hour}-{end_hour}"
        )
        # Continue processing the request if within allowed hours
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    """
    Middleware to limit the number of chat messages (POST requests) a user can send
    within a certain time window based on their IP address.
    Implements rate limiting: 5 messages per minute per IP address.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.

        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

        # Rate limiting configuration
        self.max_requests = 5  # Maximum number of requests
        self.time_window = 60  # Time window in seconds (1 minute)

        # Use defaultdict to store request counts per IP
        # Format: {ip_address: [timestamp1, timestamp2, ...]}
        self.ip_requests = defaultdict(list)

    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.

        Args:
            request: The Django request object

        Returns:
            str: The client's IP address
        """
        # Check for forwarded IP (in case of proxy/load balancer)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def clean_old_requests(self, ip_address):
        """
        Remove request timestamps that are outside the current time window.

        Args:
            ip_address: The IP address to clean
        """
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(seconds=self.time_window)

        # Keep only timestamps within the time window
        self.ip_requests[ip_address] = [
            timestamp
            for timestamp in self.ip_requests[ip_address]
            if timestamp > cutoff_time
        ]

    def __call__(self, request):
        """
        Process the request and check rate limiting for POST requests.

        Args:
            request: The Django request object

        Returns:
            429 Too Many Requests response if limit exceeded, otherwise continues processing
        """
        # Only apply rate limiting to POST requests (messages)
        if request.method == "POST":
            # Get client IP address
            client_ip = self.get_client_ip(request)
            current_time = datetime.now()

            # Clean old requests for this IP
            self.clean_old_requests(client_ip)

            # Check if IP has exceeded the rate limit
            request_count = len(self.ip_requests[client_ip])

            if request_count >= self.max_requests:
                # Rate limit exceeded - return 429 Too Many Requests
                response = HttpResponse(
                    f"Rate limit exceeded. You can only send {self.max_requests} "
                    f"messages per {self.time_window} seconds. Please try again later.",
                    status=429,
                    content_type="text/plain",
                )
                return response

            # Add current request timestamp
            self.ip_requests[client_ip].append(current_time)

            # Debug logging
            print(
                f"DEBUG: IP {client_ip} has sent {request_count + 1}/{self.max_requests} POST requests in the last {self.time_window} seconds"
            )

        # Continue processing the request
        response = self.get_response(request)
        return response


class RolePermissionMiddleware:
    """
    Middleware to check user roles and restrict access to specific actions.
    Only allows admin (superuser) and moderator (staff) users to access certain endpoints.
    Returns 403 Forbidden for users without proper permissions.
    """

    def __init__(self, get_response):
        """
        Initialize the middleware with the get_response callable.

        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response

        # Define protected endpoints that require admin/moderator access
        self.protected_paths = [
            "/api/conversations/",  # Managing conversations
            "/api/users/",  # User management
            "/admin/",  # Django admin
        ]

        # Define methods that require role-based access
        self.protected_methods = ["POST", "PUT", "PATCH", "DELETE"]

    def is_protected_endpoint(self, request):
        """
        Check if the current request is accessing a protected endpoint.

        Args:
            request: The Django request object

        Returns:
            bool: True if the endpoint requires role-based protection
        """
        # Check if path starts with any protected path
        for protected_path in self.protected_paths:
            if request.path.startswith(protected_path):
                return True

        # Also protect write operations on API endpoints
        if (
            request.path.startswith("/api/")
            and request.method in self.protected_methods
        ):
            return True

        return False

    def has_required_permission(self, user):
        """
        Check if the user has the required permissions (admin or moderator).

        Args:
            user: The Django user object

        Returns:
            bool: True if user is admin (superuser) or moderator (staff)
        """
        if not user or not user.is_authenticated:
            return False

        # Admin (superuser) has full access
        if user.is_superuser:
            return True

        # Moderator (staff) has access
        if user.is_staff:
            return True

        return False

    def __call__(self, request):
        """
        Process the request and check role-based permissions.

        Args:
            request: The Django request object

        Returns:
            403 Forbidden response if user lacks required permissions,
            otherwise continues processing
        """
        # Check if this is a protected endpoint
        if self.is_protected_endpoint(request):
            # Get the user from the request
            user = getattr(request, "user", None)

            # Debug: Log user details
            print(f"DEBUG: User object: {user}")
            print(f"DEBUG: User type: {type(user)}")
            print(
                f"DEBUG: User authenticated: {getattr(user, 'is_authenticated', False)}"
            )
            if user and hasattr(user, "username"):
                print(f"DEBUG: Username: {user.username}")
                print(f"DEBUG: is_superuser: {getattr(user, 'is_superuser', False)}")
                print(f"DEBUG: is_staff: {getattr(user, 'is_staff', False)}")

            # Check if user has required permissions
            if not self.has_required_permission(user):
                # Log the access attempt
                user_info = (
                    user.username if user and user.is_authenticated else "Anonymous"
                )
                print(
                    f"DEBUG: Access DENIED - User '{user_info}' attempted to access protected endpoint: {request.method} {request.path}"
                )

                # Return 403 Forbidden response
                return HttpResponseForbidden(
                    "Access denied. This action requires admin or moderator privileges. "
                    "Please contact an administrator if you believe this is an error."
                )

            # Log successful access for admin/moderator
            username = (
                user.username if user and hasattr(user, "username") else "Unknown"
            )
            print(
                f"DEBUG: Access GRANTED - Admin/Moderator '{username}' accessing: {request.method} {request.path}"
            )

        # Continue processing the request
        response = self.get_response(request)
        return response
