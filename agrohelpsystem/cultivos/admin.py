# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: admin.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las clases para personalizar los módulos en la página del administrador """
# ------------------------------------------------------------------------------------------------------

from django.contrib import admin
from .models import Localizacion, Cultivo, Campo, Agricultor

# Clase para personalizar la vista del módulo Localización
@admin.register(Localizacion)
class LocalizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pais', 'ciudad', 'longitud', 'latitud', 'display_campo')

# Clase para personalizar la vista del módulo Cultivo
@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

# Clase para personalizar la vista del módulo Campo
@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_propietario', 'num_ha', 'display_cultivos')

# Clase para personalizar la vista del módulo Agricultor
@admin.register(Agricultor)
class AgricultorAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'display_superuser', 'display_password')