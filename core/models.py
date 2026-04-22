from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PerfilUsuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('cajero', 'Cajero'),
        ('gerente', 'Gerente'),
        ('tesorero', 'Tesorero'),
    ]

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cajero')
    telefono = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_rol_display()}"


class Movimiento(models.Model):
    TIPO_CHOICES = [('ingreso', 'Ingreso'), ('egreso', 'Egreso')]
    CATEGORIA_CHOICES = [
        ('aporte_mensual', 'Aporte Mensual Socio'),
        ('inscripcion', 'Inscripción de Libreta'),
        ('interes_credito', 'Interés de Crédito'),
        ('comision_banco', 'Beneficio Comisión Bancaria'),
        ('multa', 'Multa'),
        ('rifa', 'Rifa / Lotería'),
        ('otro_ingreso', 'Otro Ingreso'),
        ('desembolso_credito', 'Desembolso de Crédito'),
        ('devolucion_ahorro', 'Devolución de Ahorro'),
        ('premio_rifa', 'Premio Rifa'),
        ('cumpleanos', 'Regalo Cumpleaños'),
        ('gasto_operativo', 'Gasto Operativo'),
        ('otro_egreso', 'Otro Egreso'),
    ]
    ORIGEN_CHOICES = [
        ('automatico', 'Automático (sistema)'),
        ('manual', 'Registro Manual'),
    ]

    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES)
    descripcion = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    origen = models.CharField(max_length=15, choices=ORIGEN_CHOICES, default='manual')
    comprobante = models.CharField(max_length=200, blank=True)
    comprobante_archivo = models.FileField(upload_to='comprobantes/movimientos/', null=True, blank=True)
    socio_ref = models.CharField(max_length=200, blank=True, help_text='Nombre del socio relacionado')
    libreta_ref = models.CharField(max_length=50, blank=True)
    credito_ref = models.CharField(max_length=50, blank=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='movimientos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_display()} ${self.monto} - {self.descripcion[:40]}"

    class Meta:
        ordering = ['-fecha', '-fecha_registro']
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos (Ingresos/Egresos)'


class CajaDiaria(models.Model):
    fecha = models.DateField(unique=True)
    saldo_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    abierta_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='cajas_abiertas'
    )
    cerrada_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cajas_cerradas'
    )
    fecha_apertura = models.DateTimeField(default=timezone.now)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    observaciones_apertura = models.TextField(blank=True)
    observaciones_cierre = models.TextField(blank=True)

    def __str__(self):
        return f"Caja {self.fecha}"

    @property
    def esta_abierta(self):
        return self.fecha_cierre is None

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Caja Diaria'
        verbose_name_plural = 'Cajas Diarias'


class AuditoriaSistema(models.Model):
    AREA_CHOICES = [
        ('tesoreria', 'Tesorería'),
        ('verificaciones', 'Verificaciones'),
        ('caja', 'Caja Diaria'),
        ('socios', 'Socios'),
        ('creditos', 'Créditos'),
        ('multas', 'Multas'),
        ('seguridad', 'Seguridad'),
        ('reportes', 'Reportes'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.CharField(max_length=20, choices=AREA_CHOICES)
    accion = models.CharField(max_length=80)
    entidad = models.CharField(max_length=80, blank=True)
    objeto_id = models.CharField(max_length=50, blank=True)
    descripcion = models.CharField(max_length=300)
    datos = models.JSONField(default=dict, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_area_display()} - {self.accion}"

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Auditoría del Sistema'
        verbose_name_plural = 'Auditoría del Sistema'


class PushSubscription(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='push_subscriptions'
    )
    socio = models.ForeignKey(
        'socios.Socio', on_delete=models.CASCADE, null=True, blank=True, related_name='push_subscriptions'
    )
    endpoint = models.URLField(unique=True)
    subscription_data = models.JSONField(default=dict)
    user_agent = models.CharField(max_length=300, blank=True)
    activa = models.BooleanField(default=True)
    ultima_notificacion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.socio_id:
            return f"Push socio #{self.socio_id}"
        if self.usuario_id:
            return f"Push usuario #{self.usuario_id}"
        return self.endpoint

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Suscripción Push'
        verbose_name_plural = 'Suscripciones Push'
