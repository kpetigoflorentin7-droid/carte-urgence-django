from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PersonneForm
from .models import Personne
from .utils import generer_pdf_carte, generer_qrcode_base64


def creer_carte(request):
    if request.method == "POST":
        form = PersonneForm(request.POST, request.FILES)
        if form.is_valid():
            personne = form.save()
            return redirect("carte_creee", pk=personne.pk)
    else:
        form = PersonneForm()

    return render(request, "cartes/formulaire.html", {"form": form})


def carte_creee(request, pk):
    personne = get_object_or_404(Personne, pk=pk)
    contexte = {
        "personne": personne,
        "qr_base64": generer_qrcode_base64(personne),
    }
    return render(request, "cartes/carte_creee.html", contexte)


def telecharger_pdf(request, pk):
    personne = get_object_or_404(Personne, pk=pk)
    buffer = generer_pdf_carte(personne)
    nom_fichier = f"carte_urgence_{personne.matricule}.pdf"
    return FileResponse(buffer, as_attachment=True, filename=nom_fichier)