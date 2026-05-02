from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Reunion, AsistenciaReunion, Multa, TipoMulta
from socios.models import Socio, Libreta, Periodo


@login_required
def reuniones_list(request):
    reuniones = Reunion.objects.select_related('periodo').all()
    return render(request, 'reuniones/list.html', {'reuniones': reuniones})


@login_required
def reunion_crear(request):
    if request.method == 'POST':
        periodo = get_object_or_404(Periodo, pk=request.POST.get('periodo'))
        fecha = request.POST.get('fecha')
        from datetime import date
        fecha_obj = date.fromisoformat(fecha)
        reunion = Reunion.objects.create(
            periodo=periodo, fecha=fecha_obj,
            mes=fecha_obj.month, anio=fecha_obj.year,
            descripcion=request.POST.get('descripcion',''),
            link_reunion=request.POST.get('link_reunion', '').strip(),
            registrada_por=request.user,
        )
        messages.success(request, f'Reunión del {fecha} programada.')
        return redirect('reunion_detalle', pk=reunion.pk)
    periodos = Periodo.objects.filter(activo=True)
    return render(request, 'reuniones/form.html', {'periodos': periodos})


@login_required
def reunion_detalle(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    asistencias = reunion.asistencias.select_related('socio').all()
    socios_sin_registro = Socio.objects.filter(estado='activo').exclude(
        pk__in=asistencias.values_list('socio_id', flat=True)
    )
    return render(request, 'reuniones/detalle.html', {
        'reunion': reunion, 'asistencias': asistencias, 'socios_sin_registro': socios_sin_registro
    })


@login_required
def registrar_asistencia(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    libretas_periodo = Libreta.objects.filter(
        periodo=reunion.periodo,
        estado='activa',
        socio__estado='activo',
    ).select_related('socio').order_by('fecha_inscripcion', 'numero', 'socio__apellidos', 'socio__nombres')
    socios = []
    socios_ids = set()
    for libreta in libretas_periodo:
        if libreta.socio_id not in socios_ids:
            socios.append(libreta.socio)
            socios_ids.add(libreta.socio_id)
    socios_sin_libreta_periodo = Socio.objects.filter(estado='activo').exclude(pk__in=socios_ids).order_by('fecha_registro', 'id')
    socios.extend(list(socios_sin_libreta_periodo))

    if request.method == 'POST':
        registrados = 0
        for socio in socios:
            estado = request.POST.get(f'estado_{socio.pk}', 'presente')
            justificacion = request.POST.get(f'justificacion_{socio.pk}', '').strip()
            hora_llegada = None
            asistencia, _ = AsistenciaReunion.objects.get_or_create(
                reunion=reunion,
                socio=socio,
            )
            asistencia.estado = estado
            asistencia.justificacion = justificacion
            asistencia.hora_llegada = hora_llegada
            asistencia.multas_generadas = False
            asistencia.save()
            registrados += 1
        messages.success(request, f'Se guardo la asistencia de {registrados} socio(s). Puede volver a editarla cuando necesite.')
        return redirect('reunion_detalle', pk=reunion.pk)

    asistencias_existentes = {
        asistencia.socio_id: asistencia
        for asistencia in reunion.asistencias.select_related('socio').all()
    }
    filas_asistencia = []
    for socio in socios:
        asistencia = asistencias_existentes.get(socio.pk)
        filas_asistencia.append({
            'socio': socio,
            'estado': asistencia.estado if asistencia else 'presente',
            'justificacion': asistencia.justificacion if asistencia else '',
        })
    return render(request, 'reuniones/asistencia_form.html', {
        'reunion': reunion,
        'filas_asistencia': filas_asistencia,
    })


@login_required
def generar_multas_reunion(request, pk):
    reunion = get_object_or_404(Reunion, pk=pk)
    if request.method == 'POST':
        generadas = 0
        asistencias = reunion.asistencias.select_related('socio').filter(multas_generadas=False)
        for asistencia in asistencias:
            socio = asistencia.socio
            libretas_activas = Libreta.objects.filter(socio=socio, periodo=reunion.periodo, estado='activa')
            num_libretas = libretas_activas.count()
            monto = None
            origen = None
            por_libreta = False
            if asistencia.estado == 'falta_injustificada':
                monto, origen, por_libreta = 3, 'reunion_asistencia', True
            elif asistencia.estado == 'falta_justificada':
                monto, origen, por_libreta = 1, 'reunion_asistencia', True
            elif asistencia.estado == 'atrasado_21':
                monto, origen, por_libreta = 3, 'reunion_asistencia', False
            elif asistencia.estado == 'atrasado_11':
                monto, origen, por_libreta = 1, 'reunion_asistencia', False
            if monto:
                if por_libreta:
                    for lib in libretas_activas:
                        Multa.objects.create(
                            socio=socio, libreta=lib, origen=origen,
                            descripcion=f'Reunión {reunion.fecha}: {asistencia.get_estado_display()}',
                            monto=monto, reunion=reunion, periodo=reunion.periodo,
                            aplicada_por=request.user,
                        )
                        generadas += 1
                else:
                    Multa.objects.create(
                        socio=socio, origen=origen,
                        descripcion=f'Reunión {reunion.fecha}: {asistencia.get_estado_display()}',
                        monto=monto, reunion=reunion, periodo=reunion.periodo,
                        aplicada_por=request.user,
                    )
                    generadas += 1
            asistencia.multas_generadas = True
            asistencia.save()
        # Multas de comportamiento
        for comp in reunion.comportamientos.filter(multa_generada=False):
            Multa.objects.create(
                socio=comp.socio, origen='reunion_comportamiento',
                descripcion=f'Reunión {reunion.fecha}: {comp.descripcion}',
                monto=comp.tipo_multa.monto, reunion=reunion, periodo=reunion.periodo,
                aplicada_por=request.user,
            )
            comp.multa_generada = True
            comp.save()
            generadas += 1
        reunion.estado = 'realizada'
        reunion.save()
        messages.success(request, f'Se generaron {generadas} multa(s) de la reunión.')
        return redirect('reunion_detalle', pk=reunion.pk)
    asistencias = reunion.asistencias.select_related('socio').all()
    return render(request, 'reuniones/generar_multas.html', {'reunion': reunion, 'asistencias': asistencias})
