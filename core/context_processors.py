from base64 import b64encode
from pathlib import Path

from django.conf import settings
from socios.models import AporteMensual
from creditos.models import PagoCredito, Credito
from multas.models import Multa


def _logo_data_uri():
    logo_path = Path(settings.BASE_DIR) / 'static' / 'img' / 'logo.png'
    if not logo_path.exists():
        return ''
    return f"data:image/png;base64,{b64encode(logo_path.read_bytes()).decode('ascii')}"


def nav_counts(request):
    base_context = {
        'push_enabled': bool(settings.WEBPUSH_ENABLED and settings.WEBPUSH_VAPID_PUBLIC_KEY),
        'push_vapid_public_key': settings.WEBPUSH_VAPID_PUBLIC_KEY,
        'web_logo_src': _logo_data_uri(),
    }
    if not request.user.is_authenticated:
        return base_context
    try:
        aportes_reportados = AporteMensual.objects.filter(estado='reportado').count()
        pagos_reportados = PagoCredito.objects.filter(estado='reportado').count()
        multas_reportadas = Multa.objects.filter(
            estado='pendiente',
            observaciones__startswith='Pago reportado'
        ).count()
        return {
            'pendientes_count': aportes_reportados,
            'pagos_count': pagos_reportados,
            'multas_count': Multa.objects.filter(estado='pendiente').count(),
            'solicitudes_count': Credito.objects.filter(estado='pendiente').count(),
            'verificaciones_count': aportes_reportados + pagos_reportados + multas_reportadas,
            **base_context,
        }
    except:
        return base_context
