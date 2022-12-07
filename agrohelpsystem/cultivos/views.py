from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views import generic
from .models import Cultivo, Localizacion, Campo, Agricultor
from .forms import AddCultivo, AddCampo, AddLocalizacion, ImportCultivoForm
import pandas as pd
from django.views.generic.base import View

@login_required(login_url='/accounts/login/')
def NuevoCultivo(request):
    if request.method == "POST":
        form = AddCultivo(request.POST)
        if form.is_valid():
            cultivo = form.save(commit=False)
            cultivo.save()
            return redirect("https://adnana.pythonanywhere.com/cultivos/campos/")
    form = AddCultivo()
    return render(request, "cultivos/add_cultivo.html", {"form": form})

@login_required(login_url='/accounts/login/')
def NuevaLocalizacion(request, pk):
    if request.method == "POST":
        form = AddLocalizacion(request.POST)
        if form.is_valid():
            campo = Campo.objects.get(id = pk)
            localizacion = Localizacion(pais=request.POST["pais"], ciudad=request.POST["ciudad"], longitud=request.POST["longitud"], latitud=request.POST["latitud"], campo=campo)
            localizacion.save()
            return redirect("https://adnana.pythonanywhere.com/cultivos/")
    form = AddLocalizacion()
    return render(request, "cultivos/add_localizacion.html", {"form": form})

@login_required(login_url='/accounts/login/')
def NuevoCampo(request):
    if request.method == "POST":
        form = AddCampo(request.POST)
        login_agricultor = Agricultor.objects.get(user = request.user)
        campo = Campo(num_ha=request.POST["num_ha"], login_agricultor=login_agricultor)
        campo.save()
        for cultivo in request.POST.getlist("CULTIVOS"):
            culti = Cultivo.objects.get(nombre = cultivo)
            campo.CULTIVOS.add(culti)
        return redirect("https://adnana.pythonanywhere.com/cultivos/campos/addLocalizacion/" + str(campo.id))
    form = AddCampo()
    return render(request, "cultivos/add_campo.html", {"form": form})

@login_required(login_url='/accounts/login/')
def BorrarCampo(request, pk):
    campo = Campo.objects.get(id = pk)
    if request.method == 'POST':
        campo.delete()
        return redirect('/')
    return render(request, "/", {'form': campo})

class CultivosListView(generic.ListView):
    model = Cultivo
    context_object_name = 'mis_cultivos'
    queryset = Cultivo.objects.all()
    template_name = 'cultivos/add_campo.html'

class TerrenoListView(generic.ListView):
    model = Campo
    context_object_name = 'mis_terrenos'
    template_name = 'cultivos/index.html'
    paginate_by = 3

    def get_queryset(self):
        login_agricultor = Agricultor.objects.get(user = self.request.user)
        return Campo.objects.filter(login_agricultor = login_agricultor)

class TerrenoDetailView(generic.DetailView):
    model = Campo
    context_object_name = 'mis_terrenos_detallados'

    def get_context_data(self, *args, **kwargs):
        context = super(TerrenoDetailView, self).get_context_data(*args, **kwargs)

        context['localizacion'] = Localizacion.objects.all()

        return context

class ImportCultivosView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "cultivos/importCultivo.html", {"form": ImportCultivoForm()})

    def post(self, request, *args, **kwargs):
        cultivos_file = request.FILES["cultivos_file"]
        data=pd.read_csv(cultivos_file,sep=';')
        row_iter = data.iterrows()
        cultivos = [
            Cultivo(
                nombre = row['Name']
            )
            for index, row in row_iter
        ]
        Cultivo.objects.bulk_create(cultivos)
        return redirect("https://adnana.pythonanywhere.com/cultivos/campos/")