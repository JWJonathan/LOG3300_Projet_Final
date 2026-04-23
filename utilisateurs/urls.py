# utilisateurs/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    # Authentification
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Gestion du profil
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('profil/<int:pk>/', views.ProfilView.as_view(), name='profil-detail'),
    path('profil/update/', views.ProfilUpdateView.as_view(), name='profil-update'),
    path('profil/password/', views.CustomPasswordChangeView.as_view(), name='password-change'),
    
    # Gestion des utilisateurs (admin/modérateur)
    path('utilisateurs/', views.UtilisateurListView.as_view(), name='utilisateur-list'),
    path('utilisateurs/<int:pk>/', views.UtilisateurDetailView.as_view(), name='utilisateur-detail'),
    path('utilisateurs/<int:pk>/delete/', views.UtilisateurDeleteView.as_view(), name='utilisateur-delete'),
    path('utilisateurs/<int:pk>/toggle-status/', views.toggle_user_status, name='utilisateur-toggle-status'),
    
    # Réinitialisation de mot de passe
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='utilisateurs/password_reset.html',
             email_template_name='utilisateurs/password_reset_email.html',
             subject_template_name='utilisateurs/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='utilisateurs/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='utilisateurs/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='utilisateurs/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]