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


def generer_qrcode_contact(personne):
    """
    Génère une image QR code (en mémoire) encodant les infos du contact
    à prévenir en cas d'urgence, au format vCard : scanné avec un
    téléphone, il propose directement d'enregistrer le contact.
    """
    vcard = (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"N:{personne.contact_urgence_nom}\n"
        f"FN:{personne.contact_urgence_nom}\n"
        f"TEL;TYPE=CELL:{personne.contact_urgence_telephone}\n"
        f"NOTE:Contact d'urgence ({personne.contact_urgence_relation}) "
        f"pour {personne.nom} {personne.prenoms} - Matricule {personne.matricule}\n"
        "END:VCARD"
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(vcard)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def generer_qrcode_base64(personne):
    """Même QR code que ci-dessus, mais encodé en base64 pour l'aperçu HTML."""
    buffer = generer_qrcode_contact(personne)
    return base64.b64encode(buffer.read()).decode("ascii")


def _entete(c, titre):
    c.setFillColor(BLEU)
    c.rect(0, HAUTEUR_CARTE - 9 * mm, LARGEUR_CARTE, 9 * mm, fill=1, stroke=0)
    c.setFillColor(BLANC)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(LARGEUR_CARTE / 2, HAUTEUR_CARTE - 6 * mm, titre)


def _ligne(c, x, y, label, valeur, taille=6):
    """Dessine 'Label : valeur' sur une seule ligne."""
    prefixe = f"{label} : "
    c.setFillColor(GRIS)
    c.setFont("Helvetica-Bold", taille)
    c.drawString(x, y, prefixe)
    largeur_prefixe = c.stringWidth(prefixe, "Helvetica-Bold", taille)

    c.setFillColor(NOIR)
    c.setFont("Helvetica", taille)
    c.drawString(x + largeur_prefixe, y, str(valeur) if valeur else "-")


def generer_pdf_carte(personne):
    """
    Génère un PDF de 2 pages (recto puis verso), taille carte d'identité,
    pour la personne donnée. Retourne un buffer BytesIO prêt à être servi.
    """
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(LARGEUR_CARTE, HAUTEUR_CARTE))

    # ---------- RECTO ----------
    _entete(c, "CARTE D'URGENCE - IDENTIFICATION")

    x_photo = 4 * mm
    largeur_photo = 19 * mm
    hauteur_photo = 24 * mm
    y_photo = HAUTEUR_CARTE - 9 * mm - hauteur_photo - 2 * mm

    if personne.photo and hasattr(personne.photo, "path"):
        try:
            c.drawImage(
                personne.photo.path,
                x_photo, y_photo,
                width=largeur_photo, height=hauteur_photo,
                preserveAspectRatio=True, mask="auto",
            )
        except Exception:
            c.setFillColor(HexColor("#DDDDDD"))
            c.rect(x_photo, y_photo, largeur_photo, hauteur_photo, fill=1, stroke=0)
    else:
        c.setFillColor(HexColor("#DDDDDD"))
        c.rect(x_photo, y_photo, largeur_photo, hauteur_photo, fill=1, stroke=0)

    x_texte = x_photo + largeur_photo + 3 * mm
    y = HAUTEUR_CARTE - 13 * mm
    pas = 5.2 * mm

    _ligne(c, x_texte, y, "Nom", personne.nom.upper()); y -= pas
    _ligne(c, x_texte, y, "Prénom(s)", personne.prenoms); y -= pas
    _ligne(c, x_texte, y, "Né(e) le", personne.date_naissance.strftime("%d-%m-%Y")); y -= pas
    _ligne(c, x_texte, y, "Lieu de naissance", personne.lieu_naissance); y -= pas
    _ligne(c, x_texte, y, "Nationalité", personne.nationalite); y -= pas
    _ligne(c, x_texte, y, "Sexe", personne.get_sexe_display()); y -= pas
    _ligne(c, x_texte, y, "Profession", personne.profession)

    c.setFillColor(BLEU)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(LARGEUR_CARTE / 2, 6 * mm, f"N° {personne.matricule}")

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 5)
    c.drawString(4 * mm, 2 * mm,
                 f"Fait à {personne.lieu_emission}, le {personne.date_emission.strftime('%d-%m-%Y')}")
    c.drawRightString(LARGEUR_CARTE - 4 * mm, 2 * mm,
                       f"Expire le : {personne.date_expiration.strftime('%d-%m-%Y')}")

    c.showPage()

    # ---------- VERSO ----------
    _entete(c, "INFORMATIONS COMPLÉMENTAIRES")

    x_texte = 4 * mm
    y = HAUTEUR_CARTE - 14 * mm
    pas = 6.5 * mm

    _ligne(c, x_texte, y, "Taille", f"{personne.taille_cm / 100:.2f} m")
    y -= pas
    _ligne(c, x_texte, y, "Groupe sanguin", personne.groupe_sanguin)
    y -= pas
    _ligne(c, x_texte, y, "Père", personne.pere)
    y -= pas
    _ligne(c, x_texte, y, "Mère", personne.mere)

    qr_buffer = generer_qrcode_contact(personne)
    qr_img = ImageReader(qr_buffer)
    taille_qr = 18 * mm
    x_qr = LARGEUR_CARTE - taille_qr - 4 * mm
    y_qr = 8 * mm
    c.drawImage(qr_img, x_qr, y_qr, width=taille_qr, height=taille_qr)

    c.setFillColor(GRIS)
    c.setFont("Helvetica", 4.5)
    c.drawCentredString(x_qr + taille_qr / 2, y_qr - 3, "À prévenir en cas d'urgence")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer