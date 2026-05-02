from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Socio, Periodo, Libreta, AporteMensual, AccesoSocio

@admin.register(Socio)
class SocioAdmin(ImportExportModelAdmin):
    list_display = ['cedula','nombre_completo','telefono','estado','fecha_registro']
    list_filter = ['estado','es_menor']
    search_fields = ['nombres','apellidos','cedula']

@admin.register(Periodo)
class PeriodoAdmin(ImportExportModelAdmin):
    list_display = ['anio','fecha_inicio','fecha_cierre','activo']

@admin.register(Libreta)
class LibretaAdmin(ImportExportModelAdmin):
    list_display = ['numero','socio','periodo','estado','saldo_ahorro','inscripcion_pagada']
    list_filter = ['periodo','estado']
    search_fields = ['numero','socio__nombres','socio__apellidos']

@admin.register(AporteMensual)
class AporteMensualAdmin(ImportExportModelAdmin):
    list_display = ['libreta','mes','anio','monto_total','estado']
    list_filter = ['estado','mes','anio']

@admin.register(AccesoSocio)
class AccesoSocioAdmin(ImportExportModelAdmin):
    list_display = ['socio','activo','ultimo_acceso']
