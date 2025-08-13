import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ess.settings')
django.setup()

from authentication.models import ManagingDirector
import bcrypt

username = 'md'
user_id = 'md'
email = 'thowfeekrahman123@gmail.com'
raw_password = 'Thowfeek2000'  
hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

md_user = ManagingDirector(username=username, user_id=user_id, email=email, password=hashed_password)
md_user.save()
print("MD created")