from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Cultivo, Localizacion, Campo, Agricultor, HistoricoCultivo, CultivosCampo
from .forms import AddCultivo, AddCampo, ImportCultivoForm, ImportHistoricoCultivoForm
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd
import requests
import geojson
from django.views.generic.base import View
import decimal
import sys
from pulp import LpMaximize, LpProblem, LpStatus, lpSum, LpVariable


# Obtiene el rendimiento medio de un cultivo en un campo en base a los datos almacenados en el histórico
def getRendimientoMedioCultivo(_campo, _cultivo):
    rendimientoMedio = float(0)
    rendimientosCultivo = list(HistoricoCultivo.objects.filter(campo = _campo, cultivo=_cultivo).values_list('rendimiento', flat=True))

    for rendimiento in rendimientosCultivo:
        rendimientoMedio += float(rendimiento)

    rendimientoMedio /= len(rendimientosCultivo)

    return float(rendimientoMedio)

# Obtiene la lista de objetos Cultivo que se han plantado en un campo
def getCultivosDeHistorico(_historicosCultivosCampo):
    cultivos = []

    if _historicosCultivosCampo != None:
        for historicoCultivo in _historicosCultivosCampo:
            cultivos.append(historicoCultivo.cultivo)

        cultivos = list(dict.fromkeys(cultivos)) #Elimina duplicados

        return cultivos
    return None

# Obtiene el precio por hectárea a partir del rendimiento medio del cultivo(Kg/ha) y el precio del cultivo(€/Kg)
def getPreciosPorHectareaCultivos(_campo, _cultivosCampo):
    preciosCultivos = []

    if _cultivosCampo != None:
        for cultivo in _cultivosCampo:
            preciosCultivos.append(getRendimientoMedioCultivo(_campo, cultivo) * float(cultivo.precio_kg))

        return preciosCultivos
    return None

def getHectareasLibresCampo(_campo):
    ha_ocupadas = float(0)
    ha_libres = float(0)

    for cultivo in _campo.CULTIVOS.all():
        cultivo_campo = CultivosCampo.objects.get(campo=_campo,cultivo=cultivo)
        ha_ocupadas += float(cultivo_campo.ha_sembradas)

    ha_libres = float(_campo.num_ha) - ha_ocupadas

    return float(ha_libres)

# Obtiene la lista de los cultivos a sembrar en el campo con las hectáreas recomendadas para obtener el beneficio máximo
def calcularDistribucionOptimaCampo(_idCampo):
    campo = Campo.objects.get(id = _idCampo)
    cultivosCampo = getCultivosDeHistorico(HistoricoCultivo.objects.filter(campo = campo))
    preciosCultivos = getPreciosPorHectareaCultivos(campo, cultivosCampo)

    # Create the model
    model = LpProblem(name="cultivos-a-sembrar", sense=LpMaximize)

    # Define the decision variables
    x = {i: LpVariable(name=f"x{i}", lowBound=float(0)) for i in range(len(cultivosCampo))} # xi = num_ha a sembrar de cada cultivo i

    # Add constraints
    model += (lpSum(x.values()) <= float(getHectareasLibresCampo(campo)))

    # Set the objective
    model += lpSum([preciosCultivos[i]*x[i] for i in range(len(cultivosCampo))])

    # Solve the optimization problem
    model.solve()

    # Get the results
    results = dict()
    ha_cultivos = dict()
    results['status'] = model.status
    results['beneficio'] = round(model.objective.value(), 5)
    results['ha_cultivos'] = ha_cultivos

    for i in range(len(cultivosCampo)):
        if round(x[i].value(), 1) != 0.0:
            ha_cultivos[cultivosCampo[i].nombre] = round(x[i].value(), 5)

    # Get the results
    sourceFile = open('/home/Adnana/text.txt', 'a')
    print(results, file = sourceFile)
    sourceFile.close()

    return results

def AddCultivoToCampo(request, pk):
    if request.method == "POST":
        cultivo = Cultivo.objects.get(id = request.POST["idCultivo"])
        campo = Campo.objects.get(id = pk)
        cultivoCampo = CultivosCampo(cultivo=cultivo, campo=campo, campanya_sembrado=request.POST["campanya_sembrado"], ha_sembradas=request.POST["hectareas_sembradas"])
        cultivoCampo.save()
        messages.success(request, "El cultivo se ha asignado al campo.")
        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk))
    campo = Campo.objects.get(id = pk)
    cultivos = Cultivo.objects.all()
    results = calcularDistribucionOptimaCampo(pk)

    return render(request, "cultivos/add_cultivo_to_campo.html", context={'cultivos': cultivos, 'campo': campo, 'results': results})
