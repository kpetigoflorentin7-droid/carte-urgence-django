import base64
from io import BytesIO
from datetime import datetime

import qrcode

from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PersonneForm
from .models import Personne
from .utils import generer_pdf_carte


def generer_qrcode(personne):
    """
    Génère un QR code contenant uniquement
    le matricule du badge.
    """

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(personne.matricule)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return base64.b64encode(
        buffer.getvalue()
    ).decode()


def creer_carte(request):

    if request.method == "POST":

        form = PersonneForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            personne = form.save()

            return redirect(
                "carte_creee",
                pk=personne.pk
            )

    else:
        form = PersonneForm()

    return render(
        request,
        "cartes/formulaire.html",
        {"form": form}
    )


def carte_creee(request, pk):

    personne = get_object_or_404(
        Personne,
        pk=pk
    )

    contexte = {
        "personne": personne,
        "qr_base64": generer_qrcode(personne),
    }

    return render(
        request,
        "cartes/carte_creee.html",
        contexte
    )


def scanner_badge(request, matricule):

    personne = get_object_or_404(
        Personne,
        matricule=matricule
    )

    minute = datetime.now().minute

    # Minute paire → groupe A
    if minute % 2 == 0:
        groupe_autorise = "A"
    else:
        # Minute impaire → groupe B
        groupe_autorise = "B"

    acces_autorise = (
        personne.groupe == groupe_autorise
    )

    contexte = {
        "personne": personne,
        "minute": minute,
        "groupe_autorise": groupe_autorise,
        "acces_autorise": acces_autorise,
    }

    return render(
        request,
        "cartes/scan.html",
        contexte
    )


def telecharger_pdf(request, pk):

    personne = get_object_or_404(
        Personne,
        pk=pk
    )

    buffer = generer_pdf_carte(personne)

    nom_fichier = (
        f"badge_{personne.matricule}.pdf"
    )

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=nom_fichier
    )