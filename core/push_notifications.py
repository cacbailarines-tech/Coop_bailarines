import json

from django.conf import settings
from django.utils import timezone
from pywebpush import WebPushException, webpush

from .models import PushSubscription


def push_configured():
    return bool(
        settings.WEBPUSH_ENABLED
        and settings.WEBPUSH_VAPID_PUBLIC_KEY
        and settings.WEBPUSH_VAPID_PRIVATE_KEY
        and settings.WEBPUSH_VAPID_ADMIN_EMAIL
    )


def _send_to_subscription(subscription, payload):
    if not push_configured() or not subscription.activa:
        return False
    try:
        webpush(
            subscription_info=subscription.subscription_data,
            data=json.dumps(payload),
            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
            vapid_claims={"sub": f"mailto:{settings.WEBPUSH_VAPID_ADMIN_EMAIL}"},
        )
        subscription.ultima_notificacion = timezone.now()
        subscription.activa = True
        subscription.save(update_fields=['ultima_notificacion', 'activa', 'updated_at'])
        return True
    except WebPushException as exc:
        status_code = getattr(getattr(exc, 'response', None), 'status_code', None)
        if status_code in {404, 410}:
            subscription.activa = False
            subscription.save(update_fields=['activa', 'updated_at'])
        return False
    except Exception:
        return False


def notify_socio_push(socio, title, body, url='/portal/inicio/', tag='portal-alerta'):
    if not socio or not push_configured():
        return 0
    payload = {
        'title': title,
        'body': body,
        'url': url,
        'tag': tag,
        'icon': '/static/img/logo.png',
        'badge': '/static/img/logo.png',
    }
    sent = 0
    for subscription in socio.push_subscriptions.filter(activa=True):
        if _send_to_subscription(subscription, payload):
            sent += 1
    return sent
