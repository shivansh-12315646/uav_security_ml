from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Initialize ML service on app startup."""
        try:
            from services.ml_service import ml_service
            ml_service.load_models()
        except Exception:
            pass
