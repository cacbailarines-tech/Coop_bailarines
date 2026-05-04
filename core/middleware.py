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
                logger.info('MANTENIMIENTO ACTIVO: retornando 503 para %s', request.path)
                mensaje = config.mensaje_mantenimiento or 'Estamos realizando mejoras. Volvemos pronto.'
                html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>En Mantenimiento</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#0B3D91,#1565C0);font-family:system-ui,sans-serif;color:#fff;text-align:center;padding:20px}}.logo{{width:100px;height:100px;margin:0 auto 24px;animation:pulse 2s infinite}}.logo img{{width:100%;height:100%;object-fit:contain}}h1{{font-size:22px;font-weight:800;margin-bottom:8px}}p{{font-size:14px;opacity:.85;max-width:320px;margin:0 auto 24px;line-height:1.5}}.bar{{width:120px;height:3px;background:rgba(255,255,255,.2);border-radius:2px;margin:0 auto;overflow:hidden}}.bar div{{width:30%;height:100%;background:#fff;border-radius:2px;animation:load 1.5s infinite}}@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.05)}}}}@keyframes load{{0%{{transform:translateX(-100%)}}100%{{transform:translateX(400%)}}}}</style>
</head><body><div><div class="logo"><img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Ccircle cx='50' cy='50' r='45' fill='none' stroke='white' stroke-width='3'/%3E%3Ctext x='50' y='60' text-anchor='middle' fill='white' font-size='30' font-weight='bold'%3EB%3C/text%3E%3C/svg%3E" alt="B"></div><h1>En Mantenimiento</h1><p>{mensaje}</p><div class="bar"><div></div></div></div></body></html>'''
                response = __import__('django.http').http.HttpResponse(html, content_type='text/html', status=503)
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                return response
            else:
                logger.debug('Mantenimiento NO activo')
        except Exception as e:
            logger.warning('Error middleware mantenimiento: %s', str(e))
        return self.get_response(request)
