from django.apps import AppConfig


class UtilisateursConfig(AppConfig):
    name = 'utilisateurs'

    def ready(self):
        import utilisateurs.signals  # Importer les signaux pour les connecter
