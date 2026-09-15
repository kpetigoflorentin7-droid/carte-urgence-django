from django import forms
from .models import Personne


class PersonneForm(forms.ModelForm):

    class Meta:
        model = Personne

        fields = [
            "nom",
            "prenoms",
            "date_naissance",
            "lieu_naissance",
            "nationalite",
            "groupe",
            "sexe",
            "photo",
            "lieu_emission",
        ]

        widgets = {
            "date_naissance": forms.DateInput(
                attrs={"type": "date"}
            ),
        }