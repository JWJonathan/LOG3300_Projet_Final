# utilisateurs/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profil
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import AuditLog

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil lors de la création d'un utilisateur"""
    if created:
        Profil.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil lors de la sauvegarde de l'utilisateur"""
    instance.profil.save()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Enregistre les connexions dans le journal d'audit"""
    AuditLog.objects.create(
        user=user,
        action='login',
        description=f"Connexion réussie",
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Enregistre les déconnexions dans le journal d'audit"""
    if user:  # user peut être None si la session a expiré
        AuditLog.objects.create(
            user=user,
            action='logout',
            description=f"Déconnexion",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip