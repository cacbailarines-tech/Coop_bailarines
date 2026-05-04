from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse


class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        if request.path.startswith('/static/'):
            return self.get_response(request)
        if request.path.startswith('/media/'):
            return self.get_response(request)
        try:
            from core.models import ConfiguracionSistema
            config = ConfiguracionSistema.objects.first()
            if config and config.modo_mantenimiento:
                if request.user.is_authenticated and request.user.is_staff:
                    return self.get_response(request)
                template = loader.get_template('core/maintenance.html')
                mensaje = config.mensaje_mantenimiento or 'Estamos realizando mejoras. Volvemos pronto.'
                return HttpResponse(template.render({'mensaje': mensaje}), status=503)
        except Exception:
            pass
        return self.get_response(request)
