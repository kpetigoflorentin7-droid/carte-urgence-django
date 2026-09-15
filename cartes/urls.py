from django.urls import path

from . import views


urlpatterns = [

    path(
        "",
        views.creer_carte,
        name="creer_carte"
    ),

    path(
        "carte/<int:pk>/",
        views.carte_creee,
        name="carte_creee"
    ),

    path(
        "carte/<int:pk>/pdf/",
        views.telecharger_pdf,
        name="telecharger_pdf"
    ),

    path(
        "scanner/<str:matricule>/",
        views.scanner_badge,
        name="scanner_badge"
    ),
]