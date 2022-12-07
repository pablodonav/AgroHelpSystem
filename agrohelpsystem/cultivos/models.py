from django.db import models
from django.contrib.auth.admin import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

# Modelo de Localización.
class Localizacion(models.Model):
    "Modelo que representa la tabla localización"
    class Meta:
        db_table = 'LOCALIZACION'
        verbose_name_plural = 'Localizaciones'

    # Atributos
    id = models.AutoField(primary_key=True)
    pais = models.CharField(max_length=255, null=False)
    ciudad = models.CharField(max_length=255, null=False)
    longitud = models.DecimalField(max_digits=10, decimal_places=3)
    latitud = models.DecimalField(max_digits=10, decimal_places=3)

    campo = models.OneToOneField('Campo', on_delete=models.CASCADE)

    def __str__(self):
        "String que representa el objeto Localizacion"
        return f'{self.id}'

    def display_campo(self):
        """
        Creates a string for the Login. This is required to display login in Admin.
        """
        return self.campo.id
    display_campo.short_description = 'idCampo'

# Modelo de Agricultor.
class Agricultor(models.Model):

    class Meta:
        verbose_name_plural = 'Agricultores'

    # Atributos
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def display_superuser(self):
        return self.user.is_superuser
    display_superuser.short_description = 'is_superuser'

    def display_password(self):
        return self.user.password
    display_password.short_description = 'password'

@receiver(post_save, sender=User)
def create_user_agricultor(sender, instance, created, **kwargs):
    if created:
        Agricultor.objects.create(user=instance)
    instance.agricultor.save()

# Modelo de Cultivo.
class Cultivo(models.Model):
    "Modelo que representa la tabla cultivo"
    class Meta:
        db_table = 'CULTIVO'

    # Atributos
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False)

    def __str__(self):
        "String que representa el objeto Cultivo"
        return f'{self.id}'

# Modelo de Campo.
class Campo(models.Model):
    "Modelo que representa la tabla campo"
    class Meta:
        db_table = 'CAMPO'

    # Atributos
    id = models.AutoField(primary_key=True)
    num_ha = models.DecimalField(max_digits=10, decimal_places=3)
    login_agricultor = models.ForeignKey('Agricultor', on_delete=models.CASCADE, null=False)

    CULTIVOS = models.ManyToManyField('Cultivo')

    def get_absolute_url(self):
        return reverse('terreno-detail', args=[str(self.id)])

    def cultivos_set(self):
        return self.CULTIVOS

    def __str__(self):
        "String que representa el objeto Campo"
        return f'{self.id}'

    def display_propietario(self):
        return self.login_agricultor
    display_propietario.short_description = 'propietario'

    def display_cultivos(self):
        cultivos = ""
        for c in self.CULTIVOS.all():
            if cultivos == "":
                cultivos = c.nombre
            else:
                cultivos = cultivos + ", " + c.nombre
        return cultivos
    display_cultivos.short_description = 'cultivos'

class CultivoBulkUpload(models.Model):
  date_uploaded = models.DateTimeField(auto_now=True)
  csv_file = models.FileField(upload_to='cultivo/bulkupload/')