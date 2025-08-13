import os
import django
import bcrypt

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ess.settings')
django.setup()

from authentication.models import SuperAdmin

username = 'superadmin'
user_id = 'superadmin'
email = 'superadmin@company.com'
raw_password = 'superadmin'

hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

superadmin_user = SuperAdmin(username=username, user_id=user_id, email=email, password=hashed_password)
superadmin_user.save()
print("SuperAdmin created successfully")
