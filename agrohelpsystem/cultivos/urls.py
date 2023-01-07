# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: urls.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene las urls de la app cultivos """
# ------------------------------------------------------------------------------------------------------
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.ShowIndex), name='index'),
    path('campos/', login_required(views.ShowMisTerrenos), name='campos'),
    path('campo/<pk>/', login_required(views.CampoDetailView.as_view()), name='campo-detail'),
    path('campos/addCampo/', login_required(views.NuevoCampo), name='add-campo'),
    path('campo/<pk>/addCultivoToCampo/', login_required(views.AddCultivoToCampo), name='add-cultivo-to-campo'),
    path('campos/<pk>/addCultivo/', login_required(views.NuevoCultivo), name='add-cultivo'),
    path('campos/addLocalizacion/<pk>/', login_required(views.NuevaLocalizacion), name='add-localizacion'),
    path('campos/<pk>/import_cultivos/', login_required(views.ImportCultivosView.as_view()),  name='import-cultivo'),
    path('campos/<pk>/import_historico_cultivo/', login_required(views.ImportHistoricoCultivo.as_view()),  name='import-historico-cultivo'),
    path('campo/<pk>/delete/', login_required(views.BorrarCampo), name='borrar_campo'),
    path('campo/<pk>/cosechar/', login_required(views.CosecharCampo), name='cosechar_campo'),
    path('mapaterreno/<pk>/', login_required(views.mapaCampoDetallado), name='map'),
    path('cultivosterreno/<pk>/', login_required(views.cultivosGraph), name='chart')
]