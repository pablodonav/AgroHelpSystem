# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: forms.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene los formularios de modelo creados para diferentes modelos """
# ------------------------------------------------------------------------------------------------------
from django import forms
from .models import Cultivo, Campo, Localizacion
from django.forms import TextInput, ModelMultipleChoiceField, DecimalField, FileField, Form

# Clase que representa el formulario para añadir un cultivo
class AddCultivo(forms.ModelForm):
    class Meta:
        model = Cultivo
        fields = ['nombre']
        widgets = {
            'nombre': TextInput()
        }

# Clase que representa el formulario para añadir un campo
class AddCampo(forms.ModelForm):
    cult = Cultivo.objects.values_list('nombre', flat=True)

    num_ha = DecimalField(max_digits=10, decimal_places=3)
    CULTIVOS = ModelMultipleChoiceField(widget=forms.SelectMultiple(), required=True, queryset=cult, label='')

    class Meta:
        model = Campo
        fields = ['num_ha', 'CULTIVOS']

# Clase que representa el formulario para añadir una localización
class AddLocalizacion(forms.ModelForm):
    longitud = DecimalField(max_digits=10, decimal_places=3)
    latitud = DecimalField(max_digits=10, decimal_places=3)

    class Meta:
        model = Localizacion
        fields = ['pais', 'ciudad', 'longitud', 'latitud']
        widgets = {
            'pais': TextInput(),
            'ciudad' : TextInput()
        }

# Clase que representa el formulario para importar un csv con cultivos
class ImportCultivoForm(Form):
    cultivos_file = FileField()