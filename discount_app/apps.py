from django.apps import AppConfig


class DiscountAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "discount_app"
    verbose_name = 'Discount Management'

    def ready(self):
        import discount_app.signals  # noqa
