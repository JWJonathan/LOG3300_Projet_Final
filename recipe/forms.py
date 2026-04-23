# recipes/forms.py
from django import forms
from .models import Recipe, Category

class RecipeForm(forms.ModelForm):
    """
    Formulaire de création et modification d'une recette.
    Exclut les champs automatiques (slug, auteur, dates) qui seront gérés dans la vue.
    """
    class Meta:
        model = Recipe
        fields = [
            'title',
            'category',
            'description',
            'ingredients',
            'steps',
            'prep_time',
            'cook_time',
            'servings',
            'difficulty',
            'image',
            'slug',  # Inclure le slug pour les mises à jour, mais le rendre non éditable
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Décrivez brièvement votre recette...'
            }),
            'ingredients': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Listez les ingrédients (un par ligne) :\n- 200g de farine\n- 3 œufs\n- ...'
            }),
            'steps': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Décrivez les étapes de préparation :\n1. Préchauffer le four...\n2. Mélanger...\n3. ...'
            }),
            'prep_time': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'cook_time': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'servings': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Titre de la recette',
            'category': 'Catégorie',
            'description': 'Courte description',
            'ingredients': 'Ingrédients',
            'steps': 'Étapes',
            'prep_time': 'Temps de préparation (minutes)',
            'cook_time': 'Temps de cuisson (minutes)',
            'servings': 'Nombre de portions',
            'difficulty': 'Niveau de difficulté',
            'image': 'Photo du plat (optionnelle)',
        }
        help_texts = {
            'ingredients': 'Séparez les ingrédients par un retour à la ligne.',
            'steps': 'Numérotez les étapes pour plus de clarté.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'slug' in self.fields:
            self.fields['slug'].widget.attrs['readonly'] = True
        # Ajout de classes CSS pour Bootstrap/Tailwind (exemple avec Bootstrap)
        for field_name, field in self.fields.items():
            if field_name not in ['image', 'difficulty', 'category']:
                field.widget.attrs.update({'class': 'form-control'})
        # Rendre certains champs obligatoires plus évidents
        self.fields['title'].required = True
        self.fields['ingredients'].required = True
        self.fields['steps'].required = True

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError("Le titre doit contenir au moins 3 caractères.")
        return title

    def clean_prep_time(self):
        prep_time = self.cleaned_data.get('prep_time')
        if prep_time < 0:
            raise forms.ValidationError("Le temps de préparation ne peut pas être négatif.")
        return prep_time

    def clean_cook_time(self):
        cook_time = self.cleaned_data.get('cook_time')
        if cook_time < 0:
            raise forms.ValidationError("Le temps de cuisson ne peut pas être négatif.")
        return cook_time
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug and Recipe.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ce slug est déjà utilisé par une autre recette.")
        return slug


# Formulaire optionnel pour la catégorie (si l'utilisateur peut en ajouter)
class CategoryForm(forms.ModelForm):
    """
    Formulaire pour créer/modifier une catégorie (accessible seulement à l'admin ou utilisateurs autorisés).
    """
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Entrée, Plat, Dessert'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez brièvement cette catégorie (optionnel)...',
            }),
        }
        labels = {
            'name': 'Nom de la catégorie'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("Cette catégorie existe déjà.")
        # Vérifier l'unicité (sauf pour l'instance en cours de modification)
        if Category.objects.filter(name__iexact=name).exists():
            if not self.instance.pk or Category.objects.exclude(pk=self.instance.pk).filter(name__iexact=name).exists():
                raise forms.ValidationError("Une catégorie avec ce nom existe déjà.")
        
        return name