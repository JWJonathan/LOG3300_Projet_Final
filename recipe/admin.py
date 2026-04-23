# recipes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Recipe


# -------------------------------
# ADMIN POUR LES CATÉGORIES
# -------------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description_summary', 'slug', 'recipe_count']
    list_display_links = ['name']
    search_fields = ['name', 'description', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    list_per_page = 20
    fields = ['name', 'description', 'slug']

    def description_summary(self, obj):
        """Extrait de la description."""
        if obj.description:
            if len(obj.description) > 80:
                return f"{obj.description[:80]}…"
            return obj.description
        return "-"
    description_summary.short_description = "Description"

    def recipe_count(self, obj):
        """
        Nombre de recettes avec lien vers la liste filtrée.
        Utilise les métadonnées pour construire le nom de l'URL admin.
        """
        count = obj.recipes.count()
        if count > 0:
            # Récupération dynamique de l'app_label et du model_name
            opts = Recipe._meta
            url_name = f'admin:{opts.app_label}_{opts.model_name}_changelist'
            url = reverse(url_name) + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} recette{}</a>', url, count, 's' if count > 1 else '')
        return "0 recette"
    recipe_count.short_description = "Recettes"
    recipe_count.admin_order_field = 'recipes__count'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('recipes')


# -------------------------------
# ADMIN POUR LES RECETTES
# -------------------------------

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview', 'title', 'author', 'category',
        'difficulty_badge', 'total_time', 'servings',
        'created_at', 'updated_at'
    ]
    list_display_links = ['title']
    list_filter = [
        'category',
        'difficulty',
        'created_at',
        ('author', admin.RelatedOnlyFieldListFilter),
    ]
    search_fields = [
        'title', 'description', 'ingredients', 'steps',
        'author__username', 'author__email'
    ]
    readonly_fields = ['created_at', 'updated_at', 'image_preview_large']
    save_on_top = True
    list_per_page = 25

    fieldsets = (
        ('Informations générales', {
            'fields': (
                'title', 'author', 'category', 'description',
                ('difficulty', 'servings'),
                ('prep_time', 'cook_time'),
            )
        }),
        ('Contenu de la recette', {
            'fields': ('ingredients', 'steps'),
            'classes': ('wide',)
        }),
        ('Image', {
            'fields': ('image', 'image_preview_large'),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['duplicate_recipes', 'mark_as_easy', 'mark_as_medium', 'mark_as_hard']

    # ---------- Affichage personnalisé ----------
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:4px;" />', obj.image.url)
        return format_html('<div style="width:50px;height:50px;background:#f0f0f0;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#999;">🍳</div>')
    image_preview.short_description = "Image"

    def image_preview_large(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width:300px;max-height:300px;border-radius:8px;" />', obj.image.url)
        return "Aucune image"
    image_preview_large.short_description = "Aperçu"

    def difficulty_badge(self, obj):
        colors = {'EASY': 'green', 'MEDIUM': 'orange', 'HARD': 'red'}
        color = colors.get(obj.difficulty, 'gray')
        return format_html(
            '<span style="background-color:{};color:white;padding:4px 8px;border-radius:4px;font-size:0.85em;">{}</span>',
            color, obj.get_difficulty_display()
        )
    difficulty_badge.short_description = "Difficulté"
    difficulty_badge.admin_order_field = 'difficulty'

    def total_time(self, obj):
        return f"{obj.prep_time + obj.cook_time} min"
    total_time.short_description = "Temps total"
    total_time.admin_order_field = 'prep_time'

    # ---------- Actions personnalisées ----------
    @admin.action(description="Dupliquer les recettes sélectionnées")
    def duplicate_recipes(self, request, queryset):
        count = 0
        for recipe in queryset:
            new_recipe = Recipe(
                title=f"{recipe.title} (copie)",
                author=recipe.author,
                category=recipe.category,
                description=recipe.description,
                ingredients=recipe.ingredients,
                steps=recipe.steps,
                prep_time=recipe.prep_time,
                cook_time=recipe.cook_time,
                servings=recipe.servings,
                difficulty=recipe.difficulty,
                image=recipe.image
            )
            new_recipe.save()  # le slug sera rendu unique par la méthode save()
            count += 1
        self.message_user(request, f"{count} recette(s) dupliquée(s) avec succès.")

    @admin.action(description="Marquer comme Facile")
    def mark_as_easy(self, request, queryset):
        updated = queryset.update(difficulty='EASY')
        self.message_user(request, f"{updated} recette(s) marquée(s) comme Facile.")

    @admin.action(description="Marquer comme Moyenne")
    def mark_as_medium(self, request, queryset):
        updated = queryset.update(difficulty='MEDIUM')
        self.message_user(request, f"{updated} recette(s) marquée(s) comme Moyenne.")

    @admin.action(description="Marquer comme Difficile")
    def mark_as_hard(self, request, queryset):
        updated = queryset.update(difficulty='HARD')
        self.message_user(request, f"{updated} recette(s) marquée(s) comme Difficile.")

    # ---------- Sauvegarde automatique de l'auteur ----------
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    # ---------- Optimisation des requêtes ----------
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


# Personnalisation globale de l'admin
admin.site.site_header = "Administration - Livre de Recettes Familiales"
admin.site.site_title = "Admin Recettes"
admin.site.index_title = "Gestion des Recettes et Catégories"