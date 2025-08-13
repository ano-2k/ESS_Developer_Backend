import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ess.settings')
django.setup()

from django.contrib.auth.models import User

username = 'superadmin'
email = 'superadmin@company.com'
password = 'superadmin'
first_name = 'Super'
last_name = 'Admin'

if User.objects.filter(username=username).exists():
    print(f"Super Admin '{username}' already exists!")
    existing_user = User.objects.get(username=username)
    print(f"Email: {existing_user.email}")
    print(f"Is Superuser: {existing_user.is_superuser}")
    print(f"Is Active: {existing_user.is_active}")
else:
    superuser = User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print("Super Admin created successfully!")
    print(f"Username: {username}")
    print(f"Email: {email}")
