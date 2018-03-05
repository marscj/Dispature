from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def verifycode_validate(code):
    from main.models import Setting

    qs = Setting.objects.all()[0]

    if not qs or qs.verifycode != code:
        raise ValidationError(
            _('the code %(code)s does not exist'),
            params={'code': code},
        )
