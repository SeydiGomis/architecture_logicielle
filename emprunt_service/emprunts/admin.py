from django.contrib import admin
from .models import Emprunt

@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ("id", "utilisateur_id", "livre_id", "date_emprunt", "date_retour", "statut")
    list_filter = ("statut", "date_emprunt")
    search_fields = ("utilisateur_id", "livre_id")
