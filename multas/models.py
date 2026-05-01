from django.db import models
from socios.models import Socio, Libreta, Periodo
from django.contrib.auth.models import User


class TipoMulta(models.Model):
    APLICA_CHOICES = [('socio','Por Socio'),('libreta','Por Libreta')]
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    aplica_a = models.CharField(max_length=10, choices=APLICA_CHOICES)
    activo = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.nombre} (${self.monto} por {self.get_aplica_a_display()})"
    class Meta:
        ordering = ['nombre']
        verbose_name = 'Tipo de Multa'
        verbose_name_plural = 'Tipos de Multa'


class Reunion(models.Model):
    ESTADO_CHOICES = [('programada','Programada'),('realizada','Realizada'),('cancelada','Cancelada')]
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='reuniones')
    fecha = models.DateField()
    mes = models.IntegerField()
    anio = models.IntegerField()
    descripcion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programada')
    notas = models.TextField(blank=True)
    registrada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"Reunión {self.fecha}"
    class Meta:
        ordering = ['-fecha']


class AsistenciaReunion(models.Model):
    ESTADO_CHOICES = [
        ('presente','Presente'),
        ('atrasado_11','Atrasado 11-20 min - $1'),
        ('atrasado_21','Atrasado 21+ min - $3'),
        ('falta_justificada','Falta Justificada - $1/libreta'),
        ('falta_injustificada','Falta Injustificada - $3/libreta'),
    ]
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE, related_name='asistencias')
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='asistencias')
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='presente')
    hora_llegada = models.TimeField(null=True, blank=True)
    justificacion = models.CharField(max_length=300, blank=True)
    multas_generadas = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.socio.nombre_completo} - {self.reunion.fecha} - {self.get_estado_display()}"
    class Meta:
        unique_together = ['reunion', 'socio']


class ComportamientoReunion(models.Model):
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE, related_name='comportamientos')
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='comportamientos')
    tipo_multa = models.ForeignKey(TipoMulta, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    multa_generada = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.socio.nombre_completo} - {self.tipo_multa.nombre}"


class Multa(models.Model):
    ESTADO_CHOICES = [('pendiente','Pendiente'),('pagada','Pagada'),('condonada','Condonada')]
    ORIGEN_CHOICES = [
        ('reunion_asistencia','Reunión - Asistencia'),
        ('reunion_comportamiento','Reunión - Comportamiento'),
        ('mensualidad_atraso','Mensualidad Atrasada ($5/libreta)'),
        ('mensualidad_incumplimiento','Incumplimiento Total ($20)'),
        ('credito_atraso_primera','Crédito Atrasado 1ra vez ($10)'),
        ('credito_atraso_reincidente','Crédito Atrasado Reincidente ($30)'),
        ('manual','Aplicada Manualmente'),
    ]
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='multas')
    libreta = models.ForeignKey(Libreta, null=True, blank=True, on_delete=models.SET_NULL, related_name='multas')
    origen = models.CharField(max_length=40, choices=ORIGEN_CHOICES)
    descripcion = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    reunion = models.ForeignKey(Reunion, null=True, blank=True, on_delete=models.SET_NULL)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='multas')
    mes_origen = models.IntegerField(null=True, blank=True, help_text='Mes que originó la multa')
    anio_origen = models.IntegerField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_generacion = models.DateField(auto_now_add=True)
    fecha_pago = models.DateField(null=True, blank=True)
    comprobante_pago = models.CharField(max_length=200, blank=True)
    comprobante_archivo = models.FileField(upload_to='comprobantes/multas/', null=True, blank=True)
    aplicada_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='multas_aplicadas')
    observaciones = models.CharField(max_length=300, blank=True)
    def __str__(self):
        return f"Multa ${self.monto} - {self.socio.nombre_completo}"
    class Meta:
        ordering = ['-fecha_generacion']

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
import threading

@receiver(post_save, sender=Reunion)
def notificar_reunion_programada(sender, instance, created, **kwargs):
    if instance.estado == 'programada':
        # Si no hay destinatarios, al menos enviamos al admin como prueba
        socios_activos = Socio.objects.filter(estado='activo').exclude(email='')
        destinatarios = [s.email for s in socios_activos]
        if not destinatarios:
            destinatarios = [settings.DEFAULT_FROM_EMAIL]
            
        asunto = f"Cooperativa Bailarines: Reunión Programada - {instance.fecha.strftime('%d/%m/%Y')}"
        mensaje = f"""Estimado(a) socio(a),

Le informamos que la administración ha programado una nueva reunión obligatoria.

Fecha: {instance.fecha.strftime('%d/%m/%Y')}
Detalles: {instance.descripcion if instance.descripcion else 'Asistencia obligatoria según reglamento.'}

Recuerde que el atraso o falta injustificada genera multas automáticas según el reglamento vigente ($1 - $3).
Si tiene algún inconveniente, recuerde justificar su inasistencia con al menos 24 horas de anticipación.

Atentamente,
La Directiva
Cooperativa Bailarines
(Este es un mensaje automático, por favor no responda a este correo)"""
        try:
            from django.core.mail import EmailMessage
            email = EmailMessage(
                subject=asunto,
                body=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
                bcc=destinatarios,
            )
            email.send(fail_silently=False)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error fatal enviando correos de reunión: {e}")
