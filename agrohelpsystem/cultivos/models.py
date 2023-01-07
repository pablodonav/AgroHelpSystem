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
    longitud = models.DecimalField(max_digits=17, decimal_places=5)
    latitud = models.DecimalField(max_digits=17, decimal_places=5)
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

    CULTIVO_REGADIO = 'REGADIO'
    CULTIVO_SECANO = 'SECANO'
    TIPO_CULTIVO_CHOICES = [
        (CULTIVO_REGADIO, 'Cultivo de regadío'),
        (CULTIVO_SECANO, 'Cultivo de secano'),
    ]

    # Atributos
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=255, null=False)
    precio_kg = models.DecimalField(max_digits=17, decimal_places=5, null=False)
    riego_dia = models.DecimalField(max_digits=17, decimal_places=5, null=False)
    kg_ha = models.DecimalField(max_digits=17, decimal_places=5, null=False)
    tipo = models.CharField(max_length=255, choices=TIPO_CULTIVO_CHOICES, default=CULTIVO_REGADIO, null=False)

    """String que representa el objeto Cultivo"""
    def __str__(self):
        return f'{self.id}'

# Modelo que representa la tabla Campo.
class Campo(models.Model):
    class Meta:
        db_table = 'CAMPO'

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

    # Atributos
    id = models.AutoField(primary_key=True)
    num_ha = models.DecimalField(max_digits=17, decimal_places=5)
    login_agricultor = models.ForeignKey('Agricultor', on_delete=models.CASCADE, null=False)
    volumen_agua_disp = models.DecimalField(max_digits=17, decimal_places=5, null=True)
    tipo_riego = models.CharField(max_length=255, choices=RIEGO_CHOICES, default=RIEGO_POR_SUPERFICIE, null=False)
    CULTIVOS = models.ManyToManyField('Cultivo', through='CultivosCampo', related_name='Cultivos')
    HISTORICO_CULTIVO = models.ManyToManyField('Cultivo', through='HistoricoCultivo', related_name='Historico')

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
        return reverse('campo-detail', args=[str(self.id)])

    """ Función que obtiene la variable cultivos de un campo """
    def cultivos_set(self):
        return self.CULTIVOS

    """ Función que cosecha (elimina) los cultivos de un campo. """
    def cosechar(self):
        for c in self.CULTIVOS.all():
            self.CULTIVOS.remove(c)

# Modelo que representa la tabla Cultivos_Campo.
class CultivosCampo(models.Model):
    id = models.AutoField(primary_key=True)
    cultivo = models.ForeignKey('Cultivo', on_delete=models.CASCADE, null=False)
    campo = models.ForeignKey('Campo', on_delete=models.CASCADE, null=False)
    campanya_sembrado = models.DecimalField(max_digits=4, decimal_places=0)
    ha_sembradas = models.DecimalField(max_digits=17, decimal_places=5, null=False)

    class Meta:
        db_table = 'CULTIVOS_CAMPO'
        unique_together = (('cultivo', 'campo', 'campanya_sembrado'),)

    """ String que representa el objeto CultivosCampo """
    def __str__(self):
        return f'{self.id} + {self.campo} + {self.cultivo}'

# Modelo que representa la tabla histórico de los cultivos de un campo.
class HistoricoCultivo(models.Model):
    id = models.AutoField(primary_key=True)
    cultivo = models.ForeignKey('Cultivo', on_delete=models.CASCADE, null=False)
    campo = models.ForeignKey('Campo', on_delete=models.CASCADE, null=False)
    campanya_sembrado = models.DecimalField(max_digits=4, decimal_places=0, null=False)
    ha_sembradas = models.DecimalField(max_digits=17, decimal_places=5, null=False)
    ha_cosechadas = models.DecimalField(max_digits=17, decimal_places=5, null=True)
    produccion = models.DecimalField(max_digits=17, decimal_places=5, null=True)
    rendimiento = models.DecimalField(max_digits=17, decimal_places=5, null=True)

    class Meta:
        db_table = 'HISTORICO_CULTIVO'
        unique_together = (('cultivo', 'campo', 'campanya_sembrado'),)

    """ String que representa el objeto HistoricoCultivo """
    def __str__(self):
        return f'{self.id} + {self.campo}'

# Modelo que representa la información a almacenar del fichero csv.
class CultivoBulkUpload(models.Model):
  date_uploaded = models.DateTimeField(auto_now=True)
  csv_file = models.FileField(upload_to='cultivo/bulkupload/')