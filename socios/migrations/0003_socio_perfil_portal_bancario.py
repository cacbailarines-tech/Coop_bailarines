from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0002_aportemensual_comprobante_archivo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='socio',
            name='banco_preferido',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='socio',
            name='cedula_titular_preferida',
            field=models.CharField(blank=True, max_length=13),
        ),
        migrations.AddField(
            model_name='socio',
            name='cuenta_bancaria_preferida',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='socio',
            name='nombre_preferido',
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name='socio',
            name='titular_cuenta_preferida',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
