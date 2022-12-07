from django.contrib import admin
from .models import Localizacion, Cultivo, Campo, Agricultor

# Define the admin class
@admin.register(Localizacion)
class LocalizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pais', 'ciudad', 'longitud', 'latitud', 'display_campo')

# Define the admin class
@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

# Define the admin class
@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_propietario', 'num_ha', 'display_cultivos')

@admin.register(Agricultor)
class AgricultorAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'display_superuser', 'display_password')