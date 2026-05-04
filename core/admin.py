from django.contrib import admin
from .models import ConfiguracionSistema, PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'telefono']
    list_filter = ['rol']


@admin.register(ConfiguracionSistema)
class ConfiguracionSistemaAdmin(admin.ModelAdmin):
    list_display = ['id', 'modo_mantenimiento', 'mensaje_mantenimiento']
    list_editable = ['modo_mantenimiento', 'mensaje_mantenimiento']
    list_display_links = ['id']

    def has_add_permission(self, request):
        return ConfiguracionSistema.objects.count() == 0

    def changelist_view(self, request, extra_context=None):
        if not ConfiguracionSistema.objects.exists():
            ConfiguracionSistema.objects.create()
        return super().changelist_view(request, extra_context)
