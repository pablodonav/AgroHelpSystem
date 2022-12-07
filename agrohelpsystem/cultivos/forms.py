from django import forms
from .models import Cultivo, Campo, Localizacion
from django.forms import TextInput, ModelMultipleChoiceField, DecimalField, FileField, Form

class AddCultivo(forms.ModelForm):

    class Meta:
        model = Cultivo
        fields = ['nombre']
        widgets = {
            'nombre': TextInput()
        }

class AddCampo(forms.ModelForm):
    cult = Cultivo.objects.values_list('nombre', flat=True)

    num_ha = DecimalField(max_digits=10, decimal_places=3)
    CULTIVOS = ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, required=True, queryset=cult, label='')

    class Meta:
        model = Campo
        fields = ['num_ha', 'CULTIVOS']

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

class ImportCultivoForm(Form):
    cultivos_file = FileField()