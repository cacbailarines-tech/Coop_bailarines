import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.views.decorators.http import require_POST
from .models import Socio, AccesoSocio, Libreta, AporteMensual, Periodo
from creditos.models import Credito, PagoCredito, BANCO_CHOICES
from multas.models import Multa
import hashlib
from decimal import Decimal
import random, string

from core.utils import registrar_auditoria
from core.models import PushSubscription


def hash_pin(pin):
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
            if acceso.pin != hash_pin(pin):
                messages.error(request, 'PIN incorrecto.')
                return render(request, 'portal/login.html')
        except AccesoSocio.DoesNotExist:
            messages.error(request, 'No tiene acceso al portal. Solicítelo en la cooperativa.')
            return render(request, 'portal/login.html')
        acceso.ultimo_acceso = timezone.now()
        acceso.save()
        request.session['portal_socio_id'] = socio.pk
        request.session['portal_socio_nombre'] = socio.nombre_completo
        request.session.set_expiry(0)
        return redirect('portal_inicio')
    return render(request, 'portal/login.html')


def portal_logout(request):
    request.session.flush()
    return redirect('portal_login')


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
    periodo_activo = Periodo.objects.filter(activo=True).first()
    libretas = Libreta.objects.filter(socio=socio).select_related('periodo').order_by('-periodo__anio')
    total_ahorro = libretas.aggregate(t=Sum('saldo_ahorro'))['t'] or 0
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
        aportes = libreta_actual.aportes.all().order_by('mes')
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
        def gen_num():
            year = timezone.now().year
            prefix = f'CRD-{year}-'
            existing = Credito.objects.filter(numero__startswith=prefix).values_list('numero', flat=True)
            max_num = 0
            for num in existing:
                try:
                    n = int(num.replace(prefix, ''))
                    if n > max_num: max_num = n
                except: pass
            return f"{prefix}{max_num+1:02d}" 
        credito = Credito(
            numero=gen_num(),
            periodo=periodo, socio=socio, libreta=libreta,
            tipo=tipo, monto_solicitado=monto, plazo_meses=plazo,
            banco=banco,
            numero_cuenta_bancaria=numero_cuenta,
            titular_cuenta=titular_cuenta,
            cedula_titular=cedula_titular,
            observaciones=request.POST.get('observaciones', ''),
        )
        credito.calcular_montos()
        credito.save()
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
        PagoCredito.objects.create(
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
            PagoCredito.objects.create(
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
            if comprobante_archivo:
                reiniciar_archivo()
                multa.comprobante_archivo = comprobante_archivo
            multa.save()
            total_reportado += multa.monto
            registrar_auditoria(None, 'verificaciones', 'reporte_multa_combinado_portal', f'El socio {socio.nombre_completo} reporto una multa dentro de un pago combinado.', 'Multa', multa.pk, {'comprobante': comprobante})

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
        if request.FILES.get('comprobante_archivo'):
            multa.comprobante_archivo = request.FILES.get('comprobante_archivo')
        multa.save()
        registrar_auditoria(None, 'verificaciones', 'reporte_multa_portal', f'El socio {socio.nombre_completo} reportó el pago de una multa.', 'Multa', multa.pk)
        messages.success(request, f'Pago de multa de ${multa.monto:.2f} reportado. La administración lo verificará.')
        return redirect('portal_multas')
    return render(request, 'portal/reportar_multa.html', {'multa': multa})


def portal_mis_solicitudes(request):
    socio, redir = get_socio_or_redirect(request)
    if redir:
        return redir
    # All credits of this socio
    mis_creditos = Credito.objects.filter(socio=socio).select_related('libreta').order_by('-fecha_solicitud')
    # Pending credits in queue - find position
    pendientes_cola = list(Credito.objects.filter(estado='pendiente').order_by('fecha_solicitud').values_list('pk', flat=True))
    
    solicitudes_info = []
    for c in mis_creditos:
        posicion = None
        if c.estado == 'pendiente' and c.pk in pendientes_cola:
            posicion = pendientes_cola.index(c.pk) + 1
        solicitudes_info.append({'credito': c, 'posicion': posicion})
    
    return render(request, 'portal/mis_solicitudes.html', {
        'socio': socio,
        'solicitudes_info': solicitudes_info,
    })
