from django.apps import AppConfig


class BookingCartAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "booking_cart_app"

    def ready(self):
        import booking_cart_app.signals  # noqa
