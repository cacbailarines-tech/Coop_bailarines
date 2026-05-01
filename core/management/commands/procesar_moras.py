import logging
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from socios.models import Libreta, AporteMensual, Periodo, Socio
from creditos.models import Credito
from multas.models import Multa
from core.utils import registrar_auditoria

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Automatización de moras y multas según reglamento (Art. 5, 8, 9, 11, 12, 23).'

    def add_arguments(self, parser):
        parser.add_argument('--fecha', type=str, help='Forzar una fecha específica (YYYY-MM-DD)')

    def handle(self, *args, **options):
        fecha_str = options.get('fecha')
        if fecha_str:
            from datetime import datetime
            hoy = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        else:
            hoy = timezone.now().date()

        self.stdout.write(f"Iniciando procesamiento de moras y multas para fecha: {hoy}")

        try:
            with transaction.atomic():
                self.procesar_dia_21(hoy)
                self.procesar_dia_1(hoy)
                self.procesar_vencimientos_diarios(hoy)
                
            self.stdout.write(self.style.SUCCESS("Procesamiento completado con éxito."))
        except Exception as e:
            logger.error(f"Error procesando moras y multas: {str(e)}")
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))

    def procesar_dia_21(self, hoy):
        """Regla: Los aportes y cuotas mensualizadas vencen el 20. El 21 se multan."""
        # Excepto en diciembre, la regla dice pago hasta el 6/12 (Art 23).
        # Implementaremos Diciembre: multa el 7 de Diciembre.
        
        es_diciembre = hoy.month == 12
        dia_corte_aportes = 7 if es_diciembre else 21

        if hoy.day != dia_corte_aportes:
            return

        periodo_activo = Periodo.objects.filter(activo=True).first()
        if not periodo_activo:
            return

        self.stdout.write(f"Ejecutando reglas de día de corte ({hoy.day}) para Aportes y Créditos Mensualizados.")

        # 1. Aportes Mensuales (Regla 11: Multa $5 por libreta)
        aportes_vencidos = AporteMensual.objects.filter(
            libreta__periodo=periodo_activo,
            mes=hoy.month,
            anio=hoy.year,
            estado='pendiente'
        )
        
        count_aportes = 0
        for aporte in aportes_vencidos:
            aporte.estado = 'atrasado'
            aporte.save(update_fields=['estado'])
            
            # Generar multa
            Multa.objects.get_or_create(
                socio=aporte.libreta.socio,
                libreta=aporte.libreta,
                periodo=periodo_activo,
                origen='mensualidad_atraso',
                mes_origen=aporte.mes,
                anio_origen=aporte.anio,
                defaults={
                    'descripcion': f'Mensualidad atrasada (Libreta #{aporte.libreta.numero}) - Mes {aporte.mes}',
                    'monto': 5.00,
                    'estado': 'pendiente'
                }
            )
            count_aportes += 1
            registrar_auditoria('multa_automatica', 'Sistema', aporte.libreta.socio, None, f"Multa $5.00 por mensualidad atrasada Libreta #{aporte.libreta.numero}")

        self.stdout.write(f"Aportes atrasados procesados: {count_aportes}")

        # 2. Créditos Mensualizados (Regla 8: $10 primera vez, $30 reincidente)
        # Evaluamos créditos desembolsados tipo 'mensualizado'
        creditos_mensuales = Credito.objects.filter(
            periodo=periodo_activo,
            tipo='mensualizado',
            estado__in=['desembolsado', 'mora_leve', 'mora_media', 'mora_grave']
        )
        count_creditos = 0
        for credito in creditos_mensuales:
            # Calcular meses transcurridos desde el desembolso
            if not credito.fecha_desembolso:
                continue
                
            meses_transcurridos = (hoy.year - credito.fecha_desembolso.year) * 12 + (hoy.month - credito.fecha_desembolso.month)
            if meses_transcurridos <= 0:
                continue # Aún no ha pasado un mes completo
                
            # Limitar a plazo_meses
            meses_a_evaluar = min(meses_transcurridos, credito.plazo_meses)
            
            # Monto esperado que debió pagar hasta ahora
            monto_esperado = credito.cuota_mensual * meses_a_evaluar
            
            # Monto pagado
            monto_pagado = credito.pagos.filter(estado='verificado').aggregate(t=Sum('monto_pagado'))['t'] or 0
            
            # Si le falta al menos media cuota para estar al día
            if monto_esperado - monto_pagado > (credito.cuota_mensual / 2):
                # Está en mora para este mes.
                # Determinar reincidencia y cambiar estado
                es_reincidente = credito.estado in ['mora_leve', 'mora_media', 'mora_grave']
                
                if es_reincidente:
                    if credito.estado == 'mora_leve':
                        credito.estado = 'mora_media'
                    elif credito.estado == 'mora_media':
                        credito.estado = 'mora_grave'
                    monto_multa = 30.00
                    origen = 'credito_atraso_reincidente'
                    desc = f'Atraso reincidente crédito {credito.numero}'
                else:
                    credito.estado = 'mora_leve'
                    monto_multa = 10.00
                    origen = 'credito_atraso_primera'
                    desc = f'Primer atraso crédito {credito.numero}'
                
                credito.save(update_fields=['estado'])
                
                Multa.objects.get_or_create(
                    socio=credito.socio,
                    libreta=credito.libreta,
                    periodo=periodo_activo,
                    origen=origen,
                    mes_origen=hoy.month,
                    anio_origen=hoy.year,
                    defaults={
                        'descripcion': desc,
                        'monto': monto_multa,
                        'estado': 'pendiente'
                    }
                )
                registrar_auditoria('multa_automatica', 'Sistema', credito.socio, None, f"Multa ${monto_multa} por mora en crédito {credito.numero}")
                count_creditos += 1

        self.stdout.write(f"Créditos mensualizados atrasados procesados: {count_creditos}")


    def procesar_vencimientos_diarios(self, hoy):
        """Regla 9: Préstamos no mensualizados (trimestrales). Al vencer la fecha límite."""
        # Se ejecuta a diario para detectar si hoy > fecha_pago_limite
        periodo_activo = Periodo.objects.filter(activo=True).first()
        if not periodo_activo:
            return

        creditos = Credito.objects.filter(
            periodo=periodo_activo,
            tipo='no_mensualizado',
            estado='desembolsado',
            fecha_pago_limite__lt=hoy
        )
        
        count = 0
        for credito in creditos:
            credito.estado = 'mora_leve'
            credito.save(update_fields=['estado'])
            
            Multa.objects.get_or_create(
                socio=credito.socio,
                libreta=credito.libreta,
                periodo=periodo_activo,
                origen='credito_atraso_primera',
                mes_origen=hoy.month,
                anio_origen=hoy.year,
                defaults={
                    'descripcion': f'Atraso en pago único de crédito {credito.numero}',
                    'monto': 30.00,
                    'estado': 'pendiente'
                }
            )
            count += 1
            registrar_auditoria('multa_automatica', 'Sistema', credito.socio, None, f"Multa $30.00 por atraso en crédito de pago único {credito.numero}")
            
        if count > 0:
            self.stdout.write(f"Créditos trimestrales vencidos procesados: {count}")

    def procesar_dia_1(self, hoy):
        """Regla 12: Pasado el último día de cada mes ($20 por incumplimiento general)"""
        # Se ejecuta el día 1 de cada mes
        if hoy.day != 1:
            return
            
        self.stdout.write("Ejecutando regla de día 1 (Incumplimiento mensual de mes vencido)")
        
        periodo_activo = Periodo.objects.filter(activo=True).first()
        if not periodo_activo:
            return

        # El mes vencido es el anterior
        mes_vencido = hoy.month - 1
        anio_vencido = hoy.year
        if mes_vencido == 0:
            mes_vencido = 12
            anio_vencido -= 1
            
        socios = Socio.objects.filter(estado='activo')
        
        count = 0
        for socio in socios:
            # ¿Tiene mensualidad atrasada del mes que cerró?
            tiene_atraso_aporte = AporteMensual.objects.filter(
                libreta__socio=socio, 
                mes=mes_vencido, 
                anio=anio_vencido, 
                estado='atrasado'
            ).exists()
            
            # ¿Tiene multas no pagadas que se hayan generado en el mes vencido?
            tiene_multa_pendiente = Multa.objects.filter(
                socio=socio,
                mes_origen=mes_vencido,
                anio_origen=anio_vencido,
                estado='pendiente'
            ).exists()
            
            # ¿Tiene mora en crédito actualmente?
            tiene_mora_credito = Credito.objects.filter(
                socio=socio,
                estado__in=['mora_leve', 'mora_media', 'mora_grave']
            ).exists()
            
            if tiene_atraso_aporte or tiene_multa_pendiente or tiene_mora_credito:
                Multa.objects.get_or_create(
                    socio=socio,
                    periodo=periodo_activo,
                    origen='mensualidad_incumplimiento',
                    mes_origen=mes_vencido,
                    anio_origen=anio_vencido,
                    defaults={
                        'descripcion': f'Incumplimiento total a fin de mes {mes_vencido}/{anio_vencido}',
                        'monto': 20.00,
                        'estado': 'pendiente'
                    }
                )
                count += 1
                registrar_auditoria('multa_automatica', 'Sistema', socio, None, f"Multa $20.00 por incumplimiento a cierre del mes {mes_vencido}")
                
        self.stdout.write(f"Incumplimientos de mes vencido generados: {count}")
