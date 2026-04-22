from django.db import models
from django.utils import timezone


class Socio(models.Model):
    ESTADO_CHOICES = [('activo','Activo'),('inactivo','Inactivo'),('suspendido','Suspendido')]
    GENERO_CHOICES = [('M','Masculino'),('F','Femenino'),('O','Otro')]

    cedula = models.CharField(max_length=13, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=50, default='')
    telefono = models.CharField(max_length=15)
    whatsapp = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    nombre_preferido = models.CharField(max_length=80, blank=True)
    es_menor = models.BooleanField(default=False)
    representante_nombre = models.CharField(max_length=200, blank=True)
    representante_cedula = models.CharField(max_length=13, blank=True)
    banco_preferido = models.CharField(max_length=30, blank=True)
    cuenta_bancaria_preferida = models.CharField(max_length=50, blank=True)
    titular_cuenta_preferida = models.CharField(max_length=200, blank=True)
    cedula_titular_preferida = models.CharField(max_length=13, blank=True)
    recomendado_por = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='recomendados')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"{self.cedula} - {self.nombre_completo}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_portal(self):
        return self.nombre_preferido or self.nombres.split()[0]

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name_plural = 'Socios'


class Periodo(models.Model):
    anio = models.IntegerField(unique=True)
    fecha_inicio = models.DateField()
    fecha_cierre = models.DateField()
    activo = models.BooleanField(default=True)
    descripcion = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Periodo {self.anio}"

    class Meta:
        ordering = ['-anio']


class Libreta(models.Model):
    ESTADO_CHOICES = [('activa','Activa'),('cerrada','Cerrada'),('suspendida','Suspendida')]
    numero = models.IntegerField()  # Global continuo
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='libretas')
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='libretas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')
    fecha_inscripcion = models.DateField(auto_now_add=True)
    inscripcion_pagada = models.BooleanField(default=False)
    fecha_inscripcion_pago = models.DateField(null=True, blank=True)
    # Saldo acumulado de aportes (no sale salvo créditos)
    saldo_ahorro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Libreta #{self.numero} - {self.socio.nombre_completo} ({self.periodo.anio})"

    @property
    def codigo(self):
        return f"LIB-{self.numero:04d}-{self.periodo.anio}"

    @property
    def tiene_credito_activo(self):
        return self.creditos.filter(estado__in=['aprobado','desembolsado','mora']).exists()

    @property
    def aportes_al_dia(self):
        """Cuántos meses ha pagado en el periodo actual"""
        return self.aportes.filter(estado='verificado').count()

    class Meta:
        ordering = ['numero']
        unique_together = ['numero', 'periodo']
        verbose_name_plural = 'Libretas'


class AporteMensual(models.Model):
    ESTADO_CHOICES = [('pendiente','Pendiente'),('reportado','Reportado por socio'),('verificado','Verificado'),('atrasado','Atrasado')]
    MES_CHOICES = [(i, nombre) for i, nombre in enumerate(
        ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
         'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'], 1)]

    libreta = models.ForeignKey(Libreta, on_delete=models.CASCADE, related_name='aportes')
    mes = models.IntegerField(choices=MES_CHOICES)
    anio = models.IntegerField()
    # Cuotas
    monto_ahorro = models.DecimalField(max_digits=8, decimal_places=2, default=20)
    monto_loteria = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    monto_cumpleanos = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    monto_total = models.DecimalField(max_digits=8, decimal_places=2, default=22)
    # Pago
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_reporte = models.DateTimeField(null=True, blank=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    comprobante_referencia = models.CharField(max_length=200, blank=True)
    comprobante_archivo = models.FileField(upload_to='comprobantes/aportes/', null=True, blank=True)
    observacion = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"Aporte {self.get_mes_display()} {self.anio} - Libreta #{self.libreta.numero}"

    class Meta:
        ordering = ['anio', 'mes']
        unique_together = ['libreta', 'mes', 'anio']


class AccesoSocio(models.Model):
    socio = models.OneToOneField(Socio, on_delete=models.CASCADE, related_name='acceso')
    pin = models.CharField(max_length=128)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Acceso de {self.socio.nombre_completo}"
