import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ess.settings')
django.setup()

from authentication.models import Admin
import bcrypt

username = 'admin'
user_id = 'admin'
email = 'thowfeekrahman123@gmail.com'
raw_password = 'admin'  
hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

admin_user = Admin(username=username, user_id=user_id, email=email, password=hashed_password)
admin_user.save()
print("Admin created")