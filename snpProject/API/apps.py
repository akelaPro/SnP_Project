from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'API'

    # def ready(self):
    #     # Импортируем сигналы, чтобы они зарегистрировались
    #     import API.signals.github_auth