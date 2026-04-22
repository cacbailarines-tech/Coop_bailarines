from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from .models import Socio, Libreta, AporteMensual, Periodo
from core.email_notifications import notify_aporte_rechazado, notify_aporte_verificado


@login_required
def libretas_list(request):
    q = request.GET.get('q','')
    periodo_id = request.GET.get('periodo','')
    libretas = Libreta.objects.select_related('socio','periodo').all()
    if q:
        libretas = libretas.filter(Q(socio__nombres__icontains=q)|Q(socio__apellidos__icontains=q)|Q(socio__cedula__icontains=q)|Q(numero__icontains=q))
    if periodo_id:
        libretas = libretas.filter(periodo_id=periodo_id)
    periodos = Periodo.objects.all()
    paginator = Paginator(libretas, 20)
    page = paginator.get_page(request.GET.get('page'))
    from django.db.models import Count, Q
    for lib in page.object_list:
        lib.aportes_verificados_count = lib.aportes.filter(estado='verificado').count()
    return render(request, 'libretas/list.html', {
        'page_obj': page, 'q': q, 'periodos': periodos, 'periodo_id': periodo_id,
    })


@login_required
def libreta_crear(request):
    if request.method == 'POST':
        socio = get_object_or_404(Socio, pk=request.POST.get('socio'))
        periodo = get_object_or_404(Periodo, pk=request.POST.get('periodo'))
        if not periodo.activo:
            messages.error(request, 'Solo se pueden crear libretas en el periodo activo.')
            return redirect('libreta_crear')
        # Número continuo global
        ultimo = Libreta.objects.order_by('-numero').first()
        numero = (ultimo.numero + 1) if ultimo else 1
        libreta = Libreta.objects.create(
            numero=numero, periodo=periodo, socio=socio,
            inscripcion_pagada=request.POST.get('inscripcion_pagada')=='on',
        )
        if libreta.inscripcion_pagada:
            libreta.fecha_inscripcion_pago = timezone.now().date()
            libreta.save()
            # Register ingreso for inscripcion
            from core.models import Movimiento
            Movimiento.objects.create(
                tipo='ingreso', categoria='inscripcion',
                descripcion=f'Inscripción Libreta #{libreta.numero} — {socio.nombre_completo} — Periodo {periodo.anio}',
                monto=20, fecha=timezone.now().date(),
                origen='automatico',
                socio_ref=socio.nombre_completo,
                libreta_ref=f'#{libreta.numero}',
                registrado_por=request.user,
            )
        # Generar aportes pendientes para el periodo
        for mes in range(1, 13):
            AporteMensual.objects.get_or_create(
                libreta=libreta, mes=mes, anio=periodo.anio,
                defaults={'monto_ahorro': 20, 'monto_loteria': 1, 'monto_cumpleanos': 1, 'monto_total': 22}
            )
        messages.success(request, f'Libreta #{libreta.numero} creada para {socio.nombre_completo}.')
        return redirect('libreta_detalle', pk=libreta.pk)
    socios = Socio.objects.filter(estado='activo').order_by('apellidos')
    periodos = Periodo.objects.filter(activo=True)
    return render(request, 'libretas/form.html', {'socios': socios, 'periodos': periodos})


@login_required
def libreta_detalle(request, pk):
    libreta = get_object_or_404(Libreta, pk=pk)
    aportes = libreta.aportes.all().order_by('mes')
    creditos = libreta.creditos.all()
    multas = libreta.multas.all()
    return render(request, 'libretas/detalle.html', {
        'libreta': libreta, 'aportes': aportes,
        'creditos': creditos, 'multas': multas,
    })


@login_required
def aporte_verificar(request, pk, mes):
    libreta = get_object_or_404(Libreta, pk=pk)
    aporte, _ = AporteMensual.objects.get_or_create(
        libreta=libreta, mes=mes, anio=libreta.periodo.anio,
        defaults={'monto_ahorro': 20, 'monto_loteria': 1, 'monto_cumpleanos': 1, 'monto_total': 22}
    )
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'verificar':
            aporte.estado = 'verificado'
            aporte.fecha_verificacion = timezone.now()
            aporte.comprobante_referencia = request.POST.get('comprobante','')
            aporte.observacion = request.POST.get('observacion','')
            aporte.save()
            notify_aporte_verificado(aporte)
            # Actualizar saldo de libreta
            libreta.saldo_ahorro += aporte.monto_ahorro
            libreta.save()
            messages.success(request, f'Aporte de {aporte.get_mes_display()} verificado. Saldo libreta: ${libreta.saldo_ahorro}')
        elif accion == 'rechazar':
            aporte.estado = 'pendiente'
            aporte.observacion = request.POST.get('observacion','')
            aporte.save()
            notify_aporte_rechazado(aporte, aporte.observacion or 'Reporte rechazado por administracion.')
            messages.warning(request, 'Aporte marcado como pendiente.')
        return redirect('libreta_detalle', pk=libreta.pk)
    return render(request, 'libretas/aporte_form.html', {'libreta': libreta, 'aporte': aporte})


@login_required
def aportes_list(request):
    """Ver todos los aportes reportados pendientes de verificación"""
    aportes = AporteMensual.objects.filter(estado='reportado').select_related('libreta__socio','libreta__periodo')
    return render(request, 'libretas/aportes_pendientes.html', {'aportes': aportes})


@login_required
def aporte_accion(request, pk):
    aporte = get_object_or_404(AporteMensual, pk=pk)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'verificar':
            aporte.estado = 'verificado'
            aporte.fecha_verificacion = timezone.now()
            aporte.comprobante_referencia = request.POST.get('comprobante','')
            aporte.save()
            notify_aporte_verificado(aporte)
            libreta = aporte.libreta
            libreta.saldo_ahorro += aporte.monto_ahorro
            libreta.save()
            messages.success(request, f'Aporte verificado: Libreta #{libreta.numero} - {aporte.get_mes_display()}')
        elif accion == 'rechazar':
            aporte.estado = 'pendiente'
            aporte.observacion = request.POST.get('observacion','Rechazado por administración')
            aporte.save()
            notify_aporte_rechazado(aporte, aporte.observacion)
            messages.warning(request, 'Aporte rechazado.')
        return redirect('aportes_list')
    return render(request, 'libretas/aporte_accion.html', {'aporte': aporte})

from django.http import JsonResponse

@login_required
def api_libretas_disponibles(request):
    socio_id = request.GET.get('socio')
    if not socio_id:
        return JsonResponse([], safe=False)
    libretas = Libreta.objects.filter(socio_id=socio_id, estado='activa').select_related('periodo')
    # Exclude those with active credit
    disponibles = [lib for lib in libretas if not lib.tiene_credito_activo]
    data = [{'id': lib.pk, 'numero': lib.numero, 'periodo': lib.periodo.anio} for lib in disponibles]
    return JsonResponse(data, safe=False)
