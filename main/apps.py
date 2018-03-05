from django.apps import AppConfig


class MainConfig(AppConfig):
    name = 'main'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import main.handlers