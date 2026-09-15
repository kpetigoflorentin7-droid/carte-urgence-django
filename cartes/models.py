import re
import unicodedata
from datetime import date

from django.db import models


def sans_accents(texte):
    """Retire les accents pour fiabiliser la génération du matricule."""
    if not texte:
        return ""

    nfkd = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


class Personne(models.Model):

    GROUPE_CHOICES = [
        ("A", "Groupe A"),
        ("B", "Groupe B"),
    ]

    SEXE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]

    # Identification
    matricule = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False
    )

    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=150)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=150)
    nationalite = models.CharField(
        max_length=100,
        default="Togolaise"
    )

    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES,
        blank=True
    )

    # Groupe d'accès
    groupe = models.CharField(
        max_length=1,
        choices=GROUPE_CHOICES
    )

    photo = models.ImageField(
        upload_to="photos/",
        blank=True,
        null=True
    )

    # Informations de la carte
    lieu_emission = models.CharField(
        max_length=100,
        default="Lomé",
        help_text="Lieu où la carte est établie"
    )

    date_emission = models.DateField(
        auto_now_add=True
    )

    date_expiration = models.DateField(
        blank=True,
        editable=False,
        null=True
    )

    def generer_matricule(self):
        nom_clean = re.sub(
            r"[^A-Za-z]",
            "",
            sans_accents(self.nom)
        ).upper()

        prenom_clean = re.sub(
            r"[^A-Za-z]",
            "",
            sans_accents(self.prenoms)
        ).upper()

        trois_lettres_nom = (nom_clean + "XXX")[:3]
        premiere_lettre_prenom = (prenom_clean + "X")[:1]

        jour = f"{self.date_naissance.day:02d}"
        annee = f"{self.date_naissance.year:04d}"

        return f"{trois_lettres_nom}{premiere_lettre_prenom}{jour}{annee}"

    def save(self, *args, **kwargs):

        if not self.matricule:
            self.matricule = self.generer_matricule()

        if not self.date_expiration:
            base = self.date_emission or date.today()

            try:
                self.date_expiration = base.replace(
                    year=base.year + 10
                )
            except ValueError:
                self.date_expiration = base.replace(
                    month=2,
                    day=28,
                    year=base.year + 10
                )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricule} - {self.nom} {self.prenoms}"