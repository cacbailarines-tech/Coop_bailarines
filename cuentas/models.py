from django.db import models
from socios.models import Libreta, Periodo
from django.contrib.auth.models import User


class RifaMensual(models.Model):
    ESTADO_CHOICES = [('pendiente','Pendiente'),('realizada','Realizada'),('ganada','Ganada - Pagada'),('no_ganada','No Ganada')]
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='rifas')
    mes = models.IntegerField()
    anio = models.IntegerField()
    numeros_loteria = models.CharField(max_length=50, blank=True, help_text='Últimos 3 números ganadores')
    libreta_ganadora = models.ForeignKey(Libreta, null=True, blank=True, on_delete=models.SET_NULL, related_name='rifas_ganadas')
    monto_premio = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    socio_al_dia = models.BooleanField(default=True, help_text='El ganador estaba al día')
    observaciones = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        meses = ['','Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
        return f"Rifa {meses[self.mes]} {self.anio}"

    class Meta:
        ordering = ['-anio', '-mes']
        unique_together = ['mes', 'anio']
