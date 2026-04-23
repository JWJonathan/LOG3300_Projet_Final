# recipes/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Q

from .models import Recipe, Category
from .forms import RecipeForm, CategoryForm


# -------------------------------
# VUES PUBLIQUES (consultation)
# -------------------------------

class RecipeListView(ListView):
    """
    Page d'accueil : affiche toutes les recettes, avec possibilité de recherche et filtrage par catégorie.
    Accessible à tous (utilisateurs authentifiés ou non).
    """
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 9  # Pagination pour éviter une page trop longue

    def get_queryset(self):
        queryset = super().get_queryset().select_related('author', 'category')
        # Recherche par mot-clé dans le titre ou la description
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(description__icontains=search_query)
            )
        # Filtrage par catégorie
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class RecipeDetailView(DetailView):
    """
    Affiche le détail complet d'une recette.
    Accessible à tous.
    """
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

    def get_queryset(self):
        # Optimisation : précharge l'auteur et la catégorie
        return super().get_queryset().select_related('author', 'category')


# ---------------------------------
# VUES NÉCESSITANT UNE CONNEXION
# ---------------------------------

class RecipeCreateView(LoginRequiredMixin, CreateView):
    """
    Permet à un utilisateur connecté de créer une nouvelle recette.
    L'auteur est automatiquement défini comme l'utilisateur courant.
    """
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def form_valid(self, form):
        # Associe l'utilisateur connecté comme auteur avant sauvegarde
        form.instance.author = self.request.user
        messages.success(self.request, "Votre recette a été créée avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('recipes:recipe_detail', kwargs={'slug': self.object.slug})


class RecipeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Permet de modifier une recette existante.
    Seul l'auteur de la recette y a accès.
    """
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def test_func(self):
        """Vérifie que l'utilisateur connecté est bien l'auteur de la recette."""
        recipe = self.get_object()
        return self.request.user == recipe.author

    def handle_no_permission(self):
        """Redirige avec un message d'erreur si l'utilisateur n'est pas autorisé."""
        messages.error(self.request, "Vous n'avez pas la permission de modifier cette recette.")
        return redirect('recipes:recipe_detail', slug=self.get_object().slug)

    def form_valid(self, form):
        messages.success(self.request, "La recette a été mise à jour avec succès !")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('recipes:recipe_detail', kwargs={'slug': self.object.slug})


class RecipeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Permet de supprimer une recette.
    Seul l'auteur peut y accéder.
    """
    model = Recipe
    template_name = 'recipes/recipe_confirm_delete.html'
    success_url = reverse_lazy('recipes:recipe_list')

    def test_func(self):
        recipe = self.get_object()
        return self.request.user == recipe.author

    def handle_no_permission(self):
        messages.error(self.request, "Vous n'avez pas la permission de supprimer cette recette.")
        return redirect('recipes:recipe_detail', slug=self.get_object().slug)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "La recette a été supprimée.")
        return super().delete(request, *args, **kwargs)


# ---------------------------------
# VUES SPÉCIFIQUES UTILISATEUR
# ---------------------------------

class UserRecipeListView(LoginRequiredMixin, ListView):
    """
    Affiche la liste des recettes créées par l'utilisateur connecté.
    (Mon Livre de Recettes)
    """
    model = Recipe
    template_name = 'recipes/user_recipe_list.html'
    context_object_name = 'recipes'
    paginate_by = 12

    def get_queryset(self):
        return Recipe.objects.filter(author=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_recipes'] = self.get_queryset().count()
        return context


# ---------------------------------
# VUES POUR LES CATÉGORIES (Optionnel)
# ---------------------------------

class CategoryDetailView(DetailView):
    """
    Affiche les recettes appartenant à une catégorie donnée.
    """
    model = Category
    template_name = 'recipes/category_detail.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recipes'] = self.object.recipes.all().order_by('-created_at')
        return context
    
class CategoryCreate(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'recipes/categorie_form.html'
    success_url = reverse_lazy('recipes:recipe_list')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_superuser:
            messages.error(request, "Vous n'avez pas la permission de créer une catégorie.")
            return redirect('recipes:recipe_list')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter les catégories existantes pour l'aperçu
        context['categories_existantes'] = Category.objects.all().order_by('name')[:10]
        return context

    def form_valid(self, form):
        messages.success(
            self.request,
            f"✅ La catégorie '{form.instance.nom}' a été créée avec succès !"
        )
        return super().form_valid(form)
    
