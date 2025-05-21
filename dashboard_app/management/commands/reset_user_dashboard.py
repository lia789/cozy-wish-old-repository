from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from accounts_app.models import CustomUser
from dashboard_app.models import DashboardWidget, UserWidget, DashboardPreference


class Command(BaseCommand):
    help = 'Resets a user\'s dashboard to the default configuration'

    def add_arguments(self, parser):
        parser.add_argument('user_email', type=str, help='Email of the user whose dashboard should be reset')

    def handle(self, *args, **options):
        user_email = options['user_email']
        
        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            raise CommandError(f'User with email {user_email} does not exist')
        
        # Delete existing user widgets
        UserWidget.objects.filter(user=user).delete()
        
        # Reset dashboard preferences
        DashboardPreference.objects.filter(user=user).delete()
        preference = DashboardPreference.objects.create(user=user)
        
        # Determine user type
        if user.is_customer:
            user_type = 'customer'
        elif user.is_service_provider:
            user_type = 'provider'
        elif user.is_staff:
            user_type = 'admin'
        else:
            user_type = None
        
        # Add default widgets for the user's role
        if user_type:
            widgets = DashboardWidget.objects.filter(
                Q(user_type=user_type) | Q(user_type='all'),
                is_active=True
            )
            
            for i, widget in enumerate(widgets):
                UserWidget.objects.create(
                    user=user,
                    widget=widget,
                    position=i,
                    is_visible=True
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully reset dashboard for {user.email} ({user_type}). '
                f'Added {widgets.count()} widgets.'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'User {user.email} does not have a specific role. No widgets were added.'
            ))
