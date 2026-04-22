from django.contrib import admin
from .models import Socio, Periodo, Libreta, AporteMensual, AccesoSocio

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ['cedula','nombre_completo','telefono','estado','fecha_registro']
    list_filter = ['estado','es_menor']
    search_fields = ['nombres','apellidos','cedula']

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ['anio','fecha_inicio','fecha_cierre','activo']

@admin.register(Libreta)
class LibretaAdmin(admin.ModelAdmin):
    list_display = ['numero','socio','periodo','estado','saldo_ahorro','inscripcion_pagada']
    list_filter = ['periodo','estado']
    search_fields = ['numero','socio__nombres','socio__apellidos']

@admin.register(AporteMensual)
class AporteMensualAdmin(admin.ModelAdmin):
    list_display = ['libreta','mes','anio','monto_total','estado']
    list_filter = ['estado','mes','anio']

@admin.register(AccesoSocio)
class AccesoSocioAdmin(admin.ModelAdmin):
    list_display = ['socio','activo','ultimo_acceso']
