from django.core.management.base import BaseCommand
from dashboard_app.models import DashboardWidget


class Command(BaseCommand):
    help = 'Creates default dashboard widgets for each user role'

    def handle(self, *args, **options):
        # Define default widgets
        default_widgets = [
            # Customer widgets
            {
                'name': 'Upcoming Bookings',
                'description': 'Shows your upcoming bookings',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/upcoming_bookings.html',
                'icon_class': 'fas fa-calendar-check',
                'user_type': 'customer',
            },
            {
                'name': 'Recent Bookings',
                'description': 'Shows your recent booking history',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/recent_bookings.html',
                'icon_class': 'fas fa-history',
                'user_type': 'customer',
            },
            {
                'name': 'Favorite Venues',
                'description': 'Shows your favorite venues',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/favorite_venues.html',
                'icon_class': 'fas fa-heart',
                'user_type': 'customer',
            },
            {
                'name': 'Recent Reviews',
                'description': 'Shows your recent reviews',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/recent_reviews.html',
                'icon_class': 'fas fa-star',
                'user_type': 'customer',
            },
            
            # Provider widgets
            {
                'name': "Today's Bookings",
                'description': 'Shows bookings for today',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/todays_bookings.html',
                'icon_class': 'fas fa-calendar-day',
                'user_type': 'provider',
            },
            {
                'name': 'Revenue Summary',
                'description': 'Shows revenue summary',
                'widget_type': 'stats',
                'template_name': 'dashboard_app/widgets/revenue_summary.html',
                'icon_class': 'fas fa-chart-line',
                'user_type': 'provider',
            },
            {
                'name': 'Top Services',
                'description': 'Shows your most popular services',
                'widget_type': 'chart',
                'template_name': 'dashboard_app/widgets/top_services.html',
                'icon_class': 'fas fa-chart-bar',
                'user_type': 'provider',
            },
            {
                'name': 'Recent Reviews',
                'description': 'Shows recent reviews for your venues',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/venue_reviews.html',
                'icon_class': 'fas fa-star',
                'user_type': 'provider',
            },
            
            # Admin widgets
            {
                'name': 'Platform Overview',
                'description': 'Shows platform-wide statistics',
                'widget_type': 'stats',
                'template_name': 'dashboard_app/widgets/platform_overview.html',
                'icon_class': 'fas fa-chart-pie',
                'user_type': 'admin',
            },
            {
                'name': 'User Statistics',
                'description': 'Shows user growth and activity',
                'widget_type': 'chart',
                'template_name': 'dashboard_app/widgets/user_statistics.html',
                'icon_class': 'fas fa-users',
                'user_type': 'admin',
            },
            {
                'name': 'Recent Bookings',
                'description': 'Shows recent bookings across the platform',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/admin_recent_bookings.html',
                'icon_class': 'fas fa-calendar-check',
                'user_type': 'admin',
            },
            {
                'name': 'System Health',
                'description': 'Shows system health metrics',
                'widget_type': 'stats',
                'template_name': 'dashboard_app/widgets/system_health.html',
                'icon_class': 'fas fa-heartbeat',
                'user_type': 'admin',
            },
            
            # Widgets for all users
            {
                'name': 'Quick Links',
                'description': 'Shows quick links to common actions',
                'widget_type': 'list',
                'template_name': 'dashboard_app/widgets/quick_links.html',
                'icon_class': 'fas fa-link',
                'user_type': 'all',
            },
        ]
        
        # Create widgets
        created_count = 0
        for widget_data in default_widgets:
            widget, created = DashboardWidget.objects.get_or_create(
                name=widget_data['name'],
                defaults=widget_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created widget: {widget.name}"))
            else:
                self.stdout.write(f"Widget already exists: {widget.name}")
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new widgets"))
