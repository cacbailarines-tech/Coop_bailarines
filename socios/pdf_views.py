from io import BytesIO
import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Sum

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import Libreta, AporteMensual

def generar_pdf_estado_cuenta(libreta):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm
    )

    story = []
    
    azul = colors.HexColor('#17479E')
    azul_oscuro = colors.HexColor('#10336F')
    verde = colors.HexColor('#0E8A6A')
    gris = colors.HexColor('#64748B')
    gris_borde = colors.HexColor('#D9E2F2')
    gris_fondo = colors.HexColor('#F6F9FF')

    subtitle_style = ParagraphStyle('subtitle', fontName='Helvetica-Bold', fontSize=13, leading=15, textColor=verde, alignment=TA_CENTER, spaceBefore=2, spaceAfter=14)
    section_style = ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=11, textColor=azul_oscuro, spaceBefore=12, spaceAfter=6)
    small_style = ParagraphStyle('small', fontName='Helvetica', fontSize=8, textColor=gris, alignment=TA_CENTER)
    label_style = ParagraphStyle('label', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=gris, alignment=TA_LEFT)
    money_style = ParagraphStyle('money', fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=verde, alignment=TA_RIGHT)

    def build_detail_table(rows):
        table = Table(rows, colWidths=[3.2 * cm, 5.3 * cm, 3.2 * cm, 5.3 * cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (0, -1), gris),
            ('TEXTCOLOR', (2, 0), (2, -1), gris),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.6, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, gris_borde),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, gris_fondo]),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return table

    def build_metric_card(title, value):
        card = Table(
            [[Paragraph(title, label_style)], [Paragraph(value, money_style)]],
            colWidths=[5.45 * cm], rowHeights=[0.7 * cm, 1.0 * cm],
        )
        card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.8, gris_borde),
            ('LINEBELOW', (0, 0), (-1, 0), 0.35, gris_borde),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return card

    # Logo
    base_static = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img')
    logo_candidates = [os.path.join(base_static, 'logo.png'), os.path.join(base_static, 'logo-app-full-192.png')]
    logo_path = next((path for path in logo_candidates if os.path.exists(path)), None)
    if logo_path:
        logo = Image(logo_path, width=5.6 * cm, height=2.05 * cm)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 8))

    header_table = Table([[Paragraph("ESTADO DE CUENTA", subtitle_style)]], colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.8, color=azul, spaceAfter=10))

    # Datos Generales
    socio = libreta.socio
    solicitud_data = [
        ['Socio', socio.nombre_completo, 'Cedula', socio.cedula],
        ['Libreta N°', libreta.numero, 'Periodo', str(libreta.periodo.anio)],
        ['Estado Libreta', libreta.get_estado_display().upper(), 'Inscripcion', 'Pagada' if libreta.inscripcion_pagada else 'Pendiente'],
    ]
    story.append(Paragraph("DATOS DEL SOCIO", section_style))
    story.append(build_detail_table(solicitud_data))
    story.append(Spacer(1, 12))

    # Resumen Financiero
    ahorro_total = AporteMensual.objects.filter(libreta=libreta, estado='verificado').aggregate(t=Sum('monto_ahorro'))['t'] or 0
    creditos_activos = socio.creditos.filter(estado__in=['desembolsado', 'mora_leve', 'mora_media', 'mora_grave'])
    deuda_creditos = creditos_activos.aggregate(t=Sum('saldo_pendiente'))['t'] or 0
    multas_pendientes = socio.multas.filter(estado='pendiente').aggregate(t=Sum('monto'))['t'] or 0

    story.append(Paragraph("RESUMEN FINANCIERO", section_style))
    resumen_cards = Table([[
        build_metric_card('Ahorro Base Acumulado', f'${ahorro_total:.2f}'),
        build_metric_card('Deuda Creditos', f'${deuda_creditos:.2f}'),
        build_metric_card('Multas Pendientes', f'${multas_pendientes:.2f}'),
    ]], colWidths=[5.65 * cm, 5.65 * cm, 5.65 * cm])
    resumen_cards.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(resumen_cards)
    story.append(Spacer(1, 12))

    # Tabla de Aportes
    story.append(Paragraph("HISTORIAL DE APORTES", section_style))
    aportes_data = [['Mes', 'Ahorro', 'Loteria', 'Cumpleanos', 'Total', 'Estado']]
    
    aportes = AporteMensual.objects.filter(libreta=libreta).order_by('mes')
    total_ah = 0
    total_lo = 0
    total_cu = 0
    total_to = 0
    
    for a in aportes:
        aportes_data.append([
            a.get_mes_display(), f'${a.monto_ahorro:.2f}', f'${a.monto_loteria:.2f}', f'${a.monto_cumpleanos:.2f}', f'${a.monto_total:.2f}', a.get_estado_display()
        ])
        if a.estado == 'verificado':
            total_ah += a.monto_ahorro
            total_lo += a.monto_loteria
            total_cu += a.monto_cumpleanos
            total_to += a.monto_total

    aportes_data.append(['TOTAL VERIFICADO', f'${total_ah:.2f}', f'${total_lo:.2f}', f'${total_cu:.2f}', f'${total_to:.2f}', ''])

    tabla_aportes = Table(aportes_data, colWidths=[3 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm])
    tabla_aportes.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOX', (0, 0), (-1, -1), 0.7, gris_borde),
        ('INNERGRID', (0, 0), (-1, -1), 0.35, gris_borde),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, gris_fondo]),
        ('ALIGN', (1, 0), (4, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#EAF7F3')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    story.append(tabla_aportes)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#DDE3EF'), spaceAfter=10))
    story.append(Paragraph(f"Documento generado por el sistema cooperativo.", small_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


def portal_estado_cuenta_pdf(request, pk):
    socio_id = request.session.get('portal_socio_id')
    if not socio_id:
        return redirect('portal_login')
    
    libreta = get_object_or_404(Libreta, pk=pk, socio_id=socio_id)
    buffer = generar_pdf_estado_cuenta(libreta)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Estado_Cuenta_Libreta_{libreta.numero}.pdf"'
    return response
