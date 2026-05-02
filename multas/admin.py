from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import TipoMulta, Reunion, AsistenciaReunion, Multa, ComportamientoReunion

@admin.register(TipoMulta)
class TipoMultaAdmin(ImportExportModelAdmin):
    list_display = ['nombre','monto','aplica_a','activo']

@admin.register(Reunion)
class ReunionAdmin(ImportExportModelAdmin):
    list_display = ['fecha','periodo','estado']

@admin.register(AsistenciaReunion)
class AsistenciaAdmin(ImportExportModelAdmin):
    list_display = ['socio','reunion','estado']

@admin.register(Multa)
class MultaAdmin(ImportExportModelAdmin):
    list_display = ['socio','monto','origen','estado','fecha_generacion']
    list_filter = ['estado','origen']
    search_fields = ['socio__nombres','socio__apellidos']
