from django.apps import AppConfig


class PaymentsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "payments_app"
    verbose_name = "Payments"

    def ready(self):
        import payments_app.signals  # noqa
