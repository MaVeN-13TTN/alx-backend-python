import logging
from datetime import datetime
import os
from django.conf import settings


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
