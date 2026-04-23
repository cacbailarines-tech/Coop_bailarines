import json
import logging
import threading
from base64 import urlsafe_b64encode
from datetime import date, timedelta
from email.mime.image import MIMEImage
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _portal_url(path='/portal/'):
    base_url = getattr(settings, 'APP_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
    return f'{base_url}{path}'


def _email_configured():
    if _using_gmail_api():
        return True
    return bool(
        getattr(settings, 'EMAIL_HOST_USER', '').strip()
        and getattr(settings, 'EMAIL_HOST_PASSWORD', '').strip()
    )


def _using_gmail_api():
    return bool(
        getattr(settings, 'GMAIL_CLIENT_ID', '').strip()
        and getattr(settings, 'GMAIL_CLIENT_SECRET', '').strip()
        and getattr(settings, 'GMAIL_REFRESH_TOKEN', '').strip()
        and getattr(settings, 'GMAIL_SENDER_EMAIL', '').strip()
    )


def _logo_path():
    for file_name in ('logo-app-full-192.png', 'logo.png'):
        logo_path = Path(settings.BASE_DIR) / 'static' / 'img' / file_name
        if logo_path.exists():
            return logo_path
    return None


def _logo_cid():
    return 'logo-bailarines'


def _logo_attachment():
    logo_path = _logo_path()
    if not logo_path:
        return None
    image = MIMEImage(logo_path.read_bytes(), _subtype='png')
    image.add_header('Content-ID', f'<{_logo_cid()}>')
    image.add_header('Content-Disposition', 'inline', filename=logo_path.name)
    return image


def _saludo_socio(socio):
    return socio.nombre_preferido or socio.nombres.split()[0]


def _email_shell(title, intro, sections=None, cta_label='Ir al portal', cta_url=None, note=None):
    sections = sections or []
    cta_url = cta_url or _portal_url()
    logo_html = ''
    if _logo_path():
        logo_html = (
            f'<img src="cid:{_logo_cid()}" alt="Cooperativa Bailarines" '
            'style="display:block;height:38px;width:auto;object-fit:contain;">'
        )
    section_html = ''.join(
        (
            '<tr><td style="padding:0 18px 12px 18px;">'
            '<div style="background:#ffffff;border:1px solid #DDE3EF;border-radius:12px;'
            'padding:14px 16px;box-shadow:0 2px 6px rgba(11,61,145,0.05);">'
            f'<div style="font-size:11px;font-weight:700;letter-spacing:.08em;'
            f'text-transform:uppercase;color:#6B7A99;margin-bottom:6px;">{escape(section["label"])}</div>'
            f'<div style="font-size:18px;font-weight:800;color:{section.get("color", "#0B3D91")};">'
            f'{escape(section["value"])}</div>'
            '</div></td></tr>'
        )
        for section in sections
    )
    note_html = (
        f'<tr><td style="padding:0 18px 18px 18px;font-size:13px;line-height:1.6;color:#6B7A99;">'
        f'{escape(note)}</td></tr>'
        if note else ''
    )
    return f"""
<!DOCTYPE html>
<html lang="es">
<body style="margin:0;padding:24px;background:#F0F4FA;font-family:'Plus Jakarta Sans',Arial,Helvetica,sans-serif;color:#1A2332;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:760px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #DDE3EF;box-shadow:0 2px 8px rgba(11,61,145,0.06);">
    <tr>
      <td style="background:#0B3D91;padding:0 20px;height:58px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td style="vertical-align:middle;padding:10px 0;">
              <table role="presentation" cellspacing="0" cellpadding="0">
                <tr>
                  <td style="vertical-align:middle;">{logo_html}</td>
                  <td style="vertical-align:middle;padding-left:10px;">
                    <div style="font-size:10px;color:rgba(255,255,255,0.6);font-weight:600;">Portal del Socio</div>
                  </td>
                </tr>
              </table>
            </td>
            <td style="text-align:right;vertical-align:middle;">
              <span style="display:inline-block;color:rgba(255,255,255,0.78);font-size:12px;font-weight:600;padding:6px 12px;border-radius:7px;background:rgba(255,255,255,0.12);">Notificación automática</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr><td style="height:4px;background:#F2A900;"></td></tr>
    <tr>
      <td style="padding:18px;border-bottom:1px solid #DDE3EF;background:linear-gradient(to right,rgba(11,61,145,0.03),transparent);">
        <div style="font-size:13px;font-weight:700;color:#6B7A99;letter-spacing:.04em;text-transform:uppercase;margin-bottom:6px;">Cooperativa Bailarines</div>
        <div style="font-size:24px;line-height:1.2;font-weight:800;color:#1A2332;">{escape(title)}</div>
      </td>
    </tr>
    <tr>
      <td style="padding:18px 18px 16px 18px;font-size:14px;line-height:1.7;color:#1A2332;">
        {escape(intro).replace(chr(10), '<br>')}
      </td>
    </tr>
    <tr>
      <td style="padding:0 18px 12px 18px;">
        <table role="presentation" cellspacing="0" cellpadding="0">
          <tr>
            <td><span style="display:inline-block;background:rgba(11,61,145,0.1);color:#0B3D91;font-size:11px;font-weight:700;padding:5px 10px;border-radius:20px;">Portal del Socio</span></td>
            <td style="width:8px;"></td>
            <td><span style="display:inline-block;background:rgba(0,137,123,0.1);color:#00897B;font-size:11px;font-weight:700;padding:5px 10px;border-radius:20px;">Cooperativa Bailarines</span></td>
          </tr>
        </table>
      </td>
    </tr>
    {section_html}
    {note_html}
    <tr>
      <td style="padding:0 18px 20px 18px;">
        <a href="{escape(cta_url)}" style="display:inline-block;background:#0B3D91;color:#ffffff;text-decoration:none;font-size:12px;font-weight:700;padding:10px 18px;border-radius:8px;">{escape(cta_label)}</a>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 18px 18px 18px;background:#F8FAFF;border-top:1px solid #DDE3EF;">
        <div style="font-size:12px;line-height:1.7;color:#6B7A99;">
          Este correo fue generado por el sistema de la Cooperativa Bailarines.<br>
          Si necesita ayuda, contacte a la administración.
        </div>
      </td>
    </tr>
  </table>
</body>
</html>
""".strip()


def _send_email(recipient, subject, text_body, html_body=None, attachments=None):
    if not recipient or not _email_configured():
        if not recipient:
            logger.info('Correo omitido: destinatario vacio para asunto %s', subject)
        else:
            logger.warning('Correo omitido: proveedor de correo no configurado para asunto %s', subject)
        return False

    attachments = list(attachments or [])

    def worker():
        try:
            if _using_gmail_api():
                message = EmailMultiAlternatives(
                    subject,
                    text_body,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', '') or f'Cooperativa Bailarines <{settings.GMAIL_SENDER_EMAIL}>',
                    [recipient],
                    reply_to=[settings.GMAIL_SENDER_EMAIL],
                )
                if html_body:
                    message.attach_alternative(html_body, 'text/html')
                    logo_attachment = _logo_attachment()
                    if logo_attachment:
                        message.attach(logo_attachment)
                for attachment in attachments:
                    filename, content, mimetype = attachment
                    message.attach(filename, content, mimetype)

                token_request = Request(
                    'https://oauth2.googleapis.com/token',
                    data=urlencode({
                        'client_id': settings.GMAIL_CLIENT_ID,
                        'client_secret': settings.GMAIL_CLIENT_SECRET,
                        'refresh_token': settings.GMAIL_REFRESH_TOKEN,
                        'grant_type': 'refresh_token',
                    }).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'cooperativa-bailarines/1.0',
                    },
                    method='POST',
                )
                with urlopen(token_request, timeout=settings.EMAIL_TIMEOUT) as response:
                    token_payload = json.loads(response.read().decode('utf-8'))
                access_token = token_payload['access_token']

                raw_message = urlsafe_b64encode(message.message().as_bytes()).decode('ascii').rstrip('=')
                gmail_request = Request(
                    'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                    data=json.dumps({'raw': raw_message}).encode('utf-8'),
                    headers={
                        'Authorization': f'Bearer {access_token}',
                        'Content-Type': 'application/json',
                        'User-Agent': 'cooperativa-bailarines/1.0',
                    },
                    method='POST',
                )
                with urlopen(gmail_request, timeout=settings.EMAIL_TIMEOUT) as response:
                    response.read()
                logger.info('Correo enviado por Gmail API a %s con asunto %s', recipient, subject)
                return

            message = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [recipient])
            if html_body:
                message.attach_alternative(html_body, 'text/html')
                logo_attachment = _logo_attachment()
                if logo_attachment:
                    message.attach(logo_attachment)
            for attachment in attachments:
                filename, content, mimetype = attachment
                message.attach(filename, content, mimetype)
            message.send(fail_silently=False)
            logger.info('Correo enviado por SMTP a %s con asunto %s', recipient, subject)
        except HTTPError as exc:
            detalle = exc.read().decode('utf-8', errors='ignore')
            proveedor = 'Gmail API' if _using_gmail_api() else 'SMTP'
            logger.error('Error %s enviando correo a %s con asunto %s: %s', proveedor, recipient, subject, detalle)
        except URLError as exc:
            logger.exception('Error de red enviando correo a %s con asunto %s: %s', recipient, subject, exc)
        except Exception:
            logger.exception('Error enviando correo a %s con asunto %s', recipient, subject)

    threading.Thread(target=worker, daemon=True).start()
    return True


def _credito_pdf_attachment(credito):
    from creditos.pdf_views import generar_pdf_credito

    buffer = generar_pdf_credito(credito)
    return [(f'{credito.numero}.pdf', buffer.getvalue(), 'application/pdf')]


def _send_socio_push(socio, title, body, url='/portal/inicio/', tag='portal-alerta'):
    return 0


def send_test_email(recipient):
    text_body = (
        'Hola,\n\n'
        'Este es un correo de prueba de la Cooperativa de Ahorro y Crédito Bailarines.\n'
        'Si recibió este mensaje, la configuración SMTP del sistema funciona correctamente.\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        'Correo de prueba',
        'Este mensaje confirma que la configuración de correo del sistema está funcionando correctamente.',
        sections=[
            {'label': 'Portal', 'value': _portal_url(), 'color': '#17479E'},
            {'label': 'Estado', 'value': 'Conexión SMTP activa', 'color': '#0E8A6A'},
        ],
        note='Si puede leer este correo con su estilo completo, el sistema ya está listo para enviar notificaciones reales.'
    )
    return _send_email(recipient, 'Prueba de correo - Cooperativa Bailarines', text_body, html_body)


def notify_credito_aprobado(credito):
    return False


def notify_credito_rechazado(credito):
    socio = credito.socio
    motivo = credito.motivo_rechazo or 'La administración no aprobó la solicitud en esta ocasión.'
    _send_socio_push(
        socio,
        'Solicitud no aprobada',
        f'La solicitud {credito.numero} no fue aprobada.',
        url='/portal/solicitudes/',
        tag=f'credito-rechazado-{credito.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'Su solicitud de crédito {credito.numero} fue rechazada o cancelada.\n\n'
        f'Motivo: {motivo}\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        f'Crédito no aprobado: {credito.numero}',
        f'Hola {_saludo_socio(socio)}, su solicitud no pudo continuar en esta ocasión.',
        sections=[
            {'label': 'Solicitud', 'value': credito.numero, 'color': '#17479E'},
            {'label': 'Motivo', 'value': motivo, 'color': '#E83E74'},
        ],
        note='Adjunto encontrará el PDF de la solicitud registrada para su referencia.'
    )
    return _send_email(
        socio.email,
        f'Solicitud {credito.numero}: no aprobada',
        text_body,
        html_body,
        _credito_pdf_attachment(credito),
    )


def notify_credito_desembolsado(credito):
    socio = credito.socio
    _send_socio_push(
        socio,
        'Crédito desembolsado',
        f'El crédito {credito.numero} ya fue desembolsado por ${credito.monto_transferir:.2f}.',
        url='/portal/solicitudes/',
        tag=f'credito-desembolsado-{credito.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'El crédito {credito.numero} ya fue desembolsado.\n\n'
        f'Monto transferido: ${credito.monto_transferir:.2f}\n'
        f'Interés total: ${credito.interes_total:.2f}\n'
        f'Vencimiento: {credito.fecha_pago_limite.strftime("%d/%m/%Y") if credito.fecha_pago_limite else "Pendiente"}\n'
    )
    if credito.tipo == 'mensualizado':
        text_body += f'Cuota mensual: ${credito.cuota_mensual:.2f}\n'
    else:
        text_body += f'Pago único al vencimiento: ${credito.monto_pago_final:.2f}\n'
    text_body += f'\nPortal del socio: {_portal_url()}\n\nCooperativa Bailarines'
    html_sections = [
        {'label': 'Monto transferido', 'value': f'${credito.monto_transferir:.2f}', 'color': '#0E8A6A'},
        {'label': 'Interés total', 'value': f'${credito.interes_total:.2f}', 'color': '#17479E'},
        {'label': 'Vence', 'value': credito.fecha_pago_limite.strftime('%d/%m/%Y') if credito.fecha_pago_limite else 'Pendiente', 'color': '#10336F'},
    ]
    if credito.tipo == 'mensualizado':
        html_sections.append({'label': 'Cuota mensual', 'value': f'${credito.cuota_mensual:.2f}', 'color': '#E83E74'})
    else:
        html_sections.append({'label': 'Pago único', 'value': f'${credito.monto_pago_final:.2f}', 'color': '#E83E74'})
    html_body = _email_shell(
        f'Crédito desembolsado: {credito.numero}',
        f'Hola {_saludo_socio(socio)}, su desembolso ya fue confirmado por la cooperativa.',
        sections=html_sections,
        note='Adjunto encontrará el PDF actualizado de su crédito con el detalle financiero.'
    )
    return _send_email(
        socio.email,
        f'Su crédito {credito.numero} fue desembolsado',
        text_body,
        html_body,
        _credito_pdf_attachment(credito),
    )


def notify_pago_credito_verificado(pago):
    credito = pago.credito
    socio = credito.socio
    _send_socio_push(
        socio,
        'Pago verificado',
        f'Se verificó su pago #{pago.numero_pago} del crédito {credito.numero}.',
        url='/portal/creditos/',
        tag=f'pago-credito-verificado-{pago.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'Su pago reportado del crédito {credito.numero} fue verificado correctamente.\n\n'
        f'Pago #{pago.numero_pago}\n'
        f'Monto verificado: ${pago.monto_pagado:.2f}\n'
        f'Saldo pendiente: ${credito.saldo_pendiente:.2f}\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        f'Pago verificado: {credito.numero}',
        f'Hola {_saludo_socio(socio)}, la cooperativa ya verificó su pago reportado.',
        sections=[
            {'label': 'Pago', 'value': f'#{pago.numero_pago}', 'color': '#17479E'},
            {'label': 'Monto verificado', 'value': f'${pago.monto_pagado:.2f}', 'color': '#0E8A6A'},
            {'label': 'Saldo pendiente', 'value': f'${credito.saldo_pendiente:.2f}', 'color': '#10336F'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se verificó su pago #{pago.numero_pago} del crédito {credito.numero}',
        text_body,
        html_body,
    )


def notify_pago_credito_rechazado(pago, motivo):
    credito = pago.credito
    socio = credito.socio
    _send_socio_push(
        socio,
        'Pago rechazado',
        f'Su pago #{pago.numero_pago} del crédito {credito.numero} fue rechazado.',
        url='/portal/creditos/',
        tag=f'pago-credito-rechazado-{pago.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'Su pago reportado del crédito {credito.numero} fue rechazado.\n\n'
        f'Pago #{pago.numero_pago}\n'
        f'Motivo: {motivo}\n\n'
        'Puede corregir el reporte y volver a enviarlo desde el portal.\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        f'Pago rechazado: {credito.numero}',
        f'Hola {_saludo_socio(socio)}, su reporte de pago necesita corrección antes de ser aceptado.',
        sections=[
            {'label': 'Pago', 'value': f'#{pago.numero_pago}', 'color': '#17479E'},
            {'label': 'Motivo', 'value': motivo, 'color': '#E83E74'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se rechazó su pago #{pago.numero_pago} del crédito {credito.numero}',
        text_body,
        html_body,
    )


def notify_aporte_verificado(aporte):
    socio = aporte.libreta.socio
    _send_socio_push(
        socio,
        'Aporte verificado',
        f'Se verificó su aporte de {aporte.get_mes_display()} {aporte.anio}.',
        url='/portal/libretas/',
        tag=f'aporte-verificado-{aporte.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'Su aporte de {aporte.get_mes_display()} {aporte.anio} fue verificado.\n\n'
        f'Libreta: #{aporte.libreta.numero}\n'
        f'Monto: ${aporte.monto_total:.2f}\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        f'Aporte verificado: Libreta #{aporte.libreta.numero}',
        f'Hola {_saludo_socio(socio)}, su aporte fue confirmado por la administración.',
        sections=[
            {'label': 'Periodo', 'value': f'{aporte.get_mes_display()} {aporte.anio}', 'color': '#17479E'},
            {'label': 'Monto', 'value': f'${aporte.monto_total:.2f}', 'color': '#0E8A6A'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se verificó su aporte de {aporte.get_mes_display()} {aporte.anio} - Libreta #{aporte.libreta.numero}',
        text_body,
        html_body,
    )


def notify_aporte_rechazado(aporte, motivo):
    socio = aporte.libreta.socio
    _send_socio_push(
        socio,
        'Aporte rechazado',
        f'Su aporte de {aporte.get_mes_display()} {aporte.anio} fue rechazado.',
        url='/portal/libretas/',
        tag=f'aporte-rechazado-{aporte.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'Su aporte de {aporte.get_mes_display()} {aporte.anio} fue rechazado.\n\n'
        f'Libreta: #{aporte.libreta.numero}\n'
        f'Motivo: {motivo}\n\n'
        'Puede corregirlo y reportarlo nuevamente desde el portal.\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        f'Aporte rechazado: Libreta #{aporte.libreta.numero}',
        f'Hola {_saludo_socio(socio)}, su reporte de aporte necesita corrección.',
        sections=[
            {'label': 'Periodo', 'value': f'{aporte.get_mes_display()} {aporte.anio}', 'color': '#17479E'},
            {'label': 'Motivo', 'value': motivo, 'color': '#E83E74'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se rechazó su aporte de {aporte.get_mes_display()} {aporte.anio} - Libreta #{aporte.libreta.numero}',
        text_body,
        html_body,
    )


def notify_multa_verificada(multa):
    socio = multa.socio
    _send_socio_push(
        socio,
        'Multa verificada',
        f'Se verificó el pago de su multa por ${multa.monto:.2f}.',
        url='/portal/multas/',
        tag=f'multa-verificada-{multa.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'El pago de su multa fue verificado.\n\n'
        f'Multa: {multa.descripcion}\n'
        f'Monto: ${multa.monto:.2f}\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        'Multa verificada',
        f'Hola {_saludo_socio(socio)}, su reporte de pago de multa ya fue verificado.',
        sections=[
            {'label': 'Multa', 'value': multa.descripcion, 'color': '#17479E'},
            {'label': 'Monto', 'value': f'${multa.monto:.2f}', 'color': '#0E8A6A'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se verificó su pago de multa por ${multa.monto:.2f}',
        text_body,
        html_body,
    )


def notify_multa_rechazada(multa, motivo):
    socio = multa.socio
    _send_socio_push(
        socio,
        'Multa rechazada',
        f'El pago reportado de su multa por ${multa.monto:.2f} fue rechazado.',
        url='/portal/multas/',
        tag=f'multa-rechazada-{multa.pk}',
    )
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        f'El pago reportado de su multa fue rechazado.\n\n'
        f'Multa: {multa.descripcion}\n'
        f'Motivo: {motivo}\n\n'
        'Puede corregir el reporte y volver a enviarlo desde el portal.\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    html_body = _email_shell(
        'Multa rechazada',
        f'Hola {_saludo_socio(socio)}, el reporte de pago de su multa necesita corrección.',
        sections=[
            {'label': 'Multa', 'value': multa.descripcion, 'color': '#17479E'},
            {'label': 'Motivo', 'value': motivo, 'color': '#E83E74'},
        ],
    )
    return _send_email(
        socio.email,
        f'Se rechazó su pago de multa por ${multa.monto:.2f}',
        text_body,
        html_body,
    )


def notify_cumpleanos_transferido(socio, monto_transferido, costo_operativo=0):
    _send_socio_push(
        socio,
        'Cumpleaños registrado',
        f'Se registró su incentivo de cumpleaños por ${monto_transferido:.2f}.',
        url='/portal/inicio/',
        tag=f'cumpleanos-{socio.pk}',
    )
    detalle_costo = ''
    if costo_operativo:
        detalle_costo = f'\nCosto operativo descontado: ${costo_operativo:.2f}'
    text_body = (
        f'Hola {_saludo_socio(socio)},\n\n'
        'Su incentivo de cumpleaños ya fue registrado por la cooperativa.\n\n'
        f'Monto transferido: ${monto_transferido:.2f}'
        f'{detalle_costo}\n\n'
        'Gracias por formar parte de la cooperativa.\n\n'
        f'Portal del socio: {_portal_url()}\n\n'
        'Cooperativa Bailarines'
    )
    sections = [{'label': 'Monto transferido', 'value': f'${monto_transferido:.2f}', 'color': '#0E8A6A'}]
    if costo_operativo:
        sections.append({'label': 'Costo operativo', 'value': f'${costo_operativo:.2f}', 'color': '#E83E74'})
    html_body = _email_shell(
        'Incentivo de cumpleaños registrado',
        f'Hola {_saludo_socio(socio)}, ya registramos su incentivo de cumpleaños en el sistema.',
        sections=sections,
    )
    return _send_email(
        socio.email,
        f'Su desembolso de cumpleaños fue registrado por ${monto_transferido:.2f}',
        text_body,
        html_body,
    )


def send_payment_reminders():
    from creditos.models import Credito
    from socios.models import AporteMensual, Libreta

    today = date.today()
    dias_aviso = [5, 3, 1]
    sent = 0
    errors = []

    for dias in dias_aviso:
        fecha_objetivo = today + timedelta(days=dias)
        creditos_vencen = Credito.objects.filter(
            estado__in=['desembolsado', 'mora_leve', 'mora_media', 'mora_grave'],
            fecha_pago_limite=fecha_objetivo,
        ).select_related('socio')

        for credito in creditos_vencen:
            urgencia = 'Vence en 5 días'
            if dias == 1:
                urgencia = 'Mañana vence'
            elif dias == 3:
                urgencia = 'Vence en 3 días'

            text_body = (
                f'Hola {_saludo_socio(credito.socio)},\n\n'
                f'{urgencia} su crédito {credito.numero}.\n\n'
                f'Saldo pendiente: ${credito.saldo_pendiente:.2f}\n'
                f'Fecha de vencimiento: {credito.fecha_pago_limite.strftime("%d/%m/%Y")}\n'
            )
            sections = [
                {'label': 'Crédito', 'value': credito.numero, 'color': '#17479E'},
                {'label': 'Saldo pendiente', 'value': f'${credito.saldo_pendiente:.2f}', 'color': '#E83E74'},
                {'label': 'Vencimiento', 'value': credito.fecha_pago_limite.strftime('%d/%m/%Y'), 'color': '#10336F'},
            ]
            if credito.tipo == 'mensualizado':
                text_body += f'Cuota mensual: ${credito.cuota_mensual:.2f}\n'
                sections.append({'label': 'Cuota mensual', 'value': f'${credito.cuota_mensual:.2f}', 'color': '#0E8A6A'})
            else:
                text_body += f'Monto a pagar: ${credito.saldo_pendiente:.2f}\n'
            text_body += f'\nReporte su pago desde el portal:\n{_portal_url()}\n\nCooperativa Bailarines'
            html_body = _email_shell(
                f'Recordatorio de pago: {credito.numero}',
                f'Hola {_saludo_socio(credito.socio)}, {urgencia.lower()} su crédito con la cooperativa.',
                sections=sections,
                note='Ingrese al portal para reportar su comprobante de pago.'
            )
            if _send_email(credito.socio.email, f'Recordatorio de pago - {credito.numero}', text_body, html_body):
                sent += 1
            elif credito.socio.email:
                errors.append(f'No se pudo enviar correo a {credito.socio.email}')

        if today.day == 15:
            libretas = Libreta.objects.filter(estado='activa').select_related('socio', 'periodo')
            for libreta in libretas:
                aporte = AporteMensual.objects.filter(
                    libreta=libreta,
                    mes=today.month,
                    anio=today.year,
                    estado__in=['pendiente', 'atrasado'],
                ).first()
                if not aporte or not libreta.socio.email:
                    continue
                text_body = (
                    f'Hola {_saludo_socio(libreta.socio)},\n\n'
                    f'Tiene pendiente el aporte de {aporte.get_mes_display()} {aporte.anio} '
                    f'de la libreta #{libreta.numero}.\n\n'
                    f'Monto total: ${aporte.monto_total:.2f}\n'
                    f'Ahorro: ${aporte.monto_ahorro:.2f}\n'
                    f'Lotería: ${aporte.monto_loteria:.2f}\n'
                    f'Cumpleaños: ${aporte.monto_cumpleanos:.2f}\n\n'
                    f'Reporte su comprobante aquí:\n{_portal_url()}\n\n'
                    'Cooperativa Bailarines'
                )
                html_body = _email_shell(
                    f'Recordatorio de aporte: Libreta #{libreta.numero}',
                    f'Hola {_saludo_socio(libreta.socio)}, tiene un aporte pendiente en su libreta.',
                    sections=[
                        {'label': 'Periodo', 'value': f'{aporte.get_mes_display()} {aporte.anio}', 'color': '#17479E'},
                        {'label': 'Monto total', 'value': f'${aporte.monto_total:.2f}', 'color': '#0E8A6A'},
                        {'label': 'Libreta', 'value': f'#{libreta.numero}', 'color': '#10336F'},
                    ],
                    note='Recuerde reportar su comprobante en el portal del socio.'
                )
                if _send_email(libreta.socio.email, f'Recordatorio de aporte - Libreta #{libreta.numero}', text_body, html_body):
                    sent += 1
                else:
                    errors.append(f'No se pudo enviar correo a {libreta.socio.email}')

    return sent, errors
