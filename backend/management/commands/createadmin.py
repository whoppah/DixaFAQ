#backend/management/commands/createadmin.py
# faq_api/management/commands/createadmin.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Creates an admin (superuser) if it doesn't already exist"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD")

        if not password:
            self.stderr.write(self.style.ERROR("❌ ADMIN_PASSWORD environment variable is required."))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"ℹ️ Admin user '{username}' already exists.")
        else:
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"✅ Superuser '{username}' created successfully."))
