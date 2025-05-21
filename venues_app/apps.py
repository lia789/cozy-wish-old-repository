from django.apps import AppConfig


class VenuesAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "venues_app"
    verbose_name = "Venues"

    def ready(self):
        # Temporarily disabled signals
        # import venues_app.signals  # noqa
        pass
