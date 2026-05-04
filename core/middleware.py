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
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{min-height:100vh;display:flex;align-items:center;justify-content:center;background:#1a1a2e;font-family:system-ui,-apple-system,sans-serif;color:#fff;text-align:center;padding:20px;overflow:hidden}}
.container{{position:relative;z-index:1}}
.logo-wrap{{width:140px;height:140px;margin:0 auto 28px;position:relative;display:flex;align-items:center;justify-content:center}}
.logo-wrap img{{width:100%;height:100%;object-fit:contain;filter:brightness(0) invert(1);animation:logoPulse 3s ease-in-out infinite;filter:brightness(0) invert(1) drop-shadow(0 0 25px rgba(255,255,255,.25))}}
.logo-ring{{position:absolute;top:-15px;left:-15px;right:-15px;bottom:-15px;border:2px solid rgba(255,255,255,.12);border-radius:50%;animation:ringSpin 8s linear infinite}}
.logo-ring::before{{content:'';position:absolute;top:0;left:50%;width:8px;height:8px;background:#fff;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 15px #fff,0 0 30px rgba(255,255,255,.3)}}
.logo-ring::after{{content:'';position:absolute;bottom:10%;left:10%;right:10%;top:10%;border:1px dashed rgba(255,255,255,.08);border-radius:50%;animation:ringSpin 12s linear infinite reverse}}
h1{{font-size:24px;font-weight:800;margin-bottom:8px;letter-spacing:.5px;animation:fadeUp .8s ease-out}}
p{{font-size:14px;opacity:.65;max-width:300px;margin:0 auto 28px;line-height:1.6;animation:fadeUp 1s ease-out}}
.progress{{width:160px;height:3px;background:rgba(255,255,255,.1);border-radius:2px;margin:0 auto;overflow:hidden;animation:fadeUp 1.2s ease-out}}
.progress div{{width:40%;height:100%;background:linear-gradient(90deg,transparent,#fff,transparent);border-radius:2px;animation:progressMove 2s ease-in-out infinite}}
.dots{{display:flex;justify-content:center;gap:8px;margin-top:20px;animation:fadeUp 1.4s ease-out}}
.dot{{width:6px;height:6px;background:rgba(255,255,255,.3);border-radius:50%;animation:dotPulse 1.5s ease-in-out infinite}}
.dot:nth-child(2){{animation-delay:.2s}}.dot:nth-child(3){{animation-delay:.4s}}
@keyframes logoPulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.06)}}}}
@keyframes ringSpin{{0%{{transform:rotate(0)}}100%{{transform:rotate(360deg)}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes progressMove{{0%{{transform:translateX(-100%)}}100%{{transform:translateX(350%)}}}}
@keyframes dotPulse{{0%,100%{{opacity:.3;transform:scale(1)}}50%{{opacity:1;transform:scale(1.8)}}}}
</style>
</head><body>
<div class="container">
<div class="logo-wrap"><div class="logo-ring"></div>
<img src="/static/img/logo.png" alt="Cooperativa Bailarines">
</div>
<h1>En Mantenimiento</h1>
<p>{mensaje}</p>
<div class="progress"><div></div></div>
<div class="dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
</div>
</body></html>'''
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
