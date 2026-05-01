from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.db import IntegrityError, transaction
from .models import AprobacionCredito, Credito, PagoCredito, MultaCredito, BANCO_CHOICES
from socios.models import Socio, Libreta, Periodo
from decimal import Decimal
import random, string
from datetime import date, timedelta

from core.email_notifications import (
    notify_credito_desembolsado,
    notify_credito_rechazado,
    notify_pago_credito_rechazado,
    notify_pago_credito_verificado,
)
from core.utils import has_role, registrar_auditoria


ROLES_APROBACION_CREDITO = ['admin', 'gerente', 'tesorero', 'cajero']


def _fechas_cuotas_credito(credito):
    fechas = []
    if not credito.fecha_desembolso:
        return fechas
    for i in range(1, credito.plazo_meses + 1):
        mes = credito.fecha_desembolso.month + i
        anio = credito.fecha_desembolso.year + (mes - 1) // 12
        mes = ((mes - 1) % 12) + 1
        try:
            fecha_cuota = date(anio, mes, credito.fecha_desembolso.day)
        except Exception:
            import calendar
            last_day = calendar.monthrange(anio, mes)[1]
            fecha_cuota = date(anio, mes, last_day)
        fechas.append((i, fecha_cuota))
    return fechas


def _usuarios_aprobacion_credito():
    return (
        User.objects.filter(is_active=True)
        .filter(Q(is_staff=True) | Q(is_superuser=True) | Q(perfil__rol__in=ROLES_APROBACION_CREDITO))
        .distinct()
        .order_by('first_name', 'last_name', 'username')
    )


def _estado_aprobaciones_credito(credito):
    requeridos = list(_usuarios_aprobacion_credito())
    aprobaciones = {
        aprobacion.usuario_id: aprobacion
        for aprobacion in credito.aprobaciones_admin.select_related('usuario').all()
    }
    aprobados = [usuario for usuario in requeridos if usuario.id in aprobaciones and aprobaciones[usuario.id].aprobado]
    pendientes = [usuario for usuario in requeridos if usuario.id not in aprobaciones or not aprobaciones[usuario.id].aprobado]
    forzada = next((aprobacion for aprobacion in aprobaciones.values() if aprobacion.forzada), None)
    filas = [
        {'usuario': usuario, 'aprobacion': aprobaciones.get(usuario.id)}
        for usuario in requeridos
    ]
    return {
        'requeridos': requeridos,
        'aprobaciones': aprobaciones,
        'filas': filas,
        'aprobados': aprobados,
        'pendientes': pendientes,
        'total': len(requeridos),
        'aprobados_count': len(aprobados),
        'completa': bool(requeridos) and len(aprobados) == len(requeridos),
        'forzada': forzada,
    }


def _puede_forzar_aprobacion(user):
    return user.is_superuser or has_role(user, 'admin', 'gerente')


def _estado_mora_por_dias(dias_atraso):
    if dias_atraso <= 0:
        return 'desembolsado'
    if dias_atraso <= 30:
        return 'mora_leve'
    if dias_atraso <= 60:
        return 'mora_media'
    return 'mora_grave'


def _sincronizar_mora_credito(credito):
    if credito.estado not in ['desembolsado', 'mora_leve', 'mora_media', 'mora_grave']:
        return {'dias_atraso': 0, 'cuotas_vencidas': []}
    if credito.saldo_pendiente <= 0:
        if credito.estado != 'pagado':
            credito.estado = 'pagado'
            credito.save(update_fields=['estado'])
        return {'dias_atraso': 0, 'cuotas_vencidas': []}

    hoy = timezone.localdate()
    dias_atraso = 0
    cuotas_vencidas = []

    if credito.tipo == 'mensualizado' and credito.fecha_desembolso:
        pagos_verificados = set(
            credito.pagos.filter(estado='verificado').values_list('numero_pago', flat=True)
        )
        for numero_cuota, fecha_cuota in _fechas_cuotas_credito(credito):
            if fecha_cuota < hoy and numero_cuota not in pagos_verificados:
                cuotas_vencidas.append((numero_cuota, fecha_cuota))
        if cuotas_vencidas:
            dias_atraso = (hoy - cuotas_vencidas[0][1]).days
    elif credito.fecha_pago_limite and credito.fecha_pago_limite < hoy:
        cuotas_vencidas.append((1, credito.fecha_pago_limite))
        dias_atraso = (hoy - credito.fecha_pago_limite).days

    nuevo_estado = _estado_mora_por_dias(dias_atraso) if cuotas_vencidas else 'desembolsado'
    if credito.estado != nuevo_estado:
        credito.estado = nuevo_estado
        credito.save(update_fields=['estado'])

    return {'dias_atraso': dias_atraso, 'cuotas_vencidas': cuotas_vencidas}

    multas_existentes = set(credito.multas.values_list('numero_cuota', flat=True))
    multas_previas = credito.multas.count()
    for indice, (numero_cuota, fecha_cuota) in enumerate(cuotas_vencidas, start=1):
        if numero_cuota in multas_existentes:
            continue
        es_primera = (multas_previas + indice) == 1
        MultaCredito.objects.create(
            credito=credito,
            numero_cuota=numero_cuota,
            tipo='primera' if es_primera else 'reincidente',
            monto=Decimal('10.00') if es_primera else Decimal('30.00'),
            observaciones=f'Generada automáticamente por atraso desde {fecha_cuota:%d/%m/%Y}.',
        )


def gen_num_credito():
    return Credito.generar_numero()


@login_required
def creditos_list(request):
    q = request.GET.get('q','')
    estado = request.GET.get('estado','')
    creditos = Credito.objects.select_related('socio','libreta','periodo').all()
    for credito in creditos:
        _sincronizar_mora_credito(credito)
    creditos = Credito.objects.select_related('socio','libreta','periodo').all()
    if q:
        creditos = creditos.filter(Q(numero__icontains=q)|Q(socio__nombres__icontains=q)|Q(socio__apellidos__icontains=q)|Q(socio__cedula__icontains=q))
    if estado:
        creditos = creditos.filter(estado=estado)
    paginator = Paginator(creditos, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'creditos/list.html', {'page_obj': page, 'q': q, 'estado': estado, 'estados': Credito.ESTADO_CHOICES})


@login_required
def credito_crear(request):
    if request.method == 'POST':
        socio = get_object_or_404(Socio, pk=request.POST.get('socio'))
        libreta = get_object_or_404(Libreta, pk=request.POST.get('libreta'))
        periodo = get_object_or_404(Periodo, pk=request.POST.get('periodo'))
        if libreta.tiene_credito_activo:
            messages.error(request, f'La libreta #{libreta.numero} ya tiene un crédito activo.')
            return redirect('credito_crear')
        monto = Decimal(request.POST.get('monto_solicitado'))
        plazo = int(request.POST.get('plazo_meses'))
        tipo = request.POST.get('tipo')
        banco = request.POST.get('banco')
        credito = Credito(
            numero=gen_num_credito(),
            periodo=periodo, socio=socio, libreta=libreta,
            tipo=tipo, monto_solicitado=monto, plazo_meses=plazo,
            banco=banco,
            numero_cuenta_bancaria=request.POST.get('numero_cuenta_bancaria',''),
            titular_cuenta=request.POST.get('titular_cuenta',''),
            cedula_titular=request.POST.get('cedula_titular',''),
            observaciones=request.POST.get('observaciones',''),
        )
        credito.calcular_montos()
        # Si hubo inserts manuales, puede existir choque por numero unique o secuencias.
        # Reintenta en caso de numero duplicado.
        for _ in range(5):
            try:
                with transaction.atomic():
                    credito.save()
                break
            except IntegrityError:
                credito.numero = gen_num_credito()
        else:
            raise
        messages.success(request, f'Solicitud {credito.numero} registrada. Monto a transferir: ${credito.monto_transferir}')
        return redirect('credito_detalle', pk=credito.pk)
    socios = Socio.objects.filter(estado='activo').order_by('apellidos')
    periodos = Periodo.objects.filter(activo=True)
    return render(request, 'creditos/form.html', {'socios': socios, 'periodos': periodos, 'bancos': BANCO_CHOICES})


@login_required
def credito_detalle(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    mora_info = _sincronizar_mora_credito(credito)
    credito.refresh_from_db()
    pagos = credito.pagos.all()
    multas = credito.multas.all()
    tabla_pagos = []
    if credito.tipo == 'mensualizado' and credito.fecha_desembolso and credito.estado in ['desembolsado','mora_leve','mora_media','mora_grave','pagado']:
        for cuota_base in credito.generar_tabla_amortizacion_plana():
            i = cuota_base['numero']
            pago_cuota = pagos.filter(numero_pago=i, estado='verificado').first()
            en_revision = pagos.filter(numero_pago=i, estado='reportado').exists()
            tabla_pagos.append({
                **cuota_base,
                'saldo': cuota_base['saldo_final'],
                'pagado': pago_cuota is not None,
                'pago': pago_cuota,
                'en_revision': en_revision,
            })
    resumen_plano = credito.obtener_resumen_cuota_plana()
    info_credito = [
        ('Nº Crédito', credito.numero),
        ('Socio', credito.socio.nombre_completo),
        ('Libreta', f'#{credito.libreta.numero}'),
        ('Tipo', credito.get_tipo_display()),
        ('Banco', credito.get_banco_display()),
        ('Cuenta', credito.numero_cuenta_bancaria),
        ('Titular', credito.titular_cuenta),
        ('Plazo', f'{credito.plazo_meses} mes(es)'),
        ('Fecha Solicitud', str(credito.fecha_solicitud.date())),
        ('Fecha Desembolso', str(credito.fecha_desembolso) if credito.fecha_desembolso else 'Pendiente'),
        ('Vencimiento', str(credito.fecha_pago_limite) if credito.fecha_pago_limite else 'Pendiente'),
    ]
    return render(request, 'creditos/detalle.html', {
        'credito': credito, 'pagos': pagos, 'multas': multas,
        'info_credito': info_credito, 'tabla_pagos': tabla_pagos,
        'resumen_plano': resumen_plano,
        'mora_info': mora_info,
        'hoy': timezone.localdate(),
    })


@login_required
def credito_aprobar(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    aprobaciones_info = _estado_aprobaciones_credito(credito)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'aprobar' and credito.estado == 'pendiente':
            if request.user not in aprobaciones_info['requeridos']:
                messages.error(request, 'Su usuario no forma parte del grupo requerido para aprobar creditos.')
                return redirect('credito_aprobar', pk=credito.pk)
            AprobacionCredito.objects.update_or_create(
                credito=credito,
                usuario=request.user,
                defaults={'aprobado': True, 'forzada': False, 'observacion': request.POST.get('observacion', '')},
            )
            aprobaciones_info = _estado_aprobaciones_credito(credito)
            registrar_auditoria(request.user, 'creditos', 'aprobar_credito_personal', f'{request.user.get_full_name() or request.user.username} aprobo el credito {credito.numero}.', 'Credito', credito.pk)
            if aprobaciones_info['completa']:
                credito.estado = 'aprobado'
                credito.fecha_aprobacion = timezone.now().date()
                credito.aprobado_por = request.user
                credito.save(update_fields=['estado', 'fecha_aprobacion', 'aprobado_por'])
                registrar_auditoria(request.user, 'creditos', 'aprobar_credito', f'El credito {credito.numero} quedo aprobado por todo el personal administrativo.', 'Credito', credito.pk)
                messages.success(request, f'Credito {credito.numero} aprobado por todo el personal. Ya puede desembolsarse.')
            else:
                messages.success(request, f'Su aprobacion fue registrada. Faltan {len(aprobaciones_info["pendientes"])} aprobacion(es) para desembolsar.')
        elif accion == 'forzar_aprobacion' and credito.estado in ['pendiente', 'aprobado']:
            if not _puede_forzar_aprobacion(request.user):
                messages.error(request, 'Solo Administrador o Gerente puede forzar una aprobacion.')
                return redirect('credito_aprobar', pk=credito.pk)
            motivo = request.POST.get('motivo_forzar', '').strip()
            if not motivo:
                messages.error(request, 'Debe indicar el motivo para forzar la aprobacion.')
                return redirect('credito_aprobar', pk=credito.pk)
            AprobacionCredito.objects.update_or_create(
                credito=credito,
                usuario=request.user,
                defaults={'aprobado': True, 'forzada': True, 'observacion': motivo},
            )
            credito.estado = 'aprobado'
            credito.fecha_aprobacion = timezone.now().date()
            credito.aprobado_por = request.user
            credito.save(update_fields=['estado', 'fecha_aprobacion', 'aprobado_por'])
            registrar_auditoria(request.user, 'creditos', 'forzar_aprobacion_credito', f'Se forzo la aprobacion del credito {credito.numero}.', 'Credito', credito.pk, {'motivo': motivo})
            messages.warning(request, f'Aprobacion forzada registrada. {credito.numero} puede desembolsarse con respaldo de auditoria.')
        elif accion == 'desembolsar' and credito.estado == 'aprobado':
            aprobaciones_info = _estado_aprobaciones_credito(credito)
            if not aprobaciones_info['completa'] and not aprobaciones_info['forzada']:
                messages.error(request, 'No se puede desembolsar: faltan aprobaciones administrativas.')
                return redirect('credito_aprobar', pk=credito.pk)
            fecha_str = request.POST.get('fecha_desembolso', '')
            try:
                fecha_desembolso = date.fromisoformat(fecha_str) if fecha_str else timezone.now().date()
            except ValueError:
                fecha_desembolso = timezone.now().date()
            credito.estado = 'desembolsado'
            credito.fecha_desembolso = fecha_desembolso
            if request.FILES.get('comprobante_desembolso'):
                credito.comprobante_desembolso = request.FILES.get('comprobante_desembolso')
            mes = fecha_desembolso.month + credito.plazo_meses
            anio = fecha_desembolso.year + (mes - 1) // 12
            mes = ((mes - 1) % 12) + 1
            import calendar
            last_day = calendar.monthrange(anio, mes)[1]
            day = min(fecha_desembolso.day, last_day)
            credito.fecha_pago_limite = date(anio, mes, day)
            credito.save()
            notify_credito_desembolsado(credito)
            from core.models import Movimiento
            # 1) Egreso por desembolso (lo que recibe el socio)
            Movimiento.objects.create(
                tipo='egreso', categoria='desembolso_credito',
                descripcion=f'Desembolso crédito {credito.numero} - {credito.socio.nombre_completo}',
                monto=credito.monto_transferir, fecha=fecha_desembolso,
                origen='automatico',
                socio_ref=credito.socio.nombre_completo,
                libreta_ref=f'#{credito.libreta.numero}',
                credito_ref=credito.numero,
                registrado_por=request.user,
            )
            # 2) Ingreso por beneficio de comision bancaria (siempre: $0.50 Pichincha, $0.59 otros)
            if credito.beneficio_transferencia > 0:
                Movimiento.objects.create(
                    tipo='ingreso', categoria='comision_banco',
                    descripcion=f'Beneficio comision bancaria - Credito {credito.numero} ({credito.get_banco_display()})',
                    monto=credito.beneficio_transferencia, fecha=fecha_desembolso,
                    origen='automatico',
                    socio_ref=credito.socio.nombre_completo,
                    credito_ref=credito.numero,
                    registrado_por=request.user,
                )
            # 3) Egreso por cargo externo del banco (solo bancos no Pichincha: $0.41)
            cargo_externo = credito.comision_bancaria - credito.beneficio_transferencia
            if cargo_externo > 0:
                Movimiento.objects.create(
                    tipo='egreso', categoria='gasto_operativo',
                    descripcion=f'Cargo externo banco {credito.get_banco_display()} - Credito {credito.numero}',
                    monto=cargo_externo, fecha=fecha_desembolso,
                    origen='automatico',
                    socio_ref=credito.socio.nombre_completo,
                    credito_ref=credito.numero,
                    registrado_por=request.user,
                )
            registrar_auditoria(request.user, 'creditos', 'desembolsar_credito', f'Se desembolso el credito {credito.numero}.', 'Credito', credito.pk, {'fecha': str(fecha_desembolso), 'adjunto': bool(credito.comprobante_desembolso)})
            messages.success(request, f'Credito desembolsado el {fecha_desembolso}. Vence: {credito.fecha_pago_limite}. Se transfirieron ${credito.monto_transferir} al socio.')
        elif accion == 'cancelar':
            credito.estado = 'cancelado'
            credito.motivo_rechazo = request.POST.get('motivo','')
            credito.save()
            notify_credito_rechazado(credito)
            registrar_auditoria(request.user, 'creditos', 'cancelar_credito', f'Se cancelo el credito {credito.numero}.', 'Credito', credito.pk, {'motivo': credito.motivo_rechazo})
            messages.warning(request, 'Credito cancelado/rechazado.')
        return redirect('credito_detalle', pk=credito.pk)
    return render(request, 'creditos/aprobar.html', {
        'credito': credito,
        'hoy': timezone.now().date(),
        'aprobaciones_info': _estado_aprobaciones_credito(credito),
        'puede_forzar_aprobacion': _puede_forzar_aprobacion(request.user),
    })


@login_required
def registrar_pago(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    if credito.estado not in ['desembolsado','mora_leve','mora_media','mora_grave']:
        messages.error(request, 'Solo se pueden registrar pagos de creditos activos.')
        return redirect('credito_detalle', pk=credito.pk)
    if request.method == 'POST':
        monto = Decimal(request.POST.get('monto_pagado'))
        comprobante = request.POST.get('comprobante_referencia','')
        es_abono = credito.tipo == 'no_mensualizado'
        saldo_ant = credito.saldo_pendiente
        nuevo_saldo = max(saldo_ant - monto, Decimal('0'))
        num_pago = credito.pagos.count() + 1
        PagoCredito.objects.create(
            credito=credito, numero_pago=num_pago,
            monto_pagado=monto, saldo_anterior=saldo_ant,
            saldo_posterior=nuevo_saldo,
            comprobante_referencia=comprobante,
            comprobante_archivo=request.FILES.get('comprobante_archivo'),
            estado='reportado', es_abono=es_abono,
            observaciones=request.POST.get('observaciones',''),
        )
        credito.saldo_pendiente = nuevo_saldo
        if nuevo_saldo <= 0:
            credito.estado = 'pagado'
        credito.save()
        registrar_auditoria(request.user, 'creditos', 'registrar_pago', f'Se registro el pago #{num_pago} del credito {credito.numero}.', 'PagoCredito', num_pago, {'credito': credito.numero, 'monto': str(monto)})
        messages.success(request, f'Pago #{num_pago} reportado por ${monto}. Pendiente de verificacion.')
        return redirect('credito_detalle', pk=credito.pk)
    return render(request, 'creditos/pago_form.html', {
        'credito': credito,
    })


@login_required
def verificar_pago(request, pk, pago_pk):
    credito = get_object_or_404(Credito, pk=pk)
    pago = get_object_or_404(PagoCredito, pk=pago_pk, credito=credito)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'verificar':
            pago.estado = 'verificado'
            pago.fecha_verificacion = timezone.now()
            pago.verificado_por = request.user
            pago.save()
            notify_pago_credito_verificado(pago)
            from core.models import Movimiento
            resumen_plano = credito.obtener_resumen_cuota_plana()
            if credito.tipo == 'mensualizado' and resumen_plano:
                interes = resumen_plano['interes_por_cuota']
                capital = resumen_plano['capital_por_cuota']
            else:
                tasa = credito.tasa_mensual
                saldo_antes = pago.saldo_anterior
                interes = (saldo_antes * tasa).quantize(Decimal('0.01'))
                capital = max(pago.monto_pagado - interes, Decimal('0'))
            # Registrar ingreso por el pago completo - aplica para AMBOS tipos (mensualizado Y no mensualizado)
            Movimiento.objects.create(
                tipo='ingreso', categoria='interes_credito',
                descripcion=f'Pago #{pago.numero_pago} - Credito {credito.numero} ({credito.get_tipo_display()}) - {credito.socio.nombre_completo}',
                monto=pago.monto_pagado,
                fecha=timezone.localdate(),
                origen='automatico',
                comprobante=pago.comprobante_referencia,
                comprobante_archivo=pago.comprobante_archivo,
                socio_ref=credito.socio.nombre_completo,
                credito_ref=credito.numero,
                registrado_por=request.user,
                observaciones=f'Capital: ${capital:.2f} | Interes estimado: ${interes:.2f}',
            )
            registrar_auditoria(request.user, 'verificaciones', 'verificar_pago_credito', f'Se verifico el pago #{pago.numero_pago} del credito {credito.numero}.', 'PagoCredito', pago.pk)
            messages.success(request, f'Pago #{pago.numero_pago} verificado.')
        elif accion == 'rechazar':
            observacion = request.POST.get('observacion','').strip()
            if not observacion:
                messages.error(request, 'Debe ingresar una observacion para rechazar el pago.')
                return render(request, 'creditos/verificar_pago.html', {
                    'credito': credito, 'pago': pago
                })
            pago.estado = 'rechazado'
            pago.observaciones = observacion
            pago.save()
            credito.saldo_pendiente = pago.saldo_anterior
            if credito.estado == 'pagado':
                credito.estado = 'desembolsado'
            credito.save()
            notify_pago_credito_rechazado(pago, observacion)
            registrar_auditoria(request.user, 'verificaciones', 'rechazar_pago_credito', f'Se rechazo el pago #{pago.numero_pago} del credito {credito.numero}.', 'PagoCredito', pago.pk, {'motivo': observacion})
            messages.warning(request, f'Pago #{pago.numero_pago} rechazado. Saldo restaurado.')
        return redirect('credito_detalle', pk=credito.pk)
    return render(request, 'creditos/verificar_pago.html', {
        'credito': credito, 'pago': pago
    })


@login_required
def agregar_multa_credito(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    mora_info = _sincronizar_mora_credito(credito)
    cuota_sugerida = mora_info['cuotas_vencidas'][0][0] if mora_info['cuotas_vencidas'] else (credito.pagos.count() + 1)
    if request.method == 'POST':
        multa = MultaCredito.objects.create(
            credito=credito,
            numero_cuota=int(request.POST.get('numero_cuota', cuota_sugerida)),
            tipo=request.POST.get('tipo', 'primera'),
            monto=Decimal(request.POST.get('monto', '10.00')),
            pagada=request.POST.get('pagada') == '1',
            fecha_pago=timezone.localdate() if request.POST.get('pagada') == '1' else None,
            observaciones=request.POST.get('observaciones', '').strip(),
        )
        registrar_auditoria(
            request.user,
            'creditos',
            'crear_multa_credito',
            f'Se agregó multa manual al crédito {credito.numero}.',
            'MultaCredito',
            multa.pk,
            {'numero_cuota': multa.numero_cuota, 'tipo': multa.tipo, 'monto': str(multa.monto)},
        )
        messages.success(request, 'Multa de crédito registrada.')
        return redirect('credito_detalle', pk=credito.pk)
    return render(request, 'creditos/multa_form.html', {
        'credito': credito,
        'multa': None,
        'tipos_multa': MultaCredito.TIPO_CHOICES,
        'numero_cuota_sugerida': cuota_sugerida,
        'mora_info': mora_info,
    })


@login_required
def editar_multa_credito(request, pk, multa_pk):
    credito = get_object_or_404(Credito, pk=pk)
    multa = get_object_or_404(MultaCredito, pk=multa_pk, credito=credito)
    if request.method == 'POST':
        multa.tipo = request.POST.get('tipo', multa.tipo)
        multa.monto = Decimal(request.POST.get('monto', multa.monto))
        multa.pagada = request.POST.get('pagada') == '1'
        multa.observaciones = request.POST.get('observaciones', '').strip()
        multa.fecha_pago = timezone.localdate() if multa.pagada else None
        multa.save()
        registrar_auditoria(
            request.user,
            'creditos',
            'editar_multa_credito',
            f'Se editó la multa de la cuota #{multa.numero_cuota} del crédito {credito.numero}.',
            'MultaCredito',
            multa.pk,
            {'tipo': multa.tipo, 'monto': str(multa.monto), 'pagada': multa.pagada},
        )
        messages.success(request, 'Multa de crédito actualizada.')
        return redirect('credito_detalle', pk=credito.pk)
    return render(request, 'creditos/multa_form.html', {
        'credito': credito,
        'multa': multa,
        'tipos_multa': MultaCredito.TIPO_CHOICES,
        'numero_cuota_sugerida': multa.numero_cuota,
        'mora_info': None,
    })
