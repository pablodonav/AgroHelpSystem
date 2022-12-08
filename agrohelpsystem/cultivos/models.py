# ------------------------------------------------------------------------------------------------------
# Created By  : Pablo Doñate y Adnana Dragut
# Created Date: 02/12/2022
# version ='1.0'
# ------------------------------------------------------------------------------------------------------
# File: models.py
# ------------------------------------------------------------------------------------------------------
""" Fichero que contiene los modelos necesarios para crear la base de datos """
# ------------------------------------------------------------------------------------------------------
from django.db import models
from django.contrib.auth.admin import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

# Modelo que representa la tabla Localización.
class Localizacion(models.Model):
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

    """ String que representa el objeto Localizacion """
    def __str__(self):
        return f'{self.id}'

    """ String que representa el id del campo de la localización """
    def display_campo(self):
        return self.campo.id
    display_campo.short_description = 'idCampo'

# Modelo que representa la tabla Agricultor.
class Agricultor(models.Model):
    class Meta:
        verbose_name_plural = 'Agricultores'

    # Atributos
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=255, null=True, blank=True)

    """ String que representa el objeto Agricultor """
    def __str__(self):
        return self.user.username

    """ Función que muestra si el agricultor es superusuario """
    def display_superuser(self):
        return self.user.is_superuser
    display_superuser.short_description = 'is_superuser'

    """ Función que obtiene la contraseña del usuario agricultor """
    def display_password(self):
        return self.user.password
    display_password.short_description = 'password'

# Función que permite crear un usuario Agricultor.
@receiver(post_save, sender=User)
def create_user_agricultor(sender, instance, created, **kwargs):
    if created:
        Agricultor.objects.create(user=instance)
    instance.agricultor.save()

# Modelo que representa la tabla Cultivo.
class Cultivo(models.Model):
    class Meta:
        db_table = 'CULTIVO'

    # Atributos
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, null=False)

    """ String que representa el objeto Cultivo """
    def __str__(self):
        return f'{self.id}'

# Modelo que representa la tabla Campo.
class Campo(models.Model):
    class Meta:
        db_table = 'CAMPO'

    # Atributos
    id = models.AutoField(primary_key=True)
    num_ha = models.DecimalField(max_digits=10, decimal_places=3)
    login_agricultor = models.ForeignKey('Agricultor', on_delete=models.CASCADE, null=False)
    CULTIVOS = models.ManyToManyField('Cultivo')

    """ String que representa el objeto Campo """
    def __str__(self):
        return f'{self.id}'

    """ Función que obtiene el agricultor propietario del Campo """
    def display_propietario(self):
        return self.login_agricultor
    display_propietario.short_description = 'propietario'

    """ Función que obtiene todos los cultivos del Campo en string """
    def display_cultivos(self):
        cultivos = ""
        for c in self.CULTIVOS.all():
            if cultivos == "":
                cultivos = c.nombre
            else:
                cultivos = cultivos + ", " + c.nombre
        return cultivos
    display_cultivos.short_description = 'cultivos'

    """ Función que obtiene la url asociado a un campo específico """
    def get_absolute_url(self):
        return reverse('terreno-detail', args=[str(self.id)])

    """ Función que obtiene la variable cultivos de un campo """
    def cultivos_set(self):
        return self.CULTIVOS

# Modelo que representa la información a almacenar del fichero csv.
class CultivoBulkUpload(models.Model):
  date_uploaded = models.DateTimeField(auto_now=True)
  csv_file = models.FileField(upload_to='cultivo/bulkupload/')