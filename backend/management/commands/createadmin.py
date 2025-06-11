from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = "Creates a superuser if it doesn't exist"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = "mattia"
        email = "mattia@whoppah.com"
        password = os.environ.get("ADMIN_PASSWORD", "whoppah123")

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            self.stdout.write(self.style.SUCCESS("✅ Admin user created"))
        else:
            self.stdout.write("ℹ️ Admin user already exists")
