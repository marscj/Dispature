from django.dispatch import receiver
from django.db.models.signals import post_migrate
from .models import Setting


def init_db(sender, **kwargs):
    if sender.name == 'main':
        if not Setting.objects.exists():
            Setting.objects.create()


post_migrate.connect(init_db)
