from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone

from core.models import Movimiento
from core.utils import registrar_auditoria
from socios.models import Socio, Libreta, Periodo

from .models import Multa, TipoMulta, Reunion


@login_required
def multas_list(request):
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    multas = Multa.objects.select_related('socio', 'libreta', 'periodo').all()
    if q:
        multas = multas.filter(
            Q(socio__nombres__icontains=q)
            | Q(socio__apellidos__icontains=q)
            | Q(socio__cedula__icontains=q)
        )
    if estado:
        multas = multas.filter(estado=estado)
    total_pendiente = multas.filter(estado='pendiente').aggregate(t=Sum('monto'))['t'] or 0
    return render(request, 'multas/list.html', {
        'multas': multas,
        'q': q,
        'estado': estado,
        'total_pendiente': total_pendiente,
    })


@login_required
def multa_crear(request):
    if request.method == 'POST':
        socio = get_object_or_404(Socio, pk=request.POST.get('socio'))
        periodo = get_object_or_404(Periodo, pk=request.POST.get('periodo'))
        tipo_multa = get_object_or_404(TipoMulta, pk=request.POST.get('tipo_multa'))
        libreta_id = request.POST.get('libreta')
        libreta = Libreta.objects.get(pk=libreta_id) if libreta_id else None
        if tipo_multa.aplica_a == 'libreta' and not libreta:
            libretas = Libreta.objects.filter(socio=socio, periodo=periodo, estado='activa')
            for lib in libretas:
                Multa.objects.create(
                    socio=socio,
                    libreta=lib,
                    origen='manual',
                    descripcion=request.POST.get('descripcion', tipo_multa.nombre),
                    monto=tipo_multa.monto,
                    periodo=periodo,
                    aplicada_por=request.user,
                )
            registrar_auditoria(
                request.user,
                'multas',
                'crear_multa_multiple',
                f'Se aplico una multa multiple a {socio.nombre_completo}.',
                'Socio',
                socio.pk,
            )
            messages.success(
                request,
                f'Multa aplicada a {libretas.count()} libreta(s) de {socio.nombre_completo}. '
                f'Total: ${tipo_multa.monto * libretas.count()}',
            )
        else:
            multa = Multa.objects.create(
                socio=socio,
                libreta=libreta,
                origen='manual',
                descripcion=request.POST.get('descripcion', tipo_multa.nombre),
                monto=tipo_multa.monto,
                periodo=periodo,
                aplicada_por=request.user,
            )
            registrar_auditoria(
                request.user,
                'multas',
                'crear_multa',
                f'Se aplico una multa a {socio.nombre_completo}.',
                'Multa',
                multa.pk,
            )
            messages.success(request, f'Multa de ${tipo_multa.monto} aplicada a {socio.nombre_completo}.')
        return redirect('multas_list')
    socios = Socio.objects.filter(estado='activo').order_by('apellidos')
    tipos = TipoMulta.objects.filter(activo=True)
    periodos = Periodo.objects.filter(activo=True)
    return render(request, 'multas/form.html', {'socios': socios, 'tipos': tipos, 'periodos': periodos})


@login_required
def multa_pagar(request, pk):
    multa = get_object_or_404(Multa, pk=pk)
    if request.method == 'POST':
        multa.estado = 'pagada'
        multa.fecha_pago = timezone.now().date()
        multa.comprobante_pago = request.POST.get('comprobante', '')
        if request.FILES.get('comprobante_archivo'):
            multa.comprobante_archivo = request.FILES.get('comprobante_archivo')
        multa.save()

        Movimiento.objects.create(
            tipo='ingreso',
            categoria='multa',
            descripcion=f'Multa pagada - {multa.socio.nombre_completo}: {multa.descripcion}',
            monto=multa.monto,
            fecha=timezone.localdate(),
            origen='automatico',
            comprobante=multa.comprobante_pago,
            comprobante_archivo=multa.comprobante_archivo,
            socio_ref=multa.socio.nombre_completo,
            libreta_ref=str(multa.libreta.numero) if multa.libreta else '',
            registrado_por=request.user,
            observaciones=f'Multa #{multa.pk} marcada como pagada desde administracion.',
        )
        registrar_auditoria(
            request.user,
            'multas',
            'pagar_multa',
            f'Se registro el pago de la multa #{multa.pk}.',
            'Multa',
            multa.pk,
        )
        messages.success(request, f'Multa de ${multa.monto} marcada como pagada.')
        return redirect('multas_list')
    return render(request, 'multas/pagar.html', {'multa': multa})


@login_required
def tipos_multa_list(request):
    tipos = TipoMulta.objects.all()
    return render(request, 'multas/tipos_list.html', {'tipos': tipos})


@login_required
def tipo_multa_crear(request):
    if request.method == 'POST':
        TipoMulta.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion', ''),
            monto=request.POST.get('monto'),
            aplica_a=request.POST.get('aplica_a'),
        )
        messages.success(request, 'Tipo de multa creado.')
        return redirect('tipos_multa_list')
    return render(request, 'multas/tipo_form.html')
