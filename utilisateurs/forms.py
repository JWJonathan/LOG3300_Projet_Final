# utilisateurs/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Profil
import re

class CustomUserCreationForm(UserCreationForm):
    """
    Formulaire d'inscription personnalisé avec validation avancée
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'})
    )
    
    # Validation du mot de passe personnalisée
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="""
        <ul>
            <li>Au moins 8 caractères</li>
            <li>Au moins une lettre majuscule</li>
            <li>Au moins une lettre minuscule</li>
            <li>Au moins un chiffre</li>
            <li>Au moins un caractère spécial</li>
        </ul>
        """
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
        }
    
    def clean_password1(self):
        """Validation avancée du mot de passe"""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")
        
        return password
    
    def clean_email(self):
        """Vérifie que l'email n'est pas déjà utilisé"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """
    Formulaire de mise à jour des informations utilisateur de base
    """
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfilUpdateForm(forms.ModelForm):
    """
    Formulaire de mise à jour du profil étendu
    """
    date_naissance = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = Profil
        fields = ('bio', 'avatar', 'telephone', 'adresse', 'date_naissance', 'site_web')
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+33...'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'site_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


class AdminUserUpdateForm(forms.ModelForm):
    """
    Formulaire d'administration pour modifier les utilisateurs
    """
    role = forms.ChoiceField(
        choices=Profil.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_active = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'profil'):
            self.fields['role'].initial = self.instance.profil.role
    
    def save(self, commit=True):
        user = super().save(commit=commit)
        if hasattr(user, 'profil'):
            user.profil.role = self.cleaned_data['role']
            user.profil.save()
        return user