# utilisateurs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Profil, AuditLog
from django.contrib.auth.views import LoginView, LogoutView
from .forms import (
    CustomUserCreationForm, UserUpdateForm, ProfilUpdateForm,
    AdminUserUpdateForm
)
import json
from django.utils import timezone

class CustomLoginView(LoginView):
    """
    Vue de connexion personnalisée avec journal d'audit
    """
    template_name = 'utilisateurs/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        
        # Journal d'audit
        AuditLog.objects.create(
            user=user,
            action='login',
            description=f"Connexion réussie",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_redirect_url(self):
        """Redirige les utilisateurs vers la page d'accueil après la connexion"""
        return reverse_lazy('recipes:recipe_list')

class RegisterView(CreateView):
    """
    Vue d'inscription personnalisée
    """
    form_class = CustomUserCreationForm
    template_name = 'utilisateurs/register.html'
    success_url = reverse_lazy('users:utilisateur-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        login(self.request, user)
        
        # Journal d'audit
        AuditLog.objects.create(
            user=user,
            action='create',
            description="Création du compte utilisateur",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, f"Bienvenue {user.username} ! Votre compte a été créé avec succès.")
        return response
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_redirect_url(self):
        """Redirige les utilisateurs vers la page d'accueil après la connexion"""
        return reverse_lazy('recipes:recipe_list')


class CustomLogoutView(LogoutView):
    """
    Vue de déconnexion personnalisée avec journal d'audit
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        
        # Journal d'audit
        if user.is_authenticated:
            AuditLog.objects.create(
                user=user,
                action='logout',
                description=f"Déconnexion",
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    

class ProfilView(LoginRequiredMixin, DetailView):
    """
    Vue du profil utilisateur
    """
    model = User
    template_name = 'utilisateurs/profil.html'
    context_object_name = 'utilisateur'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if 'pk' in self.kwargs and self.kwargs['pk'] != user.pk:
            # Si l'utilisateur essaie d'accéder au profil d'un autre utilisateur
            if not user.profil.can_manage_users():
                messages.error(request, "Vous n'avez pas la permission d'accéder à ce profil.")
                return redirect('profil')
        return super().dispatch(request, *args, **kwargs)
    
    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return get_object_or_404(User, pk=self.kwargs['pk'])
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        # Statistiques pour l'administrateur
        if self.request.user.profil.can_manage_users():
            context['audit_logs'] = AuditLog.objects.filter(user=user)[:5]
            context['total_items'] = user.recipes.count() if hasattr(user, 'recipes') else 0
        
        return context


# utilisateurs/views.py - Version corrigée de ProfilUpdateView

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

class ProfilUpdateView(LoginRequiredMixin, TemplateView):
    """
    Mise à jour du profil utilisateur
    """
    template_name = 'utilisateurs/profil_update.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        context['user_form'] = UserUpdateForm(instance=user)
        context['profil_form'] = ProfilUpdateForm(instance=user.profil)
        
        return context
    
    def post(self, request, *args, **kwargs):
        user = request.user
        user_form = UserUpdateForm(request.POST, instance=user)
        profil_form = ProfilUpdateForm(
            request.POST, 
            request.FILES, 
            instance=user.profil
        )
        
        if user_form.is_valid() and profil_form.is_valid():
            user_form.save()
            profil_form.save()
            
            # Journal d'audit
            AuditLog.objects.create(
                user=request.user,
                action='update',
                description="Mise à jour du profil",
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            messages.success(request, "✅ Votre profil a été mis à jour avec succès !")
            return redirect('profil')
        else:
            messages.error(request, "❌ Erreur lors de la mise à jour. Veuillez corriger les erreurs.")
            context = self.get_context_data()
            context['user_form'] = user_form
            context['profil_form'] = profil_form
            return self.render_to_response(context)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class UtilisateurListView(LoginRequiredMixin, ListView):
    """
    Liste des utilisateurs (avec pagination et recherche)
    """
    model = User
    template_name = 'utilisateurs/utilisateur_list.html'
    context_object_name = 'utilisateurs'
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.profil.can_manage_users():
            messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
            return redirect('recipes:recipe_list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = User.objects.select_related('profil').annotate(
            items_count=Count('recipes') if hasattr(User, 'recipes') else Count('id')
        ).order_by('-date_joined')
        
        # Filtres de recherche
        search = self.request.GET.get('search', '')
        role = self.request.GET.get('role', '')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(profil__role=role)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        context['roles'] = Profil.ROLE_CHOICES
        
        # Statistiques globales (pour admin)
        if self.request.user.profil.can_manage_users():
            context['total_users'] = User.objects.count()
            context['active_users'] = User.objects.filter(is_active=True).count()
            context['new_users_today'] = User.objects.filter(
                date_joined__date=timezone.now().date()
            ).count()
        
        return context


class UtilisateurDetailView(LoginRequiredMixin, DetailView):
    """
    Vue détaillée d'un utilisateur (admin/modérateur uniquement)
    """
    model = User
    template_name = 'utilisateurs/utilisateur_detail.html'
    context_object_name = 'utilisateur'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.profil.can_manage_users():
            messages.error(request, "Vous n'avez pas la permission d'accéder à ce profil.")
            return redirect('profil')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        
        context['audit_logs'] = AuditLog.objects.filter(user=user)[:20]
        context['recent_actions'] = AuditLog.objects.filter(user=user)[:5]
        context['total_items'] = user.recipes.count() if hasattr(user, 'recipes') else 0
        
        return context


class UtilisateurDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Suppression d'un utilisateur (admin uniquement)
    """
    model = User
    template_name = 'utilisateurs/utilisateur_confirm_delete.html'
    success_url = reverse_lazy('users:utilisateur-list')
    
    def test_func(self):
        user_to_delete = self.get_object()
        return (self.request.user.is_superuser or 
                self.request.user.profil.role == 'admin') and \
               user_to_delete != self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Journal d'audit
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            description=f"Suppression de l'utilisateur {user.username}",
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, f"L'utilisateur {user.username} a été supprimé.")
        return super().delete(request, *args, **kwargs)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Changement de mot de passe personnalisé
    """
    template_name = 'utilisateurs/password_change.html'
    success_url = reverse_lazy('profil')
    
    def form_valid(self, form):
        # Journal d'audit
        AuditLog.objects.create(
            user=self.request.user,
            action='password_change',
            description="Changement du mot de passe",
            ip_address=self.get_client_ip(),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(self.request, "Votre mot de passe a été changé avec succès !")
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


@login_required
@require_POST
def toggle_user_status(request, pk):
    """
    Vue AJAX pour activer/désactiver un utilisateur (admin uniquement)
    """
    if not request.user.profil.can_manage_users():
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user = get_object_or_404(User, pk=pk)
    data = json.loads(request.body)
    
    if user != request.user:
        user.is_active = data.get('is_active', not user.is_active)
        user.save()
        
        AuditLog.objects.create(
            user=request.user,
            action='update',
            description=f"{'Activation' if user.is_active else 'Désactivation'} de l'utilisateur {user.username}",
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f"Utilisateur {'activé' if user.is_active else 'désactivé'}"
        })
    
    return JsonResponse({'error': 'Cannot modify yourself'}, status=400)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip