import base64
import io

import qrcode
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


LARGEUR_CARTE = 85.6 * mm
HAUTEUR_CARTE = 54 * mm

BLEU = HexColor("#0B3D91")
GRIS = HexColor("#444444")
BLANC = HexColor("#FFFFFF")
NOIR = HexColor("#000000")


def generer_qrcode(personne):
    """
    Génère le QR code du badge.

    Le QR code contient uniquement le matricule
    permettant d'identifier le badge.
    """

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )

    qr.add_data(personne.matricule)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer


def generer_qrcode_base64(personne):
    """
    Génère le QR code en base64 pour l'affichage HTML.
    """

    buffer = generer_qrcode(personne)

    return base64.b64encode(
        buffer.read()
    ).decode("ascii")


def _entete(c, titre):
    """
    Dessine l'en-tête de la carte.
    """

    c.setFillColor(BLEU)

    c.rect(
        0,
        HAUTEUR_CARTE - 9 * mm,
        LARGEUR_CARTE,
        9 * mm,
        fill=1,
        stroke=0,
    )

    c.setFillColor(BLANC)

    c.setFont(
        "Helvetica-Bold",
        8
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        HAUTEUR_CARTE - 6 * mm,
        titre
    )


def _ligne(c, x, y, label, valeur, taille=6):
    """
    Dessine une ligne Label : valeur.
    """

    prefixe = f"{label} : "

    c.setFillColor(GRIS)
    c.setFont(
        "Helvetica-Bold",
        taille
    )

    c.drawString(
        x,
        y,
        prefixe
    )

    largeur_prefixe = c.stringWidth(
        prefixe,
        "Helvetica-Bold",
        taille
    )

    c.setFillColor(NOIR)
    c.setFont(
        "Helvetica",
        taille
    )

    c.drawString(
        x + largeur_prefixe,
        y,
        str(valeur) if valeur else "-"
    )


def generer_pdf_carte(personne):
    """
    Génère un PDF de 2 pages :
    page 1 = recto
    page 2 = verso

    Format carte d'identité.
    """

    buffer = io.BytesIO()

    c = canvas.Canvas(
        buffer,
        pagesize=(
            LARGEUR_CARTE,
            HAUTEUR_CARTE
        )
    )

    # ==================================================
    # RECTO
    # ==================================================

    _entete(
        c,
        "BADGE D'ACCÈS - IDENTIFICATION"
    )

    # Photo
    x_photo = 4 * mm
    largeur_photo = 19 * mm
    hauteur_photo = 24 * mm

    y_photo = (
        HAUTEUR_CARTE
        - 9 * mm
        - hauteur_photo
        - 2 * mm
    )

    if personne.photo and hasattr(
        personne.photo,
        "path"
    ):

        try:

            c.drawImage(
                personne.photo.path,
                x_photo,
                y_photo,
                width=largeur_photo,
                height=hauteur_photo,
                preserveAspectRatio=True,
                mask="auto",
            )

        except Exception:

            c.setFillColor(
                HexColor("#DDDDDD")
            )

            c.rect(
                x_photo,
                y_photo,
                largeur_photo,
                hauteur_photo,
                fill=1,
                stroke=0,
            )

    else:

        c.setFillColor(
            HexColor("#DDDDDD")
        )

        c.rect(
            x_photo,
            y_photo,
            largeur_photo,
            hauteur_photo,
            fill=1,
            stroke=0,
        )

    # Informations
    x_texte = (
        x_photo
        + largeur_photo
        + 3 * mm
    )

    y = HAUTEUR_CARTE - 13 * mm
    pas = 5.2 * mm

    _ligne(
        c,
        x_texte,
        y,
        "Nom",
        personne.nom.upper()
    )
    y -= pas

    _ligne(
        c,
        x_texte,
        y,
        "Prénom(s)",
        personne.prenoms
    )
    y -= pas

    _ligne(
        c,
        x_texte,
        y,
        "Né(e) le",
        personne.date_naissance.strftime(
            "%d-%m-%Y"
        )
    )
    y -= pas

    _ligne(
        c,
        x_texte,
        y,
        "Lieu de naissance",
        personne.lieu_naissance
    )
    y -= pas

    _ligne(
        c,
        x_texte,
        y,
        "Nationalité",
        personne.nationalite
    )

    # Groupe
    c.setFillColor(BLEU)

    c.setFont(
        "Helvetica-Bold",
        8
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        8 * mm,
        f"GROUPE {personne.groupe}"
    )

    # Matricule
    c.setFillColor(GRIS)

    c.setFont(
        "Helvetica",
        5
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        4.5 * mm,
        f"N° {personne.matricule}"
    )

    c.showPage()

    # ==================================================
    # VERSO
    # ==================================================

    _entete(
        c,
        "CONTRÔLE D'ACCÈS"
    )

    # Texte
    c.setFillColor(GRIS)

    c.setFont(
        "Helvetica",
        6
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        HAUTEUR_CARTE - 15 * mm,
        "Scanner le QR code pour vérifier l'accès"
    )

    # QR CODE
    qr_buffer = generer_qrcode(personne)

    qr_img = ImageReader(
        qr_buffer
    )

    taille_qr = 25 * mm

    x_qr = (
        LARGEUR_CARTE
        - taille_qr
    ) / 2

    y_qr = 14 * mm

    c.drawImage(
        qr_img,
        x_qr,
        y_qr,
        width=taille_qr,
        height=taille_qr,
        preserveAspectRatio=True,
        mask="auto",
    )

    # Matricule sous le QR
    c.setFillColor(GRIS)

    c.setFont(
        "Helvetica-Bold",
        5.5
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        9 * mm,
        personne.matricule
    )

    c.setFont(
        "Helvetica",
        4.5
    )

    c.drawCentredString(
        LARGEUR_CARTE / 2,
        5.5 * mm,
        "Badge d'accès"
    )

    c.showPage()

    c.save()

    buffer.seek(0)

    return buffer