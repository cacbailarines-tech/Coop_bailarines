import json

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.http import require_POST
from django.db import IntegrityError, transaction
from .models import Socio, AccesoSocio, Libreta, AporteMensual, Periodo
from creditos.models import Credito, PagoCredito, BANCO_CHOICES
from multas.models import Multa, Reunion
import hashlib
from decimal import Decimal
import random, string

from core.utils import registrar_auditoria
from core.models import PushSubscription
from core.email_notifications import (
    notify_admin_aporte_reportado,
    notify_admin_credito_solicitado,
    notify_admin_multa_reportada,
    notify_admin_pago_combinado_reportado,
    notify_admin_pago_credito_reportado,
)


from django.contrib.auth.hashers import make_password, check_password

def legacy_hash_pin(pin):
    return hashlib.sha256(pin.encode()).hexdigest()


def get_socio_or_redirect(request):
    sid = request.session.get('portal_socio_id')
    if not sid:
        return None, redirect('portal_login')
    try:
        return Socio.objects.get(pk=sid), None
    except Socio.DoesNotExist:
        request.session.flush()
        return None, redirect('portal_login')


# ── LOGIN / LOGOUT ────────────────────────────────────────────────────────────

def portal_login(request):
    if request.session.get('portal_socio_id'):
        return redirect('portal_inicio')
    if request.method == 'POST':
        cedula = request.POST.get('cedula', '').strip()
        pin = request.POST.get('pin', '').strip()
        try:
            socio = Socio.objects.get(cedula=cedula, estado='activo')
        except Socio.DoesNotExist:
            messages.error(request, 'Cédula no encontrada o socio inactivo.')
            return render(request, 'portal/login.html')
        try:
            acceso = socio.acceso
            if not acceso.activo:
                messages.error(request, 'Su acceso está desactivado. Contacte a la cooperativa.')
                return render(request, 'portal/login.html')
            # Verificacion de clave con migracion transparente a PBKDF2
            pin_es_valido = False
            if acceso.pin.startswith('pbkdf2_sha256$'):
                pin_es_valido = check_password(pin, acceso.pin)
            else:
                # Verificacion Legacy SHA-256
                if acceso.pin == legacy_hash_pin(pin):
                    pin_es_valido = True
                    # Migrar transparentemente
                    acceso.pin = make_password(pin)
                    acceso.save(update_fields=['pin'])

            if not pin_es_valido:
                messages.error(request, 'PIN incorrecto.')
                return render(request, 'portal/login.html')
        except AccesoSocio.DoesNotExist:
            messages.error(request, 'No tiene acceso al portal. Solicítelo en la cooperativa.')
            return render(request, 'portal/login.html')
        acceso.ultimo_acceso = timezone.now()
        acceso.save()
        request.session['portal_socio_id'] = socio.pk
        request.session['portal_socio_nombre'] = socio.nombre_completo
        keep_signed_in = request.POST.get('keep_signed_in')
        request.session.set_expiry(settings.SESSION_COOKIE_AGE if keep_signed_in else 0)
        return redirect('portal_inicio')
    return render(request, 'portal/login.html')


def portal_logout(request):
    request.session.flush()
    return redirect('portal_login')


def portal_recuperar_pin(request):
    if request.session.get('portal_socio_id'):
        return redirect('portal_inicio')
    
    estado_otp = request.session.get('otp_recuperacion_estado', False)
    
    if request.method == 'POST':
        # Cancelar proceso
        if 'cancelar' in request.POST:
            if 'otp_recuperacion_estado' in request.session:
                del request.session['otp_recuperacion_estado']
            if 'otp_codigo' in request.session:
                del request.session['otp_codigo']
            if 'otp_cedula' in request.session:
                del request.session['otp_cedula']
            if 'otp_expira' in request.session:
                del request.session['otp_expira']
            return redirect('portal_login')

        if not estado_otp:
            # PASO 1: Solicitar OTP
            cedula = request.POST.get('cedula', '').strip()
            email = request.POST.get('email', '').strip()
            
            if not cedula or not email:
                messages.error(request, 'Debe ingresar cédula y correo electrónico.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': False, 'data': request.POST})
                
            try:
                socio = Socio.objects.get(cedula=cedula, email__iexact=email, estado='activo')
            except Socio.DoesNotExist:
                messages.error(request, 'Los datos ingresados no coinciden con ningún socio activo o el correo es incorrecto.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': False, 'data': request.POST})
                
            # Generar OTP
            codigo_otp = ''.join(random.choices(string.digits, k=6))
            request.session['otp_codigo'] = codigo_otp
            request.session['otp_cedula'] = socio.cedula
            request.session['otp_expira'] = (timezone.now() + timezone.timedelta(minutes=10)).timestamp()
            request.session['otp_recuperacion_estado'] = True
            
            # Enviar correo
            asunto = "Código de Recuperación de PIN - Cooperativa Bailarines"
            mensaje = f"""Estimado(a) {socio.nombre_completo},

Ha solicitado recuperar su PIN de acceso al portal.
Su código de verificación es: {codigo_otp}

Este código expirará en 10 minutos. Si no ha solicitado este cambio, por favor ignore este mensaje.

Atentamente,
Cooperativa Bailarines"""
            try:
                from django.core.mail import EmailMessage
                email_msg = EmailMessage(
                    subject=asunto,
                    body=mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[socio.email],
                )
                email_msg.send(fail_silently=False)
                messages.success(request, f'Se ha enviado un código de 6 dígitos a su correo electrónico.')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al intentar enviar el correo. Intente más tarde.')
                # Limpiar sesión si falla
                del request.session['otp_recuperacion_estado']
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': False, 'data': request.POST})
            
            return render(request, 'portal/recuperar_pin.html', {'estado_otp': True, 'email_oculto': f"{socio.email[:3]}***@{socio.email.split('@')[1]}"})
            
        else:
            # PASO 2: Verificar OTP y cambiar PIN
            otp_ingresado = request.POST.get('otp', '').strip()
            nuevo_pin = request.POST.get('nuevo_pin', '').strip()
            confirmar_pin = request.POST.get('confirmar_pin', '').strip()
            
            # Obtener datos de sesión
            otp_guardado = request.session.get('otp_codigo')
            cedula_guardada = request.session.get('otp_cedula')
            expira_timestamp = request.session.get('otp_expira')
            
            # Verificar vigencia
            if not otp_guardado or not expira_timestamp or timezone.now().timestamp() > expira_timestamp:
                messages.error(request, 'El código de verificación ha expirado. Por favor solicite uno nuevo.')
                del request.session['otp_recuperacion_estado']
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': False})
                
            if otp_ingresado != otp_guardado:
                messages.error(request, 'El código de verificación es incorrecto.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': True})
                
            if not nuevo_pin or not confirmar_pin:
                messages.error(request, 'Debe ingresar el nuevo PIN.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': True})
                
            if nuevo_pin != confirmar_pin:
                messages.error(request, 'Los PINs no coinciden.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': True})
                
            if len(nuevo_pin) < 4:
                messages.error(request, 'El PIN debe tener al menos 4 caracteres.')
                return render(request, 'portal/recuperar_pin.html', {'estado_otp': True})
                
            try:
                socio = Socio.objects.get(cedula=cedula_guardada, estado='activo')
            except Socio.DoesNotExist:
                messages.error(request, 'Error al recuperar el socio.')
                del request.session['otp_recuperacion_estado']
                return redirect('portal_login')
                
            # Actualizar o crear el acceso
            acceso, created = AccesoSocio.objects.get_or_create(
                socio=socio,
                defaults={'pin': make_password(nuevo_pin), 'activo': True}
            )
            if not created:
                if not acceso.activo:
                    messages.error(request, 'Su acceso está desactivado. Contacte a la cooperativa.')
                    del request.session['otp_recuperacion_estado']
                    return redirect('portal_login')
                acceso.pin = make_password(nuevo_pin)
                acceso.save()
                
            registrar_auditoria(None, 'socios', 'recuperar_pin_portal', f'El socio {socio.nombre_completo} recuperó su PIN tras verificación OTP.', 'Socio', socio.pk)
                
            # Limpiar sesión
            del request.session['otp_recuperacion_estado']
            del request.session['otp_codigo']
            del request.session['otp_cedula']
            del request.session['otp_expira']
            
            messages.success(request, 'Su PIN ha sido actualizado con éxito. Ahora puede iniciar sesión.')
            return redirect('portal_login')
            
    return render(request, 'portal/recuperar_pin.html', {'estado_otp': estado_otp})


@require_POST
def portal_push_subscribe(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return JsonResponse({'ok': False, 'detail': 'Sesion expirada.'}, status=401)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'ok': False, 'detail': 'Solicitud invalida.'}, status=400)

    endpoint = (payload.get('endpoint') or '').strip()
    keys = payload.get('keys') or {}
    if not endpoint or not keys.get('p256dh') or not keys.get('auth'):
        return JsonResponse({'ok': False, 'detail': 'Suscripcion incompleta.'}, status=400)

    PushSubscription.objects.update_or_create(
        endpoint=endpoint,
        defaults={
            'socio': socio,
            'usuario': None,
            'subscription_data': payload,
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:300],
            'activa': True,
        }
    )
    return JsonResponse({'ok': True})


@require_POST
def portal_push_unsubscribe(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return JsonResponse({'ok': False, 'detail': 'Sesion expirada.'}, status=401)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        payload = {}

    endpoint = (payload.get('endpoint') or '').strip()
    if endpoint:
        PushSubscription.objects.filter(endpoint=endpoint, socio=socio).update(activa=False)
    else:
        PushSubscription.objects.filter(socio=socio).update(activa=False)
    return JsonResponse({'ok': True})


# ── INICIO ────────────────────────────────────────────────────────────────────

def portal_inicio(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
        
    proxima_reunion = Reunion.objects.filter(estado='programada', fecha__gte=timezone.now().date()).order_by('fecha').first()
    
    periodo_activo = Periodo.objects.filter(activo=True).first()
    libretas = Libreta.objects.filter(socio=socio).select_related('periodo').order_by('-periodo__anio')
    total_ahorro = AporteMensual.objects.filter(libreta__socio=socio, estado='verificado').aggregate(t=Sum('monto_ahorro'))['t'] or 0
    creditos_activos = Credito.objects.filter(
        socio=socio, estado__in=['desembolsado', 'mora_leve', 'mora_media', 'mora_grave'])
    total_deuda = creditos_activos.aggregate(t=Sum('saldo_pendiente'))['t'] or 0
    multas_pendientes = socio.multas.filter(estado='pendiente').order_by('-fecha_generacion')
    total_multas = multas_pendientes.aggregate(t=Sum('monto'))['t'] or 0
    # Aportes del mes actual pendientes
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    aportes_pendientes_mes = AporteMensual.objects.filter(
        libreta__socio=socio, mes=mes_actual, anio=anio_actual,
        estado__in=['pendiente', 'atrasado']).count()
    # Calcular días para el próximo cumpleaños
    dias_para_cumpleanos = None
    if socio.fecha_nacimiento:
        from datetime import date
        hoy = timezone.localdate()
        try:
            proximo = socio.fecha_nacimiento.replace(year=hoy.year)
        except ValueError:
            proximo = socio.fecha_nacimiento.replace(year=hoy.year, day=28)
        if proximo < hoy:
            try:
                proximo = socio.fecha_nacimiento.replace(year=hoy.year + 1)
            except ValueError:
                proximo = socio.fecha_nacimiento.replace(year=hoy.year + 1, day=28)
        dias_para_cumpleanos = (proximo - hoy).days
    return render(request, 'portal/inicio.html', {
        'socio': socio,
        'libretas': libretas,
        'total_ahorro': total_ahorro,
        'creditos_activos': creditos_activos,
        'total_deuda': total_deuda,
        'multas_pendientes': multas_pendientes[:5],
        'total_multas': total_multas,
        'aportes_pendientes_mes': aportes_pendientes_mes,
        'periodo_activo': periodo_activo,
        'dias_para_cumpleanos': dias_para_cumpleanos,
        'proxima_reunion': proxima_reunion,
    })


def portal_mis_datos(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir

    if request.method == 'POST':
        def posted_value(field_name, current_value=''):
            if field_name not in request.POST:
                return current_value
            return request.POST.get(field_name, '').strip()

        socio.nombre_preferido = request.POST.get('nombre_preferido', '').strip()
        socio.direccion = posted_value('direccion', socio.direccion)
        socio.ciudad = posted_value('ciudad', socio.ciudad)
        socio.whatsapp = posted_value('whatsapp', socio.whatsapp)
        socio.banco_preferido = posted_value('banco_preferido', socio.banco_preferido)
        socio.cuenta_bancaria_preferida = posted_value('cuenta_bancaria_preferida', socio.cuenta_bancaria_preferida)
        socio.titular_cuenta_preferida = posted_value('titular_cuenta_preferida', socio.titular_cuenta_preferida)
        socio.cedula_titular_preferida = posted_value('cedula_titular_preferida', socio.cedula_titular_preferida)
        socio.observaciones = posted_value('observaciones', socio.observaciones)
        socio.save()
        registrar_auditoria(None, 'socios', 'actualizar_datos_portal', f'El socio {socio.nombre_completo} actualizo sus datos desde el portal.', 'Socio', socio.pk)
        messages.success(request, 'Sus datos fueron actualizados. Ahora puede reutilizarlos al solicitar un credito.')
        return redirect('portal_mis_datos')

    return render(request, 'portal/mis_datos.html', {
        'socio': socio,
        'bancos': BANCO_CHOICES,
        'generos': Socio.GENERO_CHOICES,
    })


# ── LIBRETAS Y APORTES ────────────────────────────────────────────────────────

def portal_libretas(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    libretas = Libreta.objects.filter(socio=socio).select_related('periodo').order_by('-periodo__anio')
    lib_sel = request.GET.get('libreta')
    libreta_actual = None
    aportes = []
    if lib_sel:
        try:
            libreta_actual = libretas.get(pk=lib_sel)
        except Libreta.DoesNotExist:
            pass
    if not libreta_actual and libretas.exists():
        libreta_actual = libretas.first()
    if libreta_actual:
        ahorro_real = AporteMensual.objects.filter(libreta=libreta_actual, estado='verificado').aggregate(t=Sum('monto_ahorro'))['t'] or 0
        libreta_actual.ahorro_real = ahorro_real
        aportes_db = libreta_actual.aportes.all().order_by('mes')
        aportes_dict = {a.mes: a for a in aportes_db}
        for mes_num, _ in AporteMensual.MES_CHOICES:
            if mes_num in aportes_dict:
                aportes.append(aportes_dict[mes_num])
            else:
                aportes.append(AporteMensual(
                    libreta=libreta_actual, mes=mes_num, anio=libreta_actual.periodo.anio,
                    monto_ahorro=20, monto_loteria=1, monto_cumpleanos=1, monto_total=22,
                    estado='pendiente'
                ))
    return render(request, 'portal/libretas.html', {
        'socio': socio,
        'libretas': libretas,
        'libreta_actual': libreta_actual,
        'aportes': aportes,
    })


def portal_reportar_aporte(request, lib_pk, mes):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    libreta = get_object_or_404(Libreta, pk=lib_pk, socio=socio)
    aporte, _ = AporteMensual.objects.get_or_create(
        libreta=libreta, mes=mes, anio=libreta.periodo.anio,
        defaults={'monto_ahorro': 20, 'monto_loteria': 1, 'monto_cumpleanos': 1, 'monto_total': 22}
    )
    if aporte.estado == 'verificado':
        messages.info(request, 'Este aporte ya fue verificado por la administración.')
        return redirect('portal_libretas')
    if request.method == 'POST':
        comprobante = request.POST.get('comprobante', '').strip()
        if not comprobante:
            messages.error(request, 'Debe ingresar el número de comprobante o referencia de transferencia.')
            return render(request, 'portal/reportar_aporte.html', {'libreta': libreta, 'aporte': aporte})
        aporte.estado = 'reportado'
        aporte.fecha_reporte = timezone.now()
        aporte.comprobante_referencia = comprobante
        if request.FILES.get('comprobante_archivo'):
            aporte.comprobante_archivo = request.FILES.get('comprobante_archivo')
        aporte.observacion = request.POST.get('observacion', '')
        aporte.save()
        notify_admin_aporte_reportado(aporte)
        registrar_auditoria(None, 'verificaciones', 'reporte_aporte_portal', f'El socio {socio.nombre_completo} reportó un aporte.', 'AporteMensual', aporte.pk)
        messages.success(request, f'Aporte de {aporte.get_mes_display()} reportado. La administración lo verificará pronto.')
        return redirect('portal_libretas')
    return render(request, 'portal/reportar_aporte.html', {'libreta': libreta, 'aporte': aporte})


# ── CRÉDITOS ──────────────────────────────────────────────────────────────────

def portal_creditos(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    creditos = Credito.objects.filter(socio=socio).select_related('libreta').order_by('-fecha_solicitud')
    cred_sel = request.GET.get('credito')
    credito_actual = None
    pagos = []
    if cred_sel:
        try:
            credito_actual = creditos.get(pk=cred_sel)
            pagos = credito_actual.pagos.all().order_by('numero_pago')
        except Credito.DoesNotExist:
            pass
    if not credito_actual and creditos.exists():
        credito_actual = creditos.first()
        if credito_actual:
            pagos = credito_actual.pagos.all().order_by('numero_pago')
    info = []
    if credito_actual:
        info = [
            ('N° Crédito', credito_actual.numero),
            ('Tipo de Pago', credito_actual.get_tipo_display()),
            ('Monto Solicitado', f'${credito_actual.monto_solicitado:.2f}'),
            ('Saldo Pendiente', f'${credito_actual.saldo_pendiente:.2f}'),
            ('Banco', credito_actual.get_banco_display()),
            ('Interés Total (5%)', f'${credito_actual.interes_total:.2f}'),
            ('Plazo', f'{credito_actual.plazo_meses} mes(es)'),
            ('Vencimiento', str(credito_actual.fecha_pago_limite) if credito_actual.fecha_pago_limite else 'Pendiente de aprobación'),
        ]
    # Libretas disponibles para solicitar nuevo crédito
    libretas_disponibles = Libreta.objects.filter(
        socio=socio, estado='activa'
    ).exclude(creditos__estado__in=['pendiente', 'aprobado', 'desembolsado', 'mora_leve', 'mora_media', 'mora_grave'])
    return render(request, 'portal/creditos.html', {
        'socio': socio,
        'creditos': creditos,
        'credito_actual': credito_actual,
        'pagos': pagos,
        'info': info,
        'libretas_disponibles': libretas_disponibles,
    })


def portal_solicitar_credito(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    # Libretas activas sin crédito vigente
    libretas_disponibles = Libreta.objects.filter(
        socio=socio, estado='activa'
    ).exclude(creditos__estado__in=['pendiente', 'aprobado', 'desembolsado', 'mora_leve', 'mora_media', 'mora_grave'])
    if not libretas_disponibles.exists():
        messages.error(request, 'No tiene libretas disponibles para solicitar un crédito. Todas sus libretas activas ya tienen un crédito vigente.')
        return redirect('portal_creditos')
    if request.method == 'POST':
        libreta_id = request.POST.get('libreta')
        try:
            libreta = libretas_disponibles.get(pk=libreta_id)
        except Libreta.DoesNotExist:
            messages.error(request, 'Libreta no válida.')
            return render(request, 'portal/solicitar_credito.html', {'libretas': libretas_disponibles, 'bancos': BANCO_CHOICES, 'data': request.POST})
        monto = Decimal(request.POST.get('monto_solicitado', '0'))
        if monto <= 0 or monto > 500:
            messages.error(request, 'El monto debe ser entre $1 y $500.')
            return render(request, 'portal/solicitar_credito.html', {'libretas': libretas_disponibles, 'bancos': BANCO_CHOICES, 'data': request.POST})
        plazo = int(request.POST.get('plazo_meses', 1))
        periodo = libreta.periodo
        tipo = request.POST.get('tipo')
        origen_datos = request.POST.get('origen_datos', 'mis_datos')
        if origen_datos == 'mis_datos':
            banco = socio.banco_preferido
            numero_cuenta = socio.cuenta_bancaria_preferida
            titular_cuenta = socio.titular_cuenta_preferida or socio.nombre_completo
            cedula_titular = socio.cedula_titular_preferida or socio.cedula
            if not all([banco, numero_cuenta, titular_cuenta, cedula_titular]):
                messages.error(request, 'Complete primero sus datos bancarios en "Mis datos" o use la opcion "Otro".')
                return render(request, 'portal/solicitar_credito.html', {'libretas': libretas_disponibles, 'bancos': BANCO_CHOICES, 'data': request.POST, 'socio': socio})
        else:
            banco = request.POST.get('banco')
            numero_cuenta = request.POST.get('numero_cuenta_bancaria', '').strip()
            titular_cuenta = request.POST.get('titular_cuenta', '').strip()
            cedula_titular = request.POST.get('cedula_titular', '').strip()
            if not all([banco, numero_cuenta, titular_cuenta, cedula_titular]):
                messages.error(request, 'Complete todos los datos del beneficiario en la opcion "Otro".')
                return render(request, 'portal/solicitar_credito.html', {'libretas': libretas_disponibles, 'bancos': BANCO_CHOICES, 'data': request.POST, 'socio': socio})
        credito = Credito(
            numero=Credito.generar_numero(),
            periodo=periodo, socio=socio, libreta=libreta,
            tipo=tipo, monto_solicitado=monto, plazo_meses=plazo,
            banco=banco,
            numero_cuenta_bancaria=numero_cuenta,
            titular_cuenta=titular_cuenta,
            cedula_titular=cedula_titular,
            observaciones=request.POST.get('observaciones', ''),
        )
        credito.calcular_montos()
        for _ in range(5):
            try:
                with transaction.atomic():
                    credito.save()
                break
            except IntegrityError:
                credito.numero = Credito.generar_numero()
        else:
            raise
        notify_admin_credito_solicitado(credito)
        messages.success(request,
            f'Solicitud {credito.numero} enviada. '
            f'Monto solicitado: ${credito.monto_solicitado:.2f}. '
            f'Si es aprobada recibirá: ${credito.monto_transferir:.2f}. '
            f'La administración la revisará en 24 horas.')
        return redirect('portal_creditos')
    return render(request, 'portal/solicitar_credito.html', {
        'libretas': libretas_disponibles,
        'bancos': BANCO_CHOICES,
        'socio': socio,
    })


def portal_reportar_pago(request, cred_pk):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    credito = get_object_or_404(Credito, pk=cred_pk, socio=socio)
    if credito.estado not in ['desembolsado', 'mora_leve', 'mora_media', 'mora_grave']:
        messages.error(request, 'Solo puede reportar pagos de créditos activos.')
        return redirect('portal_creditos')
    # Verificar que no haya un pago pendiente de verificación
    pago_pendiente = credito.pagos.filter(estado='reportado').exists()
    if request.method == 'POST':
        monto = Decimal(request.POST.get('monto_pagado', '0'))
        comprobante = request.POST.get('comprobante_referencia', '').strip()
        if monto <= 0:
            messages.error(request, 'El monto debe ser mayor a cero.')
            return render(request, 'portal/reportar_pago.html', {'credito': credito, 'pago_pendiente': pago_pendiente})
        if not comprobante:
            messages.error(request, 'Debe ingresar el número de comprobante de la transferencia.')
            return render(request, 'portal/reportar_pago.html', {'credito': credito, 'pago_pendiente': pago_pendiente})
        saldo_ant = credito.saldo_pendiente
        nuevo_saldo = max(saldo_ant - monto, Decimal('0'))
        num_pago = credito.pagos.count() + 1
        pago = PagoCredito.objects.create(
            comprobante_archivo=request.FILES.get('comprobante_archivo'),
            credito=credito, numero_pago=num_pago,
            monto_pagado=monto,
            saldo_anterior=saldo_ant,
            saldo_posterior=nuevo_saldo,
            comprobante_referencia=comprobante,
            estado='reportado',
            es_abono=(credito.tipo == 'no_mensualizado'),
            observaciones=request.POST.get('observaciones', ''),
        )
        # Actualizar saldo provisionalmente
        credito.saldo_pendiente = nuevo_saldo
        if nuevo_saldo <= 0:
            credito.estado = 'pagado'
        credito.save()
        registrar_auditoria(None, 'verificaciones', 'reporte_pago_portal', f'El socio {socio.nombre_completo} reportó un pago para el crédito {credito.numero}.', 'Credito', credito.pk, {'monto': str(monto)})
        notify_admin_pago_credito_reportado(pago)
        messages.success(request,
            f'Pago de ${monto:.2f} reportado con comprobante {comprobante}. '
            f'Quedará como "En revisión" hasta que la administración lo verifique.')
        return redirect('portal_creditos')
    return render(request, 'portal/reportar_pago.html', {
        'credito': credito,
        'pago_pendiente': pago_pendiente,
    })


def portal_pago_combinado(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir

    aportes = AporteMensual.objects.filter(
        libreta__socio=socio,
        estado__in=['pendiente', 'atrasado'],
    ).select_related('libreta', 'libreta__periodo').order_by('libreta__numero', 'anio', 'mes')
    creditos = Credito.objects.filter(
        socio=socio,
        estado__in=['desembolsado', 'mora_leve', 'mora_media', 'mora_grave'],
    ).select_related('libreta').order_by('-fecha_solicitud')
    multas = socio.multas.filter(estado='pendiente').exclude(
        observaciones__icontains='Pago reportado por socio.'
    ).select_related('libreta').order_by('-fecha_generacion')

    if request.method == 'POST':
        aporte_ids = request.POST.getlist('aporte_ids')
        credito_ids = request.POST.getlist('credito_ids')
        multa_ids = request.POST.getlist('multa_ids')
        comprobante = request.POST.get('comprobante_referencia', '').strip()
        observacion = request.POST.get('observacion', '').strip()
        comprobante_archivo = request.FILES.get('comprobante_archivo')

        if not (aporte_ids or credito_ids or multa_ids):
            messages.error(request, 'Debe seleccionar al menos un concepto para reportar.')
            return render(request, 'portal/pago_combinado.html', {'socio': socio, 'aportes': aportes, 'creditos': creditos, 'multas': multas})
        if not comprobante:
            messages.error(request, 'Debe ingresar el numero de comprobante de la transferencia.')
            return render(request, 'portal/pago_combinado.html', {'socio': socio, 'aportes': aportes, 'creditos': creditos, 'multas': multas})

        aportes_sel = list(aportes.filter(pk__in=aporte_ids))
        creditos_sel = list(creditos.filter(pk__in=credito_ids))
        multas_sel = list(multas.filter(pk__in=multa_ids))
        total_reportado = Decimal('0.00')
        pagos_creados = []

        def reiniciar_archivo():
            if comprobante_archivo and hasattr(comprobante_archivo, 'seek'):
                comprobante_archivo.seek(0)

        for aporte in aportes_sel:
            aporte.estado = 'reportado'
            aporte.fecha_reporte = timezone.now()
            aporte.comprobante_referencia = comprobante
            if comprobante_archivo:
                reiniciar_archivo()
                aporte.comprobante_archivo = comprobante_archivo
            aporte.observacion = observacion
            aporte.save()
            total_reportado += aporte.monto_total
            registrar_auditoria(None, 'verificaciones', 'reporte_aporte_combinado_portal', f'El socio {socio.nombre_completo} reporto un aporte dentro de un pago combinado.', 'AporteMensual', aporte.pk, {'comprobante': comprobante})

        for credito in creditos_sel:
            monto = Decimal(request.POST.get(f'credito_monto_{credito.pk}', '0') or '0')
            if monto <= 0:
                messages.error(request, f'El monto reportado para el credito {credito.numero} debe ser mayor a cero.')
                return render(request, 'portal/pago_combinado.html', {'socio': socio, 'aportes': aportes, 'creditos': creditos, 'multas': multas})
            if credito.tipo == 'no_mensualizado':
                tipo_pago = 'abono'
            else:
                tipo_pago = 'cuota' if monto == credito.cuota_mensual else 'abono'
            saldo_ant = credito.saldo_pendiente
            nuevo_saldo = max(saldo_ant - monto, Decimal('0'))
            num_pago = credito.pagos.count() + 1
            es_abono = tipo_pago == 'abono' or credito.tipo == 'no_mensualizado'
            detalle = 'Pago combinado - cuota sugerida.' if tipo_pago == 'cuota' else 'Pago combinado - abono manual.'
            if observacion:
                detalle = f'{detalle} {observacion}'
            reiniciar_archivo()
            pago = PagoCredito.objects.create(
                comprobante_archivo=comprobante_archivo,
                credito=credito,
                numero_pago=num_pago,
                monto_pagado=monto,
                saldo_anterior=saldo_ant,
                saldo_posterior=nuevo_saldo,
                comprobante_referencia=comprobante,
                estado='reportado',
                es_abono=es_abono,
                observaciones=detalle,
            )
            pagos_creados.append(pago)
            credito.saldo_pendiente = nuevo_saldo
            if nuevo_saldo <= 0:
                credito.estado = 'pagado'
            credito.save()
            total_reportado += monto
            registrar_auditoria(None, 'verificaciones', 'reporte_pago_combinado_portal', f'El socio {socio.nombre_completo} reporto un pago combinado para el credito {credito.numero}.', 'Credito', credito.pk, {'monto': str(monto), 'tipo_pago': tipo_pago, 'comprobante': comprobante})

        for multa in multas_sel:
            detalle = f'Pago reportado por socio. Comprobante: {comprobante}.'
            if observacion:
                detalle = f'{detalle} Obs: {observacion}'
            multa.observaciones = detalle
            multa.comprobante_pago = comprobante
            if comprobante_archivo:
                reiniciar_archivo()
                multa.comprobante_archivo = comprobante_archivo
            multa.save()
            total_reportado += multa.monto
            registrar_auditoria(None, 'verificaciones', 'reporte_multa_combinado_portal', f'El socio {socio.nombre_completo} reporto una multa dentro de un pago combinado.', 'Multa', multa.pk, {'comprobante': comprobante})

        notify_admin_pago_combinado_reportado(
            socio,
            total_reportado,
            aportes=aportes_sel,
            pagos=pagos_creados,
            multas=multas_sel,
            comprobante=comprobante,
        )
        messages.success(
            request,
            f'Pago combinado reportado por ${total_reportado:.2f}. '
            f'Se enviaron {len(aportes_sel)} aporte(s), {len(creditos_sel)} pago(s) de credito y {len(multas_sel)} multa(s) para verificacion.'
        )
        return redirect('portal_pago_combinado')

    return render(request, 'portal/pago_combinado.html', {
        'socio': socio,
        'aportes': aportes,
        'creditos': creditos,
        'multas': multas,
    })


# ── MULTAS ────────────────────────────────────────────────────────────────────

def portal_multas(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    # TODAS las multas del socio, tanto por socio como por sus libretas
    multas_directas = socio.multas.select_related('libreta', 'periodo').order_by('-fecha_generacion')
    total_pendiente = multas_directas.filter(estado='pendiente').aggregate(t=Sum('monto'))['t'] or 0
    total_pagado = multas_directas.filter(estado='pagada').aggregate(t=Sum('monto'))['t'] or 0
    return render(request, 'portal/multas.html', {
        'socio': socio,
        'multas': multas_directas,
        'total_pendiente': total_pendiente,
        'total_pagado': total_pagado,
    })


def portal_reportar_multa(request, multa_pk):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    multa = get_object_or_404(Multa, pk=multa_pk, socio=socio, estado='pendiente')
    if request.method == 'POST':
        comprobante = request.POST.get('comprobante', '').strip()
        if not comprobante:
            messages.error(request, 'Debe ingresar el número de comprobante.')
            return render(request, 'portal/reportar_multa.html', {'multa': multa})
        # Store comprobante in observaciones and mark as "reported" (admin still must confirm)
        multa.observaciones = f'Pago reportado por socio. Comprobante: {comprobante}. Obs: {request.POST.get("observacion","")}'
        multa.comprobante_pago = comprobante
        if request.FILES.get('comprobante_archivo'):
            multa.comprobante_archivo = request.FILES.get('comprobante_archivo')
        multa.save()
        notify_admin_multa_reportada(multa)
        registrar_auditoria(None, 'verificaciones', 'reporte_multa_portal', f'El socio {socio.nombre_completo} reportó el pago de una multa.', 'Multa', multa.pk)
        messages.success(request, f'Pago de multa de ${multa.monto:.2f} reportado. La administración lo verificará.')
        return redirect('portal_multas')
    return render(request, 'portal/reportar_multa.html', {'multa': multa})


def portal_mis_solicitudes(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir

    estado = request.GET.get('estado', '').strip()
    mis_creditos = Credito.objects.filter(socio=socio).select_related('libreta').order_by('-fecha_solicitud')
    conteos_estado = {}
    for key, _label in Credito.ESTADO_CHOICES:
        conteos_estado[key] = mis_creditos.filter(estado=key).count()
    total_solicitudes = mis_creditos.count()

    if estado:
        mis_creditos = mis_creditos.filter(estado=estado)

    pendientes_cola = list(Credito.objects.filter(estado='pendiente').order_by('fecha_solicitud').values_list('pk', flat=True))

    solicitudes_info = []
    for c in mis_creditos:
        posicion = None
        if c.estado == 'pendiente' and c.pk in pendientes_cola:
            posicion = pendientes_cola.index(c.pk) + 1
        solicitudes_info.append({
            'credito': c,
            'posicion': posicion,
            'estado_badge': (
                'badge-warning' if c.estado == 'pendiente'
                else 'badge-primary' if c.estado == 'aprobado'
                else 'badge-success' if c.estado in ['desembolsado', 'pagado']
                else 'badge-danger' if 'mora' in c.estado
                else 'badge-secondary'
            ),
            'estado_texto': 'En revisión' if c.estado == 'pendiente' else c.get_estado_display(),
        })

    return render(request, 'portal/mis_solicitudes.html', {
        'socio': socio,
        'solicitudes_info': solicitudes_info,
        'estado_actual': estado,
        'filtros_estado': [
            {'value': '', 'label': 'Todas', 'count': total_solicitudes},
            {'value': 'pendiente', 'label': 'Pendiente', 'count': conteos_estado.get('pendiente', 0)},
            {'value': 'aprobado', 'label': 'Aprobado', 'count': conteos_estado.get('aprobado', 0)},
            {'value': 'desembolsado', 'label': 'Desembolsado', 'count': conteos_estado.get('desembolsado', 0)},
            {'value': 'pagado', 'label': 'Pagado', 'count': conteos_estado.get('pagado', 0)},
            {'value': 'mora_leve', 'label': 'Mora leve', 'count': conteos_estado.get('mora_leve', 0)},
            {'value': 'mora_media', 'label': 'Mora media', 'count': conteos_estado.get('mora_media', 0)},
            {'value': 'mora_grave', 'label': 'Mora grave', 'count': conteos_estado.get('mora_grave', 0)},
            {'value': 'cancelado', 'label': 'Cancelado', 'count': conteos_estado.get('cancelado', 0)},
        ],
    })

import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def portal_chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Solo POST'}, status=405)
        
    socio_id = request.session.get('portal_socio_id')
    if not socio_id:
        return JsonResponse({'error': 'No autorizado'}, status=401)
        
    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get('message', '')
        
        if not mensaje_usuario:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)
            
        socio = Socio.objects.get(id=socio_id)
        
        # Recopilar contexto detallado
        libretas = Libreta.objects.filter(socio=socio)
        info_libretas_list = []
        for l in libretas:
            ahorro_real = AporteMensual.objects.filter(libreta=l, estado='verificado').aggregate(t=Sum('monto_ahorro'))['t'] or 0
            pagos_detalles = AporteMensual.objects.filter(libreta=l).values_list('mes', 'estado')
            detalle_meses = ", ".join([f"M{m[0]}:{m[1]}" for m in pagos_detalles])
            info_libretas_list.append(f"Libreta #{l.numero} (Ahorro Puro: ${ahorro_real}) [Meses: {detalle_meses}]")
        info_libretas = " | ".join(info_libretas_list)
        
        creditos = Credito.objects.filter(socio=socio)
        info_creditos = " | ".join([f"Crédito {c.numero} ({c.get_tipo_display()}) - Saldo: ${c.saldo_pendiente} - Estado: {c.get_estado_display()} - Plazo: {c.plazo_meses} meses" for c in creditos])
        if not info_creditos: info_creditos = "Sin historial de créditos."
        
        multas = Multa.objects.filter(socio=socio)
        info_multas = " | ".join([f"${m.monto} ({m.descripcion}) - Estado: {m.estado}" for m in multas])
        if not info_multas: info_multas = "Sin historial de multas."
        
        contexto_sistema = f"""Eres el Asistente Virtual Oficial de la Cooperativa Bailarines.
Estás hablando con el socio: {socio.nombre_completo} (Cédula: {socio.cedula}, Banco: {socio.banco_preferido}, Teléfono: {socio.telefono}).
Si pregunta por su fecha de nacimiento: {socio.fecha_nacimiento}.

TUS REGLAS DE CONOCIMIENTO (LOS 34 REGLAMENTOS DE LA COOPERATIVA):
1. Reuniones último domingo de cada mes.
2. Multas reuniones: justificada $1, injustificada $3, atraso min 11 ($1), min 21 ($3).
3. Faltas se justifican 24hr antes.
4. Inscripción $20 (plazo 20 enero).
5. Ahorro mensual $22 ($20 ahorro, $1 lotería, $1 cumpleaños) hasta el 20 de cada mes.
6. Pagos depositados a cuenta autorizada.
7. Enviar comprobantes detallados al grupo.
8. Multa crédito mensualizado atrasado: 1ra vez $10, reincidente $30.
9. Multa crédito trimestral atrasado: $30.
10. Retiro: se devuelve ahorro (no inscripción), si hay deudas se descuenta.
11. Mensualidad hasta el 20, atraso multa de $5 por libreta.
12. Fin de mes sin pagar = multa general de $20 por incumplimiento.
13. Rifa fin de mes $50 con últimos 3 números de lotería (debe estar al día para ganar).
14. Préstamos trimestrales: interés descontado por adelantado.
15. Préstamos mensualizados: interés sumado al valor y dividido para los meses.
16. Mínimo préstamo $500, si no saca préstamo en el periodo paga interés mínimo de $100 en noviembre.
17. Para solicitar préstamo debe estar al día.
18. Tiempo de aprobación de préstamo: 24hrs (depende de saldo).
19. Aprobación por orden de ingreso.
20. Solicitudes llenas correctamente.
21. Última solicitud de préstamo: 31 de octubre.
22. Al día hasta 30 noviembre para cierres.
23. Mensualidad diciembre pago máximo hasta 06/12.
24. Incumplir pagos de préstamos reduce valores en futuras solicitudes.
25. Valores pendientes a fin de periodo se descuentan de otras libretas del socio y pierde la libreta.
26. Integrantes nuevos recomendados por socio activo (1 recomendación por cada 2 libretas).
27. Nuevos socios inician con 1 sola libreta.
28. El garante/recomendante asume las deudas si el nuevo socio no paga.
29. Menor de edad requiere representante adulto.
30. Reuniones: asistir con buena presencia.
31. Mal comportamiento en reunión (cámaras apagadas, gorras, alcohol, etc) = multa $1.
32. Regalo de Cumpleaños = $12 en el mes de su cumpleaños (después del 6 dic, se entrega en el cierre).
33. Pago mensualidad de todo el año adelantado = opción de no hacer préstamo obligatorio.
34. Multa directiva si incumple = $10.

DATOS FINANCIEROS DE {socio.nombre_completo}:
- Libretas: {info_libretas}
- Créditos (Activos e Históricos): {info_creditos}
- Multas (Pendientes y Pagadas): {info_multas}

Responde siempre basándote EN ESTA INFORMACIÓN EXACTA. No inventes. Sé amable, claro y directo. Responde como un humano experto de la cooperativa. Si te preguntan sobre reglas, explícalas detalladamente."""

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return JsonResponse({'reply': 'La clave de IA (GEMINI_API_KEY) no está configurada. Avisa a administración.'})

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[contexto_sistema, mensaje_usuario]
            )
            respuesta = response.text
            return JsonResponse({'reply': respuesta})
        except Exception as api_e:
            return JsonResponse({'reply': f'Hubo un problema procesando tu mensaje con la IA. Error: {str(api_e)}'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
