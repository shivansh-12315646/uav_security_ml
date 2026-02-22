import os
from django.core.management.base import BaseCommand
from core.models import User


class Command(BaseCommand):
    help = 'Create default admin user'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@uavsecurity.com')
        password = os.getenv('ADMIN_PASSWORD', 'admin123')

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"Admin user '{username}' already exists.")
            return

        user = User.objects.create_superuser(username=username, email=email, password=password)
        user.role = 'admin'
        user.save()
        self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created."))
