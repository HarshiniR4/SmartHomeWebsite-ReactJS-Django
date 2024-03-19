from django.apps import AppConfig


class ShemsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shems_app'
    def ready(self):
        import shems_project.signals