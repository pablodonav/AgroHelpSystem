# Generated by Django 4.0.6 on 2023-01-04 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultivos', '0002_alter_campo_num_ha_alter_campo_volumen_agua_disp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cultivo',
            name='kg_ha',
            field=models.DecimalField(decimal_places=5, default=1, max_digits=17),
            preserve_default=False,
        ),
    ]