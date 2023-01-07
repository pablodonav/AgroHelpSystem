# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: views.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las vistas de la app cultivos """
# ------------------------------------------------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Cultivo, Localizacion, Campo, Agricultor, CultivosCampo, HistoricoCultivo
from .forms import AddCultivo, AddCampo, ImportCultivoForm, ImportHistoricoCultivoForm
import pandas as pd
from django.views.generic.base import View
import plotly.graph_objects as go
from plotly.offline import plot
import json
import urllib.request
import datetime
import decimal
from django.contrib import messages
from pulp import LpMaximize, LpProblem, lpSum, LpVariable
from geopy.geocoders import Nominatim

#Función que permite redirigir a la plantilla para crear un cultivo
@login_required(login_url='/accounts/login/')
def NuevoCultivo(request, pk):
    if request.method == "POST":
        form = AddCultivo(request.POST)
        if cultivoRepetido(request.POST["nombre"]):
            messages.error(request, "Error. Ya existe un cultivo con ese nombre.")
        elif form.is_valid():
            cultivo = Cultivo(nombre=request.POST["nombre"], precio_kg=request.POST["precio_kg"], riego_dia=request.POST["riego_dia"], kg_ha=request.POST["kg_ha"], tipo=request.POST["tipo"])
            cultivo.save()
            messages.success(request, "El cultivo se ha creado correctamente")

        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk) + "/addCultivoToCampo/")
    form = AddCultivo()
    campo = Campo.objects.get(id = pk)
    return render(request, "cultivos/add_cultivo.html", {"form": form, 'campo': campo})

#Función que permite redirigir a la plantilla para crear una localización
@login_required(login_url='/accounts/login/')
def NuevaLocalizacion(request, pk):
    campo = Campo.objects.get(id = pk)
    if request.method == "GET":
        if request.GET.get('longitud') != None:
            localizacion = Localizacion(pais='', ciudad='', longitud=request.GET.get('longitud'), latitud=request.GET.get('latitud'), campo=campo)
            localizacion.save()

            mapbox_access_token = 'pk.eyJ1IjoicGFibG9kb25hdiIsImEiOiJjbGM3aW53bGYxNjR1M29wNjhiM3pmYzMwIn0.b2gpIbdHSeTw4oAdQcgMgQ'

            fig = go.Figure(go.Scattermapbox(
                lat=[float(localizacion.latitud)],
                lon=[float(localizacion.longitud)],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=14
                ),
            ))

            fig.update_layout(
                hovermode='closest',
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=go.layout.mapbox.Center(
                        lat=float(localizacion.latitud),
                        lon=float(localizacion.longitud)
                    ),
                    pitch=0,
                    zoom=15,
                    style="outdoors"
                ),
                margin={"r": 5, "t": 0, "l": 5, "b": 0}
            )

            map = fig.to_html()

            localizacion.delete()

            context = {'map': map, 'campo': campo, 'lat': request.GET.get('latitud'), 'long': request.GET.get('longitud')}

            return render(request, "cultivos/add_localizacion.html", context)

    if request.method == "POST":
        campo = Campo.objects.get(id = pk)
        geolocator = Nominatim(user_agent="geoapiExercises")
        longitud = request.POST.get('hiddenLongitud')
        latitud = request.POST.get('hiddenLatitud')
        location = geolocator.reverse(latitud+","+longitud)
        address = location.raw['address']
        city = address.get('province', '')
        country = address.get('country', '')
        localizacion = Localizacion(pais=country, ciudad=city, longitud=longitud, latitud=latitud, campo=campo)
        localizacion.save()
        messages.success(request, 'El terreno se ha creado correctamente.')
        return redirect("https://adnana.pythonanywhere.com/cultivos/campos/")

    return render(request, "cultivos/add_localizacion.html", {'campo': campo})

#Función que permite redirigir a la plantilla para crear un nuevo campo
@login_required(login_url='/accounts/login/')
def NuevoCampo(request):
    if request.method == "POST":
        form = AddCampo(request.POST)
        login_agricultor = Agricultor.objects.get(user = request.user)
        campo = Campo(num_ha=request.POST["num_ha"], login_agricultor=login_agricultor, volumen_agua_disp=request.POST["volumen_agua_disp"], tipo_riego=request.POST["tipo_riego"])
        campo.save()
        return redirect("https://adnana.pythonanywhere.com/cultivos/campos/addLocalizacion/" + str(campo.id))
    form = AddCampo()
    return render(request, "cultivos/add_campo.html", {"form": form})

#Función que permite redirigir a la plantilla para borrar un campo
@login_required(login_url='/accounts/login/')
def BorrarCampo(request, pk):
    campo = Campo.objects.get(id = pk)
    if request.method == 'POST':
        campo.delete()
        messages.success(request, 'El campo ha sido borrado con éxito.')
        return redirect('/')
    return render(request, "/", {'form': campo})

#Función que permite redirigir a la plantilla para cosechar un campo
@login_required(login_url='/accounts/login/')
def CosecharCampo(request, pk):
    campo = Campo.objects.get(id = pk)
    if request.method == 'POST':

        for c in campo.CULTIVOS.all():
            cultivos_campo = CultivosCampo.objects.get(campo=campo,cultivo=c)
            ha_cosechadas = float("{:.2f}".format(float(cultivos_campo.ha_sembradas) * 0.9))
            produccion = float("{:.2f}".format(float(float(c.kg_ha) * float(ha_cosechadas)) / 1000.0))
            rendimiento = float("{:.2f}".format(float((produccion * 1000) / ha_cosechadas)))
            historico = HistoricoCultivo(cultivo=cultivos_campo.cultivo, campo=cultivos_campo.campo, campanya_sembrado=cultivos_campo.campanya_sembrado, ha_sembradas=cultivos_campo.ha_sembradas, ha_cosechadas=ha_cosechadas, produccion=produccion, rendimiento=rendimiento)
            historico.save()

        campo.cosechar()
        messages.success(request, 'El campo ha sido cosechado con éxito.')
        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk))
    return render(request, "/", {'form': campo})

# Obtiene el rendimiento medio de un cultivo en un campo en base a los datos almacenados en el histórico
def getRendimientoMedioCultivo(_campo, _cultivo):
    rendimientoMedio = float(0)
    rendimientosCultivo = list(HistoricoCultivo.objects.filter(campo = _campo, cultivo=_cultivo).values_list('rendimiento', flat=True)) # Obtiene únicamente el atributo rendimiento

    if rendimientosCultivo:
        for rendimiento in rendimientosCultivo:
            rendimientoMedio += float(rendimiento)

        rendimientoMedio /= len(rendimientosCultivo)

    return float(rendimientoMedio)

# Obtiene la lista de objetos Cultivo que se han plantado en un campo
def getCultivosSembrados(_cultivosSembrados):
    cultivos = []

    if _cultivosSembrados:
        for cultivo in _cultivosSembrados:
            cultivos.append(cultivo.cultivo)

        cultivos = list(dict.fromkeys(cultivos)) #Elimina duplicados
        return cultivos
    return None

# Obtiene la lista de objetos Cultivo que se han sembrado en años anteriores y que no han sido sembrados en la campaña (año) actual
def getCultivosDeHistoricoNoSembrados(_campo, _historicosCultivosCampo):
    cultivosNoSembrados = []
    cultivosSembradosCampanyaActual = list(_campo.CULTIVOS.all())
    historicosCultivos = getCultivosSembrados(_historicosCultivosCampo)

    if cultivosSembradosCampanyaActual:
        if historicosCultivos:
            historicosCultivos = set(historicosCultivos)
            cultivosSembradosCampanyaActual = set(cultivosSembradosCampanyaActual)
            cultivosNoSembrados = list(historicosCultivos - cultivosSembradosCampanyaActual) # Eliminar de la primera lista las ocurrencias de cultivos que hay en la segunda

            return cultivosNoSembrados
    return None

# Obtiene el precio por hectárea a partir del rendimiento medio del cultivo(Kg/ha) y el precio del cultivo(€/Kg)
def getPreciosPorHectareaCultivos(_campo, _cultivosCampo):
    preciosCultivos = []

    if _cultivosCampo:
        for cultivo in _cultivosCampo:
            preciosCultivos.append(getRendimientoMedioCultivo(_campo, cultivo) * float(cultivo.precio_kg))

        return preciosCultivos
    return None

# Obtiene las hectáreas libres de un campo
def getHectareasLibresCampo(_campo):
    ha_ocupadas = float(0)
    ha_libres = float(0)
    cultivosCampo = _campo.CULTIVOS.all()

    if cultivosCampo:
        for cultivo in cultivosCampo:
            cultivo_campo = CultivosCampo.objects.get(campo=_campo,cultivo=cultivo)
            ha_ocupadas += float(cultivo_campo.ha_sembradas)

    ha_libres = float(_campo.num_ha) - ha_ocupadas

    return float(ha_libres)

# Obtiene la lista de los cultivos a sembrar en el campo con las hectáreas recomendadas para obtener el beneficio máximo
def calcularDistribucionOptimaCampo(_idCampo):
    campo = Campo.objects.get(id = _idCampo)
    cultivosCampo = getCultivosDeHistoricoNoSembrados(campo, HistoricoCultivo.objects.filter(campo = campo))

    if cultivosCampo:
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

        return results
    return None

#Función que devuelve cierto si un cultivo ha sido asignado ya a un campo.
def cultivoEnCampoRepetido(cultivo, campo):
    if CultivosCampo.objects.filter(cultivo=cultivo, campo=campo).exists():
        return True
    else:
        return False

#Función que devuelve cierto si un cultivo está repetido.
def cultivoRepetido(nombreCultivo):
    if Cultivo.objects.all().filter(nombre=nombreCultivo).exists():
        return True
    else:
        return False

#Función que permite añadir un cultivo a un campo específico.
def AddCultivoToCampo(request, pk):
    if request.method == "POST":
        cultivo = Cultivo.objects.get(id = request.POST["idCultivo"])
        campo = Campo.objects.get(id = pk)
        if getHectareasLibresCampo(campo) < float(request.POST["hectareas_sembradas"]):
            messages.error(request, "Error. El número de hectáreas del cultivo debe de ser igual o menor al de hectáreas disponibles en el campo.")
        else:
            if cultivoEnCampoRepetido(cultivo, campo):
                messages.error(request, "Error. El cultivo que has intentado añadir ya se encuentra en el terreno.")
            else:
                cultivoCampo = CultivosCampo(cultivo=cultivo, campo=campo, campanya_sembrado=request.POST["campanya_sembrado"], ha_sembradas=request.POST["hectareas_sembradas"])
                cultivoCampo.save()
                messages.success(request, "El cultivo se ha asignado al campo.")
        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk))
    campo = Campo.objects.get(id = pk)
    cultivos = Cultivo.objects.all()
    results = calcularDistribucionOptimaCampo(pk)

    return render(request, "cultivos/add_cultivo_to_campo.html", context={'cultivos': cultivos, 'campo': campo, 'results': results})

# Obtiene el total de hectareas que tienen todos los campos de un agricultor
def getTotalHectareasCampos(_campos):
    total_ha_campos = float(0)

    if _campos:
        for campo in _campos:
            total_ha_campos += float(campo.num_ha)

    return total_ha_campos

# Obtiene el total de hectáreas ocupadas en los campos de un agricultor
def getTotalHectareasOcupadas(_campos):
    ha_ocupadas_campo = float(0)
    total_ha_ocupadas_campos = float(0)

    if _campos:
        for campo in _campos:
            ha_ocupadas_campo = float(campo.num_ha) - getHectareasLibresCampo(campo)
            total_ha_ocupadas_campos += ha_ocupadas_campo

    return total_ha_ocupadas_campos

# Obtiene el total de hectáreas ocupadas por un agricultor en porcentaje
def getPorcentajeOcupacionCampos(_campos):
    total_ha_ocupadas = getTotalHectareasOcupadas(_campos)
    total_ha_tienen_campos = getTotalHectareasCampos(_campos)
    total_porcentaje_ha_ocupadas_campos = float(0)

    if total_ha_tienen_campos > 0:
            total_porcentaje_ha_ocupadas_campos = (total_ha_ocupadas / total_ha_tienen_campos) * 100

    return round(total_porcentaje_ha_ocupadas_campos)

# Obtiene el total de hectáreas ocupadas por la lista de campos de histórico
def getHectareasOcupadasCampos(_campos):
    total_ha_ocupadas_campos = float(0)

    if _campos:
        for campo in _campos:
            total_ha_ocupadas_campos += float(campo.ha_sembradas)

    return total_ha_ocupadas_campos

# Obtiene la diferencia de hectáreas ocupadas de este año con respecto al año anterior
def getDiferenciaHectareasOcupadas(_campos):
    total_ha_ocupadas_anyo_anterior = float(0)
    total_ha_ocupadas_anyo_actual = float(0)
    diferencia_ha_ocupadas = float(0)
    today = datetime.date.today()
    anyo_anterior = decimal.Decimal(today.year) - 1

    campos_anyo_anterior = HistoricoCultivo.objects.filter(campanya_sembrado = anyo_anterior, campo__in=_campos)
    if campos_anyo_anterior:
        total_ha_ocupadas_anyo_anterior = getHectareasOcupadasCampos(campos_anyo_anterior)

    campos_anyo_actual = CultivosCampo.objects.filter(campo__in=_campos)
    if campos_anyo_actual:
        total_ha_ocupadas_anyo_actual = getHectareasOcupadasCampos(campos_anyo_actual)

    diferencia_ha_ocupadas = total_ha_ocupadas_anyo_actual - total_ha_ocupadas_anyo_anterior

    return round(diferencia_ha_ocupadas, 2);

# Obtiene la estimación de la producción actual hasta el momento
def getEstimacionProduccionActual(_campos):
    produccionTotal = float(0)
    cultivosSembrados = CultivosCampo.objects.filter(campo__in=_campos)

    if cultivosSembrados:
        for cultivoSembrado in cultivosSembrados:
            produccionTotal += float((cultivoSembrado.ha_sembradas * Cultivo.objects.get(id=cultivoSembrado.cultivo.id).kg_ha) / 1000)
    return produccionTotal

# Obtiene la producción del año anterior
def getProduccionAnyoAnterior(_campos):
    produccionTotal = float(0)
    today = datetime.date.today()
    anyo_anterior = decimal.Decimal(today.year) - 1

    cultivosSembradosAnyoAnterior = HistoricoCultivo.objects.filter(campanya_sembrado = anyo_anterior, campo__in=_campos)

    if cultivosSembradosAnyoAnterior:
        for cultivoSembrado in cultivosSembradosAnyoAnterior:
            produccionTotal +=  float(cultivoSembrado.produccion)

    return produccionTotal

# Obtiene el porcentaje de diferencia de la producción entre el año actual y el año anterior
def getPorcentajeDiferenciaProduccion(_campos, _estimacion_produccion_actual):
    diferencia_produccion = float(0)
    produccion_anyo_anterior = getProduccionAnyoAnterior(_campos)

    if produccion_anyo_anterior:
        if produccion_anyo_anterior > 0 :
            diferencia_produccion = ((_estimacion_produccion_actual - produccion_anyo_anterior) / produccion_anyo_anterior) * 100
    return round(diferencia_produccion, 2)

# Obtiene la produccion de un cultivo sembrado en el año actual
def getProduccionCultivo(_cultivoSembrado):
    produccion = float(0)

    produccion = float(_cultivoSembrado.ha_sembradas) * float(_cultivoSembrado.cultivo.kg_ha)

    return produccion

# Obtiene la estimación del beneficio actual hasta el momento
def getEstimacionBeneficioActual(_campos):
    beneficioTotal = float(0)
    cultivosSembrados = CultivosCampo.objects.filter(campo__in=_campos)

    if cultivosSembrados:
        for cultivoSembrado in cultivosSembrados:
            beneficioTotal += (getProduccionCultivo(cultivoSembrado) * float(Cultivo.objects.get(id=cultivoSembrado.cultivo.id).precio_kg))
    return round(beneficioTotal, 2)

# Obtiene el beneficio del año anterior
def getBeneficioAnyoAnterior(_campos):
    beneficioTotal = float(0)
    today = datetime.date.today()
    anyo_anterior = decimal.Decimal(today.year) - 1

    cultivosSembradosAnyoAnterior = HistoricoCultivo.objects.filter(campanya_sembrado = anyo_anterior, campo__in=_campos)

    if cultivosSembradosAnyoAnterior:
        for cultivoSembrado in cultivosSembradosAnyoAnterior:
            produccionEnKg = cultivoSembrado.produccion * 1000
            beneficioTotal += float(produccionEnKg * Cultivo.objects.get(id=cultivoSembrado.cultivo.id).precio_kg)

    return beneficioTotal

# Obtiene el porcentaje de diferencia de beneficio entre el año actual y el año anterior
def getPorcentajeDiferenciaBeneficio(_campos, _estimacion_beneficio_actual):
    diferencia_beneficio = float(0)
    beneficio_anyo_anterior = getBeneficioAnyoAnterior(_campos)

    if beneficio_anyo_anterior:
        if beneficio_anyo_anterior > 0:
            diferencia_beneficio = ((_estimacion_beneficio_actual - beneficio_anyo_anterior) / beneficio_anyo_anterior) * 100

    return round(diferencia_beneficio, 2)

# Obtiene una lista con todos los años en los que se ha obtenido la producción de un cultivo
def getAnyosProduccionCultivo(_cultivo, _campos):
    years = []
    historicosCultivos = HistoricoCultivo.objects.filter(cultivo = _cultivo, campo__in=_campos)

    if historicosCultivos:
        for historicoCultivo in historicosCultivos:
            years.append(str(historicoCultivo.campanya_sembrado))

        years = list(dict.fromkeys(years)) #Elimina duplicados
        years.sort()

        return years
    return None

# Obtiene una lista con la producción total por años de un cultivo
def getProduccionTotalPorAnyoCultivo(_cultivo, _years, _campos):
    producciones = []

    if _years:
        for year in _years:
            sumaProduccion = decimal.Decimal(0)
            historicosCultivos = HistoricoCultivo.objects.filter(cultivo = _cultivo, campanya_sembrado=decimal.Decimal(year), campo__in=_campos)
            if historicosCultivos:
                for historicoCultivo in historicosCultivos:
                    sumaProduccion += historicoCultivo.produccion

                producciones.append(round(sumaProduccion,0))

        return producciones
    return None

# Obtiene una lista con la visibilidad de los botones que aparecen en el gráfico de lineas
def getGraphButtonsVisibilityList(_cultivoButton, _cultivos):
    visibilityList = []

    if _cultivos:
        for cultivo in _cultivos:
            if cultivo == _cultivoButton:
                visibilityList.append(True)
            else:
                visibilityList.append(False)

        return visibilityList
    return None

# Crea el gráfico de lineas con la producción/año de cada cultivo plantado por un agricultor
def drawGraficoLineasProduccionCultivo(_campos):
    years = []
    producciones = []
    buttonsList = []
    cultivosSembrados = getCultivosSembrados(HistoricoCultivo.objects.filter(campo__in=_campos))

    graph = go.Figure()
    if cultivosSembrados:
        for cultivoSembrado in cultivosSembrados:
            years = getAnyosProduccionCultivo(cultivoSembrado, _campos)

            if years:
                producciones = getProduccionTotalPorAnyoCultivo(cultivoSembrado, years, _campos)

                if producciones:
                    if cultivosSembrados.index(cultivoSembrado) == 0:
                        graph.add_trace(
                            go.Scatter(
                                name=cultivoSembrado.nombre,
                                x=years,
                                y=producciones)
                        )
                    else:
                        graph.add_trace(
                            go.Scatter(
                                name=cultivoSembrado.nombre,
                                x=years,
                                y=producciones,
                                visible=False)
                        )

                    buttonsList.append(
                        dict(label=cultivoSembrado.nombre,
                             args=[{"visible": getGraphButtonsVisibilityList(cultivoSembrado, cultivosSembrados)}]
                        )
                    )

        graph.update_layout(xaxis_title='Año', yaxis_title='Producción (Tm)', height=350, margin=dict(l=50, r=30, t=10, b=20),
                paper_bgcolor="#b2d2fd",
                showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True),
                updatemenus=[
                dict(
                    buttons=list(buttonsList),
                    x = 0.0,
                    xanchor = 'left',
                    y = 1.2,
                    yanchor = 'top',
                )]
        )

        return plot({'data': graph}, output_type='div')
    return None

#Función que permite generar una gráfica de producción por año.
@login_required(login_url='/accounts/login/')
def ShowIndex(request):
    login_agricultor = Agricultor.objects.get(user = request.user)
    mis_campos = Campo.objects.filter(login_agricultor = login_agricultor)
    porcentaje_total_ha_ocupadas = getPorcentajeOcupacionCampos(mis_campos)
    diferencia_ha_ocupadas = getDiferenciaHectareasOcupadas(mis_campos)
    estimacion_produccion_actual = getEstimacionProduccionActual(mis_campos)
    diferencia_produccion = getPorcentajeDiferenciaProduccion(mis_campos, estimacion_produccion_actual)
    estimacion_beneficio_actual = getEstimacionBeneficioActual(mis_campos)
    diferencia_beneficio = getPorcentajeDiferenciaBeneficio(mis_campos, estimacion_beneficio_actual)
    plotly_plot_obj = drawGraficoLineasProduccionCultivo(mis_campos)

    return render(request, "cultivos/index.html", context={'porcentaje_total_ha_ocupadas':porcentaje_total_ha_ocupadas,
        'estimacion_produccion_actual': estimacion_produccion_actual, 'diferencia_produccion': diferencia_produccion,
        'estimacion_beneficio_actual': estimacion_beneficio_actual, 'diferencia_beneficio': diferencia_beneficio,
        'diferencia_ha_ocupadas': diferencia_ha_ocupadas,'plot_div': plotly_plot_obj})

#Función que permite generar un mapa con los terrenos de un agricultor.
@login_required(login_url='/accounts/login/')
def ShowMisTerrenos(request):
    login_agricultor = Agricultor.objects.get(user = request.user)
    mis_campos = Campo.objects.filter(login_agricultor = login_agricultor)
    localizaciones = Localizacion.objects.filter(campo__in=mis_campos)

    mapbox_access_token = 'pk.eyJ1IjoicGFibG9kb25hdiIsImEiOiJjbGM3aW53bGYxNjR1M29wNjhiM3pmYzMwIn0.b2gpIbdHSeTw4oAdQcgMgQ'

    fig = go.Figure(go.Scattermapbox())

    for localizacion in localizaciones:
        fig.add_scattermapbox(
            lat=[localizacion.latitud],
            lon=[localizacion.longitud],
            text ='Campo: ' + str(localizacion.display_campo()),
            mode='markers',
            name='Campo: ' + str(localizacion.display_campo()),
            marker=go.scattermapbox.Marker(
                size=9,
            )
        )

    if not mis_campos:
        latit = decimal.Decimal(40.34167)
        longit = decimal.Decimal(-1.10691)
    else:
        latit=localizaciones[0].latitud
        longit=localizaciones[0].longitud

    fig.update_layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=float(latit),
                lon=float(longit)
            ),
            pitch=0,
            zoom=12,
            style="outdoors"
        ),
        margin={"r": 5, "t": 15, "l": 5, "b": 0}
    )

    chart = fig.to_html()

    return render(request, "cultivos/show_campos.html", context={'chart': chart, 'mis_campos': mis_campos})

#Clase detallada que representa los campos detallados
class CampoDetailView(generic.DetailView):
    model = Campo
    context_object_name = 'mis_campos_detallados'

    """ Función que permite añadir campos a la vista detallada """
    def get_context_data(self, *args, **kwargs):

        media_riego_campo = decimal.Decimal(0.0)
        num_cultivos = 0

        context = super(CampoDetailView, self).get_context_data(*args, **kwargs)
        context['localizacion'] = Localizacion.objects.all()
        context['campo'] = get_object_or_404(Campo, id=self.kwargs['pk'])
        context['localizacion_campo'] = get_object_or_404(Localizacion, campo=context['campo'])

        source = urllib.request.urlopen('https://api.openweathermap.org/data/2.5/forecast?lat=' + str(context['localizacion_campo'].latitud) + '&lon=' + str(context['localizacion_campo'].longitud) + '&appid=269a92ced72ee673fa247096c0c54faa').read()
        forecast = json.loads(source)

        for c in context['campo'].CULTIVOS.all():
            media_riego_campo += c.riego_dia
            num_cultivos += 1

        if num_cultivos > 0:
            media_riego_campo = media_riego_campo / decimal.Decimal(num_cultivos)
            media_riego_campo = (3 * media_riego_campo) / 24
        else:
            media_riego_campo = decimal.Decimal(0.0)

        for list in forecast['list']:
            list['main']['temp'] = float("{:.2f}".format(list['main']['temp'] - 273.15))
            day = datetime.datetime.fromtimestamp(list['dt']).strftime('%d-%m-%Y')
            list['main']['day'] = day
            hour = datetime.datetime.fromtimestamp(list['dt']).strftime('%H:%M')
            list['main']['hour'] = hour

            try:
                list['rain'] = list['rain']['3h']
            except KeyError:
                list['rain'] = 0.0

            if list['rain'] == 0.0:
                list['main']['riego'] = float("{:.4f}".format(float(media_riego_campo)))
            else:
                if list['rain'] < media_riego_campo:
                    list['main']['riego'] = float("{:.4f}".format(float(media_riego_campo) - list['rain']))
                else:
                    list['main']['riego'] = 0.0

        context['forecast'] = forecast

        source = urllib.request.urlopen('https://api.openweathermap.org/data/2.5/weather?lat=' + str(context['localizacion_campo'].latitud) + '&lon=' + str(context['localizacion_campo'].longitud) + '&appid=269a92ced72ee673fa247096c0c54faa').read()
        weather = json.loads(source)

        weather['main']['temp'] = float("{:.2f}".format(weather['main']['temp'] - 273.15))
        day = datetime.datetime.fromtimestamp(weather['dt']).strftime('%d-%m-%Y')
        weather['main']['day'] = day
        hour = datetime.datetime.fromtimestamp(weather['dt']).strftime('%H:%M')
        weather['main']['hour'] = hour

        context['weather'] = weather

        return context

#Clase que representa la vista para importar cultivos
class ImportCultivosView(View):
    """ Función que permite obtener la plantilla para importar cultivos """
    def get(self, request, pk, *args, **kwargs):
        return render(request, "cultivos/import_cultivos.html", {'form': ImportCultivoForm()})

    """ Función que permite añadir los cultivos a la base de datos """
    def post(self, request, pk, *args, **kwargs):
        cultivos_file = request.FILES["cultivos_file"]
        data=pd.read_csv(cultivos_file,sep=',')
        row_iter = data.iterrows()
        cultivos = [
            Cultivo(
                nombre = row['Name'],
                precio_kg = row['Price'],
                riego_dia = row['Water'],
                kg_ha = row['kg_ha'],
                tipo = row['Type']
            )
            for index, row in row_iter
        ]

        Cultivo.objects.bulk_create(cultivos)

        messages.success(request, 'Se han importado correctamente los cultivos.')
        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk) + "/addCultivoToCampo/")

#Clase que representa la vista para importar datos históricos de un cultivo
class ImportHistoricoCultivo(View):
    """ Función que permite obtener la plantilla para importar datos históricos de un cultivo """
    def get(self, request, pk, *args, **kwargs):
        return render(request, "cultivos/import_historico_cultivo.html", {'form': ImportHistoricoCultivoForm()})

    """ Función que permite añadir los cultivos a la base de datos """
    def post(self, request, pk, *args, **kwargs):
        historico_cultivo_file = request.FILES["historico_cultivo"]
        data=pd.read_csv(historico_cultivo_file,sep=',')
        row_iter = data.iterrows()
        historico_cultivo_campo = [
                HistoricoCultivo(
                    cultivo = Cultivo.objects.get(id = row['id_cultivo']),
                    campo = Campo.objects.get(id = pk),
                    campanya_sembrado = float(row['indice_tiempo']),
                    ha_sembradas = float(row['superficie_sembrada']),
                    ha_cosechadas = float(row['superficie_cosechada']),
                    produccion = float(row['produccion']),
                    rendimiento = float(row['rendimiento'])
                )
                for index, row in row_iter
            ]

        HistoricoCultivo.objects.bulk_create(historico_cultivo_campo)
        return redirect("https://adnana.pythonanywhere.com/cultivos/campo/"+ str(pk))

#Función que permite generar una mapa con un terreno concreto de un agricultor.
@login_required(login_url='/accounts/login/')
def mapaCampoDetallado(request, pk):

    campo = Campo.objects.get(id = pk)
    localizacion = Localizacion.objects.get(campo_id = pk)

    mapbox_access_token = 'pk.eyJ1IjoicGFibG9kb25hdiIsImEiOiJjbGM3aW53bGYxNjR1M29wNjhiM3pmYzMwIn0.b2gpIbdHSeTw4oAdQcgMgQ'

    fig = go.Figure(go.Scattermapbox(
        lat=[localizacion.latitud],
        lon=[localizacion.longitud],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
    ))

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=localizacion.latitud,
                lon=localizacion.longitud
            ),
            pitch=0,
            zoom=15,
            style="outdoors"
        ),
        margin={"r": 5, "t": 0, "l": 5, "b": 0}
    )

    map = fig.to_html()

    context = {'map': map, 'id': pk}

    return render(request, 'cultivos/campo_map.html', context)

#Función que permite generar una gráfica con los cultivos de un terreno.
@login_required(login_url='/accounts/login/')
def cultivosGraph(request, pk):

    ha_ocupadas = decimal.Decimal(0)
    ha_libres = decimal.Decimal(0)

    cam = Campo.objects.get(id = pk)

    cultivos = []
    valores_ha_ocupadas = []

    for c in cam.CULTIVOS.all():
        cultivos.append(c.nombre)
        cultivo_campo = CultivosCampo.objects.get(campo=cam,cultivo=c)
        valores_ha_ocupadas.append(cultivo_campo.ha_sembradas)
        ha_ocupadas += cultivo_campo.ha_sembradas

    ha_libres = cam.num_ha - ha_ocupadas

    cultivos.append('Hectáreas libres')
    valores_ha_ocupadas.append(ha_libres)

    fig = go.Figure(data=[go.Pie(labels=cultivos, values=valores_ha_ocupadas)])

    chart = fig.to_html()

    context = {'chart': chart, 'id': pk}

    return render(request, 'cultivos/campo_cultivos.html', context)