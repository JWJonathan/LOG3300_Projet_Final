# recipes/models.py
from django.db import models
from django.urls import reverse
from django.conf import settings  # Pour référencer le modèle User personnalisé

class Category(models.Model):
    """
    Modèle représentant une catégorie de recette (Entrée, Plat, Dessert...).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la catégorie")
    description = models.TextField(blank=True, verbose_name="Déscription de la catégorie")
    slug = models.SlugField(max_length=100, unique=True, blank=True, 
                            help_text="Généré automatiquement à partir du nom si laissé vide.")

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-génération du slug à partir du nom s'il n'est pas fourni
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recipes:category_detail', kwargs={'slug': self.slug})


class Recipe(models.Model):
    """
    Modèle représentant une recette de cuisine.
    L'auteur est lié au modèle User de l'application 'users'.
    """
    DIFFICULTY_CHOICES = [
        ('EASY', 'Facile'),
        ('MEDIUM', 'Moyen'),
        ('HARD', 'Difficile'),
    ]

    title = models.CharField(max_length=200, verbose_name="Titre de la recette")
    slug = models.SlugField(max_length=200, unique=True, blank=True,
                            help_text="Identifiant unique pour l'URL (généré automatiquement).")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Référence dynamique au modèle User (users.CustomUser si défini)
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Auteur"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipes',
        verbose_name="Catégorie"
    )
    description = models.TextField(verbose_name="Courte description")
    ingredients = models.TextField(verbose_name="Liste des ingrédients")
    steps = models.TextField(verbose_name="Étapes de préparation")
    prep_time = models.PositiveIntegerField(default=0, verbose_name="Temps de préparation (minutes)")
    cook_time = models.PositiveIntegerField(default=0, verbose_name="Temps de cuisson (minutes)")
    servings = models.PositiveIntegerField(default=4, verbose_name="Nombre de portions")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM', 
                                  verbose_name="Difficulté")
    image = models.ImageField(upload_to='recipes/images/', blank=True, null=True, 
                              verbose_name="Photo du plat")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")

    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ['-created_at']
        # Optionnel : empêcher les doublons exacts de titre pour un même auteur
        # unique_together = ['title', 'author']

    def __str__(self):
        return f"{self.title} par {self.author.username}"

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            # On crée un slug basé sur le titre, mais on s'assure qu'il est unique
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', kwargs={'slug': self.slug})