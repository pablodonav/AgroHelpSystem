# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: admin.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las clases para personalizar los modelos en la página del administrador """
# ------------------------------------------------------------------------------------------------------

from django.contrib import admin
from .models import Localizacion, Cultivo, Campo, Agricultor, CultivosCampo, HistoricoCultivo

# Clase para personalizar la vista del módulo Localización
@admin.register(Localizacion)
class LocalizacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pais', 'ciudad', 'longitud', 'latitud', 'display_campo')

# Clase para personalizar la vista del módulo Agricultor
@admin.register(Agricultor)
class AgricultorAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'display_superuser', 'display_password')

# Clase para personalizar la vista del módulo Cultivo
@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio_kg', 'riego_dia', 'kg_ha', 'tipo')

# Clase para personalizar la vista del módulo Campo
@admin.register(Campo)
class CampoAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_propietario', 'num_ha', 'display_cultivos', 'volumen_agua_disp', 'tipo_riego')

# Clase para personalizar la vista del módulo CultivosCampo
@admin.register(CultivosCampo)
class CultivosCampoAdmin(admin.ModelAdmin):
    list_display = ('cultivo', 'campo', 'campanya_sembrado', 'ha_sembradas')

# Clase para personalizar la vista del módulo HistoricoCultivo
@admin.register(HistoricoCultivo)
class HistoricoCultivoAdmin(admin.ModelAdmin):
    list_display = ('cultivo', 'campo', 'campanya_sembrado', 'ha_sembradas', 'ha_cosechadas', 'produccion', 'rendimiento')