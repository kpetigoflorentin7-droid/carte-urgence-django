from django.contrib import admin
from .models import Personne
# Register your models here.

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ("matricule", "nom", "prenoms", "date_naissance", "date_expiration")
    search_fields = ("matricule", "nom", "prenoms")
    readonly_fields = ("matricule", "date_emission", "date_expiration")