import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("This password is too short. It must contain at least 8 characters."))

        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("This password must contain at least one uppercase letter."))

        if not re.search(r'[a-z]', password):
            raise ValidationError(_("This password must contain at least one lowercase letter."))

        if not re.search(r'[0-9]', password):
            raise ValidationError(_("This password must contain at least one digit."))

        if not re.search(r'[@$!%*?&]', password):
            raise ValidationError(_("This password must contain at least one special character."))

        common_passwords = ['password', '12345678', 'qwerty', 'letmein']
        if password.lower() in common_passwords:
            raise ValidationError(_("This password is too common."))

    def get_help_text(self):
        return _("Your password must contain at least 8 characters, including uppercase, lowercase, digit, and special character.")
