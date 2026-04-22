from django.db import models
from socios.models import Socio, Libreta, Periodo
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_UP
import math


TASA_MENSUAL = Decimal('0.05')  # 5% fijo

BANCO_CHOICES = [
    ('pichincha', 'Banco Pichincha'),
    ('guayaquil', 'Banco Guayaquil'),
    ('pacifico', 'Banco del Pacífico'),
    ('bolivariano', 'Banco Bolivariano'),
    ('produbanco', 'Produbanco'),
    ('internacional', 'Banco Internacional'),
    ('otro', 'Otro Banco'),
]

COMISION_BANCO = {
    'pichincha': Decimal('0.50'),
    'guayaquil': Decimal('1.00'),
    'pacifico': Decimal('1.00'),
    'bolivariano': Decimal('1.00'),
    'produbanco': Decimal('1.00'),
    'internacional': Decimal('1.00'),
    'otro': Decimal('1.00'),
}

COMISION_INTERNA = {
    'pichincha': Decimal('0.50'),   # beneficio total para cooperativa (no hay cobro externo)
    'guayaquil': Decimal('0.59'),   # 1.00 - 0.41 cobro externo
    'pacifico': Decimal('0.59'),
    'bolivariano': Decimal('0.59'),
    'produbanco': Decimal('0.59'),
    'internacional': Decimal('0.59'),
    'otro': Decimal('0.59'),
}


class Credito(models.Model):
    TIPO_CHOICES = [('mensualizado','Mensualizado'),('no_mensualizado','No Mensualizado')]
    ESTADO_CHOICES = [
        ('pendiente','Pendiente'),
        ('aprobado','Aprobado'),
        ('desembolsado','Desembolsado'),
        ('pagado','Pagado'),
        ('mora_leve','Mora Leve (≤30d)'),
        ('mora_media','Mora Media (31-60d)'),
        ('mora_grave','Mora Grave (>60d)'),
        ('cancelado','Cancelado'),
    ]

    # Identificación
    numero = models.CharField(max_length=20, unique=True)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='creditos')
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='creditos')
    libreta = models.ForeignKey(Libreta, on_delete=models.CASCADE, related_name='creditos')

    # Solicitud
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto_solicitado = models.DecimalField(max_digits=10, decimal_places=2)
    plazo_meses = models.IntegerField()
    banco = models.CharField(max_length=30, choices=BANCO_CHOICES)
    numero_cuenta_bancaria = models.CharField(max_length=50)
    titular_cuenta = models.CharField(max_length=200)
    cedula_titular = models.CharField(max_length=13)

    # Cálculos (se llenan al aprobar)
    tasa_mensual = models.DecimalField(max_digits=5, decimal_places=4, default=TASA_MENSUAL)
    interes_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comision_bancaria = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    beneficio_transferencia = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    monto_transferir = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # lo que recibe el socio
    # Mensualizado
    cuota_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # No mensualizado
    monto_pago_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Saldo
    saldo_pendiente = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_aprobacion = models.DateField(null=True, blank=True)
    fecha_desembolso = models.DateField(null=True, blank=True)
    comprobante_desembolso = models.FileField(upload_to='comprobantes/desembolsos_credito/', null=True, blank=True)
    fecha_pago_limite = models.DateField(null=True, blank=True)
    aprobado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='creditos_aprobados')
    observaciones = models.TextField(blank=True)
    motivo_rechazo = models.CharField(max_length=300, blank=True)

    @staticmethod
    def _ceil_money(valor):
        return Decimal(valor).quantize(Decimal('0.01'), rounding=ROUND_UP)

    def calcular_montos(self):
        """Calcula todos los montos según el tipo de crédito"""
        monto = self.monto_solicitado
        plazo = self.plazo_meses
        tasa = self.tasa_mensual
        comision = COMISION_BANCO.get(self.banco, Decimal('1.00'))
        beneficio = COMISION_INTERNA.get(self.banco, Decimal('0.59'))

        self.comision_bancaria = comision
        self.beneficio_transferencia = beneficio
        self.interes_total = (monto * tasa * plazo).quantize(Decimal('0.01'))

        if self.tipo == 'mensualizado':
            # Recibe el monto completo menos comisión
            # Paga (capital + interés_total) / plazo pero redondeado hacia arriba
            self.monto_transferir = monto - comision
            capital_por_cuota = self._ceil_money(monto / plazo)
            interes_por_cuota = self._ceil_money(self.interes_total / plazo)
            self.cuota_mensual = capital_por_cuota + interes_por_cuota
            self.monto_pago_final = Decimal('0')
        else:
            # No mensualizado: descuenta interés por adelantado
            self.monto_transferir = monto - self.interes_total - comision
            self.cuota_mensual = Decimal('0')
            self.monto_pago_final = monto  # devuelve el capital completo

        self.saldo_pendiente = monto

    def obtener_resumen_cuota_plana(self):
        if self.tipo != 'mensualizado' or not self.plazo_meses:
            return None
        capital_por_cuota = self._ceil_money(self.monto_solicitado / self.plazo_meses)
        interes_por_cuota = self._ceil_money(self.interes_total / self.plazo_meses)
        cuota = capital_por_cuota + interes_por_cuota
        return {
            'capital_por_cuota': capital_por_cuota,
            'interes_por_cuota': interes_por_cuota,
            'cuota': cuota,
            'capital_total': capital_por_cuota * self.plazo_meses,
            'interes_total_cobrado': interes_por_cuota * self.plazo_meses,
        }

    def generar_tabla_amortizacion_plana(self):
        if self.tipo != 'mensualizado' or not self.fecha_desembolso:
            return []

        from datetime import date
        import calendar

        resumen = self.obtener_resumen_cuota_plana()
        if not resumen:
            return []

        saldo = self.monto_solicitado
        tabla = []
        for i in range(1, self.plazo_meses + 1):
            mes = self.fecha_desembolso.month + i
            anio = self.fecha_desembolso.year + (mes - 1) // 12
            mes = ((mes - 1) % 12) + 1
            last_day = calendar.monthrange(anio, mes)[1]
            fecha_cuota = date(anio, mes, min(self.fecha_desembolso.day, last_day))
            saldo_inicial = saldo
            capital = resumen['capital_por_cuota']
            interes = resumen['interes_por_cuota']
            cuota = resumen['cuota']
            saldo = (saldo_inicial - capital).quantize(Decimal('0.01'))
            tabla.append({
                'numero': i,
                'fecha': fecha_cuota,
                'saldo_inicial': saldo_inicial,
                'capital': capital,
                'interes': interes,
                'cuota': cuota,
                'saldo_final': saldo,
            })
        return tabla

    def __str__(self):
        return f"{self.numero} - {self.socio.nombre_completo} ${self.monto_solicitado}"

    class Meta:
        ordering = ['-fecha_solicitud']


class PagoCredito(models.Model):
    ESTADO_CHOICES = [('reportado','Reportado'),('verificado','Verificado'),('rechazado','Rechazado')]

    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name='pagos')
    numero_pago = models.IntegerField()
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    saldo_posterior = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    comprobante_referencia = models.CharField(max_length=200, blank=True)
    comprobante_archivo = models.FileField(upload_to='comprobantes/pagos_credito/', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reportado')
    es_abono = models.BooleanField(default=False, help_text='Para no mensualizado')
    verificado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    observaciones = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"Pago #{self.numero_pago} - {self.credito.numero}"

    class Meta:
        ordering = ['numero_pago']


class MultaCredito(models.Model):
    """Multas por cuotas atrasadas de crédito"""
    TIPO_CHOICES = [('primera','Primera vez $10'),('reincidente','Reincidente $30')]
    credito = models.ForeignKey(Credito, on_delete=models.CASCADE, related_name='multas')
    numero_cuota = models.IntegerField(help_text='Número de cuota atrasada')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    pagada = models.BooleanField(default=False)
    fecha_generacion = models.DateField(auto_now_add=True)
    fecha_pago = models.DateField(null=True, blank=True)
    observaciones = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Multa crédito {self.credito.numero} cuota #{self.numero_cuota}"
