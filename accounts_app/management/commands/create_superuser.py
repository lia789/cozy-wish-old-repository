from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with the specified email and password'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default='pse.coliahabib@gmail.com',
            help='Email for the superuser'
        )
        parser.add_argument(
            '--password',
            default='123',
            help='Password for the superuser'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Superuser with email {email} already exists.'))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser created with email: {email}'))
