from django.contrib import admin
from .models import Livre

@admin.register(Livre)
class LivreAdmin(admin.ModelAdmin):
    list_display = ("id", "titre", "auteur", "categorie", "disponible")
    search_fields = ("titre", "auteur")
    list_filter = ("disponible", "categorie")
