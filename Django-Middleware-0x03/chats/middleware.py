import logging
from datetime import datetime
import os
from django.conf import settings
from django.http import HttpResponseForbidden


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
