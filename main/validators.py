from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def verifycode_validate(code):
    import main.models as main
    
    qs = main.Company.objects.filter(verifycode=code)

    if not qs:
        raise ValidationError(
            _('the code %(code)s does not exist'),
            params={'code': code},
        )
