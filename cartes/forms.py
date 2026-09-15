from django import forms
from .models import Personne
from django.utils import timezone

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

    def clean_date_naissance(self):
        date = self.cleaned_data.get("date_naissance")

        if date and date > timezone.now().date():
            raise forms.ValidationError(
                "La date de naissance ne peut pas être dans le futur."
            )

        return date