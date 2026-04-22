from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RifaMensual
from socios.models import Libreta, Periodo

@login_required
def rifas_list(request):
    rifas = RifaMensual.objects.select_related('periodo','libreta_ganadora__socio').all()
    return render(request, 'cuentas/rifas_list.html', {'rifas': rifas})

@login_required
def rifa_crear(request):
    if request.method == 'POST':
        periodo = get_object_or_404(Periodo, pk=request.POST.get('periodo'))
        mes = int(request.POST.get('mes'))
        anio = int(request.POST.get('anio'))
        numeros = request.POST.get('numeros_loteria','')
        libreta_id = request.POST.get('libreta_ganadora')
        libreta = Libreta.objects.get(pk=libreta_id) if libreta_id else None
        al_dia = request.POST.get('socio_al_dia') == 'on'
        estado = 'ganada' if libreta and al_dia else ('no_ganada' if not libreta else 'ganada')
        RifaMensual.objects.create(
            periodo=periodo, mes=mes, anio=anio,
            numeros_loteria=numeros, libreta_ganadora=libreta,
            socio_al_dia=al_dia, estado=estado,
            registrado_por=request.user,
            observaciones=request.POST.get('observaciones','')
        )
        messages.success(request, 'Rifa registrada.')
        return redirect('rifas_list')
    periodos = Periodo.objects.filter(activo=True)
    libretas = Libreta.objects.filter(estado='activa').select_related('socio')
    return render(request, 'cuentas/rifa_form.html', {'periodos': periodos, 'libretas': libretas})

@login_required
def rifa_detalle(request, pk):
    rifa = get_object_or_404(RifaMensual, pk=pk)
    return render(request, 'cuentas/rifa_detalle.html', {'rifa': rifa})
