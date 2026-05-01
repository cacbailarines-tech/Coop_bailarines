from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Max
from .models import Socio, Libreta, AporteMensual, AccesoSocio, Periodo
from core.utils import require_roles
import json
from django.contrib.auth.hashers import make_password

@login_required
def socios_list(request):
    q = request.GET.get('q','')
    socios = Socio.objects.all()
    if q:
        socios = socios.filter(Q(nombres__icontains=q)|Q(apellidos__icontains=q)|Q(cedula__icontains=q))
    paginator = Paginator(socios, 15)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'socios/list.html', {'page_obj': page, 'q': q})

@login_required
def socio_crear(request):
    from .models import Periodo
    if request.method == 'POST':
        cedula = request.POST.get('cedula','').strip()
        if Socio.objects.filter(cedula=cedula).exists():
            messages.error(request, 'Ya existe un socio con esa cédula.')
            return render(request, 'socios/form.html', {'accion':'Registrar','data':request.POST})
        rec_id = request.POST.get('recomendado_por')
        socio = Socio(
            cedula=cedula,
            nombres=request.POST.get('nombres','').strip(),
            apellidos=request.POST.get('apellidos','').strip(),
            fecha_nacimiento=request.POST.get('fecha_nacimiento'),
            genero=request.POST.get('genero'),
            direccion=request.POST.get('direccion',''),
            ciudad=request.POST.get('ciudad','Quito'),
            telefono=request.POST.get('telefono',''),
            whatsapp=request.POST.get('whatsapp',''),
            email=request.POST.get('email',''),
            es_menor=request.POST.get('es_menor')=='on',
            representante_nombre=request.POST.get('representante_nombre',''),
            representante_cedula=request.POST.get('representante_cedula',''),
            recomendado_por_id=rec_id if rec_id else None,
            observaciones=request.POST.get('observaciones',''),
        )
        socio.save()
        messages.success(request, f'Socio {socio.nombre_completo} registrado exitosamente.')
        return redirect('socio_detalle', pk=socio.pk)
    socios_activos = Socio.objects.filter(estado='activo')
    return render(request, 'socios/form.html', {'accion':'Registrar','socios':socios_activos})

@login_required
def socio_detalle(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    libretas = socio.libretas.select_related('periodo').order_by('-periodo__anio','numero')
    multas_pendientes = socio.multas.filter(estado='pendiente')
    total_multas = multas_pendientes.aggregate(t=Sum('monto'))['t'] or 0
    creditos_activos = socio.creditos.filter(estado__in=['desembolsado','mora_leve','mora_media','mora_grave'])
    return render(request, 'socios/detalle.html', {
        'socio': socio, 'libretas': libretas,
        'multas_pendientes': multas_pendientes, 'total_multas': total_multas,
        'creditos_activos': creditos_activos,
    })

@login_required
def socio_editar(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.cedula = request.POST.get('cedula', socio.cedula)
        socio.nombres = request.POST.get('nombres', socio.nombres)
        socio.apellidos = request.POST.get('apellidos', socio.apellidos)
        socio.direccion = request.POST.get('direccion', socio.direccion)
        socio.ciudad = request.POST.get('ciudad', socio.ciudad)
        socio.telefono = request.POST.get('telefono', socio.telefono)
        socio.whatsapp = request.POST.get('whatsapp', socio.whatsapp)
        socio.email = request.POST.get('email', socio.email)
        socio.es_menor = request.POST.get('es_menor') == 'on'
        socio.representante_nombre = request.POST.get('representante_nombre','')
        socio.representante_cedula = request.POST.get('representante_cedula','')
        socio.estado = request.POST.get('estado', socio.estado)
        socio.observaciones = request.POST.get('observaciones','')
        socio.save()
        messages.success(request, 'Datos actualizados.')
        return redirect('socio_detalle', pk=socio.pk)
    socios_activos = Socio.objects.filter(estado='activo').exclude(pk=pk)
    return render(request, 'socios/form.html', {'accion':'Editar','socio':socio,'socios':socios_activos})

@login_required
def socio_crear_acceso(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        pin = request.POST.get('pin','').strip()
        confirmar = request.POST.get('confirmar','').strip()
        if len(pin) < 4:
            messages.error(request, 'El PIN debe tener al menos 4 caracteres.')
        elif pin != confirmar:
            messages.error(request, 'Los PINs no coinciden.')
        else:
            acceso, created = AccesoSocio.objects.get_or_create(socio=socio)
            acceso.pin = make_password(pin)
            acceso.activo = True
            acceso.save()
            messages.success(request, f'Acceso al portal {"creado" if created else "actualizado"} para {socio.nombre_completo}.')
            return redirect('socio_detalle', pk=socio.pk)
    has_access = hasattr(socio, 'acceso')
    return render(request, 'socios/crear_acceso.html', {'socio': socio, 'has_access': has_access})

@login_required
@require_roles('admin', 'tesorero', 'gerente')
def dashboard_aportes(request):
    periodo_id = request.GET.get('periodo')
    periodos = Periodo.objects.all().order_by('-anio')
    
    if not periodo_id:
        p_activo = periodos.filter(activo=True).first()
        periodo_id = p_activo.id if p_activo else None

    aportes = AporteMensual.objects.select_related('libreta__socio')
    
    if periodo_id:
        aportes = aportes.filter(libreta__periodo_id=periodo_id)

    aportes_verificados = aportes.filter(estado='verificado')
    
    total_recaudado = aportes_verificados.aggregate(t=Sum('monto_total'))['t'] or 0
    total_ahorro = aportes_verificados.aggregate(t=Sum('monto_ahorro'))['t'] or 0
    total_loteria = aportes_verificados.aggregate(t=Sum('monto_loteria'))['t'] or 0
    total_cumpleanos = aportes_verificados.aggregate(t=Sum('monto_cumpleanos'))['t'] or 0
    total_extra = total_loteria + total_cumpleanos
    
    aportes_atrasados_count = aportes.filter(estado='atrasado').count()
    aportes_pendientes_count = aportes.filter(estado='pendiente').count()
    
    meses_data = []
    meses_labels = [m[1] for m in AporteMensual.MES_CHOICES]
    for mes_num, _ in AporteMensual.MES_CHOICES:
        total_mes = aportes_verificados.filter(mes=mes_num).aggregate(t=Sum('monto_total'))['t'] or 0
        meses_data.append(float(total_mes))

    distribucion_data = [float(total_ahorro), float(total_loteria), float(total_cumpleanos)]

    top_atrasados = []
    if periodo_id:
        libretas_atrasadas = Libreta.objects.filter(periodo_id=periodo_id).annotate(
            atrasos=Count('aportes', filter=Q(aportes__estado='atrasado'))
        ).filter(atrasos__gt=0).order_by('-atrasos')[:5]
        top_atrasados = libretas_atrasadas
        
    context = {
        'periodos': periodos,
        'periodo_id': int(periodo_id) if periodo_id else '',
        'total_recaudado': total_recaudado,
        'total_ahorro': total_ahorro,
        'total_extra': total_extra,
        'aportes_atrasados_count': aportes_atrasados_count,
        'aportes_pendientes_count': aportes_pendientes_count,
        'meses_labels_json': json.dumps(meses_labels),
        'meses_data_json': json.dumps(meses_data),
        'distribucion_data_json': json.dumps(distribucion_data),
        'top_atrasados': top_atrasados,
    }
    return render(request, 'socios/dashboard_aportes.html', context)
