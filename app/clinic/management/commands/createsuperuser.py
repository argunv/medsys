"""Generate a superuser if none exist."""
from os import getenv

from clinic.models import CustomUser
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

load_dotenv()


class Command(BaseCommand):
    """Create a superuser if none exist."""

    help = 'Create a superuser if none exist'

    def handle(self, *args, **options):  # noqa: WPS110
        """Create a superuser if none exist.

        Args:
            args: Not used.
            options: Not used.
        """
        username = getenv('SUPERUSER_USERNAME', 'admin')
        password = getenv('SUPERUSER_PASSWORD', 'admin')
        email = getenv('SUPERUSER_EMAIL', 'root@example.com')

        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Superuser "{username}" already exists'))
        CustomUser.objects.create_superuser(username=username, password=password, email=email)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created'))
