from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.RecipeListView.as_view(), name='recipe_list'),
    path('recette/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('creer/', views.RecipeCreateView.as_view(), name='recipe_create'),
    path('modifier/<slug:slug>/', views.RecipeUpdateView.as_view(), name='recipe_update'),
    path('supprimer/<slug:slug>/', views.RecipeDeleteView.as_view(), name='recipe_delete'),
    path('mes-recettes/', views.UserRecipeListView.as_view(), name='user_recipes'),
    path('categorie/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('ajouter/categorie/', views.CategoryCreate.as_view(), name='categorie-create'),
]