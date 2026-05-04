import logging

logger = logging.getLogger(__name__)


class MaintenanceModeMiddleware:
    ALWAYS_ALLOW_PATHS = ('/admin/', '/static/', '/media/', '/favicon.ico')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for prefix in self.ALWAYS_ALLOW_PATHS:
            if request.path.startswith(prefix):
                return self.get_response(request)
        try:
            from core.models import ConfiguracionSistema
            config = ConfiguracionSistema.objects.first()
            if config and config.modo_mantenimiento:
                logger.info('Mantenimiento activo: mostrando pagina 503 para %s', request.path)
                template = loader.get_template('core/maintenance.html')
                mensaje = config.mensaje_mantenimiento or 'Estamos realizando mejoras. Volvemos pronto.'
                return HttpResponse(template.render({'mensaje': mensaje}), status=503)
            else:
                logger.debug('Mantenimiento NO activo (config=%s)', config)
        except Exception as e:
            logger.debug('Middleware mantenimiento: %s', str(e))
        return self.get_response(request)
