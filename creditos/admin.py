from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Credito, PagoCredito, MultaCredito

@admin.register(Credito)
class CreditoAdmin(ImportExportModelAdmin):
    list_display = ['numero','socio','libreta','tipo','monto_solicitado','estado','fecha_solicitud']
    list_filter = ['estado','tipo','banco']
    search_fields = ['numero','socio__nombres','socio__apellidos']

@admin.register(PagoCredito)
class PagoCreditoAdmin(ImportExportModelAdmin):
    list_display = ['credito','numero_pago','monto_pagado','estado','fecha_reporte']
    list_filter = ['estado']

@admin.register(MultaCredito)
class MultaCreditoAdmin(ImportExportModelAdmin):
    list_display = ['credito','numero_cuota','tipo','monto','pagada']
