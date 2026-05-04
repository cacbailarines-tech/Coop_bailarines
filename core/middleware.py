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
.logo-wrap{{width:120px;height:120px;margin:0 auto 28px;position:relative}}
.logo-wrap svg{{width:100%;height:100%;animation:logoPulse 3s ease-in-out infinite;filter:drop-shadow(0 0 30px rgba(255,255,255,.3))}}
.logo-ring{{position:absolute;top:-15px;left:-15px;right:-15px;bottom:-15px;border:2px solid rgba(255,255,255,.15);border-radius:50%;animation:ringSpin 8s linear infinite}}
.logo-ring::before{{content:'';position:absolute;top:0;left:50%;width:8px;height:8px;background:#fff;border-radius:50%;transform:translate(-50%,-50%);box-shadow:0 0 15px #fff}}
h1{{font-size:24px;font-weight:800;margin-bottom:8px;letter-spacing:.5px;animation:fadeUp .8s ease-out}}
p{{font-size:14px;opacity:.65;max-width:300px;margin:0 auto 28px;line-height:1.6;animation:fadeUp 1s ease-out}}
.progress{{width:160px;height:3px;background:rgba(255,255,255,.1);border-radius:2px;margin:0 auto;overflow:hidden;animation:fadeUp 1.2s ease-out}}
.progress div{{width:40%;height:100%;background:linear-gradient(90deg,transparent,#fff,transparent);border-radius:2px;animation:progressMove 2s ease-in-out infinite}}
.dots{{display:flex;justify-content:center;gap:8px;margin-top:20px;animation:fadeUp 1.4s ease-out}}
.dot{{width:6px;height:6px;background:rgba(255,255,255,.3);border-radius:50%;animation:dotPulse 1.5s ease-in-out infinite}}
.dot:nth-child(2){{animation-delay:.2s}}.dot:nth-child(3){{animation-delay:.4s}}
@keyframes logoPulse{{0%,100%{{transform:scale(1) rotate(0)}}50%{{transform:scale(1.08) rotate(2deg)}}}}
@keyframes ringSpin{{0%{{transform:rotate(0)}}100%{{transform:rotate(360deg)}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes progressMove{{0%{{transform:translateX(-100%)}}100%{{transform:translateX(350%)}}}}
@keyframes dotPulse{{0%,100%{{opacity:.3;transform:scale(1)}}50%{{opacity:1;transform:scale(1.5)}}}}
</style>
</head><body>
<div class="container">
<div class="logo-wrap"><div class="logo-ring"></div>
<svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="100" cy="100" r="90" stroke="white" stroke-width="3" opacity=".8"/>
<path d="M65 70 L80 65 L95 62 L100 55 L105 62 L120 65 L135 70 L130 85 L125 100 L110 105 L100 115 L90 105 L75 100 L70 85 Z" fill="white" opacity=".9"/>
<circle cx="100" cy="100" r="20" fill="white" opacity=".6"/>
<text x="100" y="106" text-anchor="middle" fill="#1a1a2e" font-size="16" font-weight="bold" font-family="system-ui">B</text>
<path d="M85 135 Q100 125 115 135" stroke="white" stroke-width="2" fill="none" opacity=".6"/>
<text x="100" y="150" text-anchor="middle" fill="white" font-size="8" opacity=".5" font-family="system-ui" letter-spacing="2">BAILARINES</text>
</svg>
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
