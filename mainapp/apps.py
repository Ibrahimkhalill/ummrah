from django.apps import AppConfig

class MainappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mainapp"

    def ready(self):
        # Import and start the scheduler when the app is ready
        from .scheduler import start_scheduler
        start_scheduler()