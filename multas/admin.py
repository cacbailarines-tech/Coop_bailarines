from django.contrib import admin
from .models import TipoMulta, Reunion, AsistenciaReunion, Multa, ComportamientoReunion

@admin.register(TipoMulta)
class TipoMultaAdmin(admin.ModelAdmin):
    list_display = ['nombre','monto','aplica_a','activo']

@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ['fecha','periodo','estado']

@admin.register(AsistenciaReunion)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['socio','reunion','estado']

@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ['socio','monto','origen','estado','fecha_generacion']
    list_filter = ['estado','origen']
    search_fields = ['socio__nombres','socio__apellidos']
