from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """
    Django app configuration for the messaging app.

    This configuration ensures that the signals are properly
    registered when the app is ready.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "messaging"
    verbose_name = "Messaging System"

    def ready(self):
        """
        Called when the app is ready.

        This method imports the signals module to ensure that
        all signal handlers are registered with Django's
        signal dispatcher.
        """
        try:
            # Import signals to register them
            import messaging.signals

            print("Messaging app signals registered successfully")
        except ImportError as e:
            print(f"Error importing messaging signals: {e}")
            pass
