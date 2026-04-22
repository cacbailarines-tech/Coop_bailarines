from django.conf import settings
from socios.models import AporteMensual
from creditos.models import PagoCredito, Credito
from multas.models import Multa

def nav_counts(request):
    if not request.user.is_authenticated:
        return {
            'push_enabled': bool(settings.WEBPUSH_ENABLED and settings.WEBPUSH_VAPID_PUBLIC_KEY),
            'push_vapid_public_key': settings.WEBPUSH_VAPID_PUBLIC_KEY,
        }
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
            'push_enabled': bool(settings.WEBPUSH_ENABLED and settings.WEBPUSH_VAPID_PUBLIC_KEY),
            'push_vapid_public_key': settings.WEBPUSH_VAPID_PUBLIC_KEY,
        }
    except:
        return {
            'push_enabled': bool(settings.WEBPUSH_ENABLED and settings.WEBPUSH_VAPID_PUBLIC_KEY),
            'push_vapid_public_key': settings.WEBPUSH_VAPID_PUBLIC_KEY,
        }
