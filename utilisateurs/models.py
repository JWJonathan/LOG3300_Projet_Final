# utilisateurs/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import os

class Profil(models.Model):
    """
    Extension du modèle User de Django pour ajouter des champs personnalisés
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('moderateur', 'Modérateur'),
        ('membre', 'Membre'),
        ('visiteur', 'Visiteur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biographie")
    avatar = models.ImageField(
        upload_to='avatars/', 
        default='avatars/default.png',
        blank=True,
        verbose_name="Photo de profil"
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='membre',
        verbose_name="Rôle"
    )
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    adresse = models.TextField(max_length=200, blank=True, verbose_name="Adresse")
    date_naissance = models.DateField(null=True, blank=True, verbose_name="Date de naissance")
    site_web = models.URLField(max_length=200, blank=True, verbose_name="Site web")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    email_verifie = models.BooleanField(default=False, verbose_name="Email vérifié")
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ['-user__date_joined']
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Redimensionne l'avatar lors de l'enregistrement"""
        super().save(*args, **kwargs)
        
        if self.avatar and os.path.exists(self.avatar.path):
            img = Image.open(self.avatar.path)
            
            # Redimensionner si l'image est trop grande
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur"""
        return self.role == 'admin' or self.user.is_superuser
    
    def can_manage_users(self):
        """Vérifie si l'utilisateur peut gérer d'autres utilisateurs"""
        return self.role in ['admin', 'moderateur'] or self.user.is_superuser


class AuditLog(models.Model):
    """
    Journal d'audit pour suivre les actions importantes des utilisateurs
    """
    ACTION_TYPES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('login', 'Connexion'),
        ('logout', 'Déconnexion'),
        ('password_change', 'Changement de mot de passe'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Journal d'audit"
        verbose_name_plural = "Journaux d'audit"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.timestamp}"