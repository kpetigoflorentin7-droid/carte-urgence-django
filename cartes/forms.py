from django import forms

from .models import Personne


class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = [
            "nom", "prenoms", "date_naissance", "sexe",
            "lieu_naissance", "nationalite", "profession", "photo",
            "taille_cm", "groupe_sanguin",
            "pere", "mere",
            "lieu_emission",
            "contact_urgence_nom", "contact_urgence_relation",
            "contact_urgence_telephone",
        ]
        widgets = {
            "date_naissance": forms.DateInput(attrs={"type": "date"}),
        }