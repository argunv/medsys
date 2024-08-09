from django.apps import AppConfig


class ClinicConfig(AppConfig):
    """AppConfig subclass for the 'clinic' app.

    Args:
        AppConfig: The base class for application configuration.

    Attributes:
        default_auto_field (str): The default auto field to use for models in this app.
        name (str): The name of the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "clinic"

    def ready(self) -> None:
        """Import signals when the app is ready."""
        import clinic.signals
