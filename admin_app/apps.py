from django.apps import AppConfig


class AdminAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "admin_app"
    verbose_name = "Admin Management"

    def ready(self):
        import admin_app.signals  # noqa
