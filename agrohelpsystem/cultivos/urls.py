from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(views.TerrenoListView.as_view()), name='index'),
    path('terreno/<pk>/', login_required(views.TerrenoDetailView.as_view()), name='terreno-detail'),
    path('campos/', views.NuevoCampo, name='campos'),
    path('campos/addCultivo/', views.NuevoCultivo, name='add-cultivo'),
    path('campos/addLocalizacion/<pk>/', views.NuevaLocalizacion, name='add-cultivo'),
    path('campos/import_cultivos/', login_required(views.ImportCultivosView.as_view()),  name='import-cultivo'),
    path('terreno/<pk>/delete/', views.BorrarCampo, name='borrar_campo')
]