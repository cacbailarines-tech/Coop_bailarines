from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import Socio, Libreta, AporteMensual, AccesoSocio
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
