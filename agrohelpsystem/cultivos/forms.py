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
from .models import Cultivo, Campo
from django.forms import DecimalField, FileField, Form, CharField

# Clase que representa el formulario para añadir un cultivo
class AddCultivo(forms.ModelForm):
        CULTIVO_REGADIO = 'REGADIO'
        CULTIVO_SECANO = 'SECANO'
        TIPO_CULTIVO_CHOICES = [
            (CULTIVO_REGADIO, 'Cultivo de regadío'),
            (CULTIVO_SECANO, 'Cultivo de secano'),
        ]

        nombre = CharField()
        precio_kg = DecimalField(max_digits=12, decimal_places=5)
        riego_dia = DecimalField(max_digits=12, decimal_places=5)
        kg_ha = DecimalField(max_digits=12, decimal_places=5)
        tipo = CharField(label='Selecciona un tipo de cultivo', widget=forms.Select(choices=TIPO_CULTIVO_CHOICES))

        class Meta:
            model = Cultivo
            fields = ['nombre', 'precio_kg', 'riego_dia', 'kg_ha', 'tipo']


# Clase que representa el formulario para añadir un campo
class AddCampo(forms.ModelForm):
    RIEGO_POR_SUPERFICIE = 'RSUPERFICIE'
    RIEGO_POR_ASPERSION = 'RASPERSION'
    RIEGO_LOCALIZADO = 'RLOCALIZADO'
    RIEGO_SUBTERRANEO = 'RSUBTERRANEO'
    RIEGO_CHOICES = [
        (RIEGO_POR_SUPERFICIE, 'Riego por superficie'),
        (RIEGO_POR_ASPERSION, 'Riego por aspersión'),
        (RIEGO_LOCALIZADO, 'Riego localizado'),
        (RIEGO_SUBTERRANEO, 'Riego subterráneo'),
    ]

    cult = Cultivo.objects.values_list('nombre', flat=True)

    num_ha = DecimalField(max_digits=12, decimal_places=5)
    volumen_agua_disp = DecimalField(max_digits=12, decimal_places=5)
    tipo_riego = CharField(label='Selecciona un tipo de riego', widget=forms.Select(choices=RIEGO_CHOICES))

    class Meta:
        model = Campo
        fields = ['num_ha', 'volumen_agua_disp', 'tipo_riego']

# Clase que representa el formulario para importar un csv con cultivos
class ImportCultivoForm(Form):
    cultivos_file = FileField()

# Clase que representa el formulario para importar un csv con datos históricos sobre un cultivo de un terreno
class ImportHistoricoCultivoForm(Form):
    historico_cultivo = FileField()