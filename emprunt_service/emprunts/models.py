from django.db import models
from django.db.models import Q

STATUT_CHOICES = (
    ("EN_COURS", "EN_COURS"),
    ("RENDU", "RENDU"),
)

class Emprunt(models.Model):
    utilisateur_id = models.IntegerField()
    livre_id = models.IntegerField()
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_COURS")

    class Meta:
        constraints = [
            # Un seul emprunt EN_COURS par livre
            models.UniqueConstraint(
                fields=["livre_id"],
                condition=Q(statut="EN_COURS"),
                name="uniq_emprunt_en_cours_par_livre",
            )
        ]

    def __str__(self):
        return f"(U{self.utilisateur_id}) Livre {self.livre_id} — {self.statut}"
