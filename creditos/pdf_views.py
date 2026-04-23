from io import BytesIO
import os

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import Credito


def generar_pdf_credito(credito):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    azul = colors.HexColor('#17479E')
    azul_oscuro = colors.HexColor('#10336F')
    verde = colors.HexColor('#0E8A6A')
    verde_suave = colors.HexColor('#EAF7F3')
    gris = colors.HexColor('#64748B')
    gris_borde = colors.HexColor('#D9E2F2')
    gris_fondo = colors.HexColor('#F6F9FF')
    rosa = colors.HexColor('#E83E74')

    title_style = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=10, leading=9, textColor=azul_oscuro, alignment=TA_CENTER, spaceAfter=6)
    brand_style = ParagraphStyle('bigname', fontName='Helvetica-Bold', fontSize=24, leading=26, textColor=rosa, alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('subtitle', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=verde, alignment=TA_CENTER, spaceBefore=2, spaceAfter=14)
    section_style = ParagraphStyle('section', fontName='Helvetica-Bold', fontSize=11, textColor=azul_oscuro, spaceBefore=12, spaceAfter=6)
    small_style = ParagraphStyle('small', fontName='Helvetica', fontSize=8, textColor=gris, alignment=TA_CENTER)
    body_style = ParagraphStyle('body', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.black, alignment=TA_LEFT)
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
            colWidths=[5.45 * cm],
            rowHeights=[0.7 * cm, 1.0 * cm],
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

    base_static = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img')
    logo_candidates = [
        os.path.join(base_static, 'logo.png'),
        os.path.join(base_static, 'logo-app-full-192.png'),
    ]
    logo_path = next((path for path in logo_candidates if os.path.exists(path)), None)
    if logo_path:
        logo = Image(logo_path, width=4.8 * cm, height=1.55 * cm)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 12))

    header_table = Table([[
        Paragraph("COOPERATIVA DE AHORRO Y CREDITO", title_style),
    ], [
        Paragraph("BAILARINES", brand_style),
    ], [
        Paragraph("SOLICITUD DE CREDITO", subtitle_style),
    ]], colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.8, color=azul, spaceAfter=10))

    solicitud_data = [
        ['Codigo Solicitud', credito.numero, 'Fecha Solicitud', credito.fecha_solicitud.strftime('%d/%m/%Y %H:%M')],
        ['Tipo', credito.get_tipo_display(), 'Plazo', f'{credito.plazo_meses} mes(es)'],
        ['Fecha Desembolso', credito.fecha_desembolso.strftime('%d/%m/%Y') if credito.fecha_desembolso else 'Pendiente', 'Vencimiento', credito.fecha_pago_limite.strftime('%d/%m/%Y') if credito.fecha_pago_limite else 'N/D'],
    ]
    story.append(Paragraph("DATOS DE LA SOLICITUD", section_style))
    story.append(build_detail_table(solicitud_data))
    story.append(Spacer(1, 8))

    persona_data = [
        ['Socio', credito.socio.nombre_completo, 'Cedula', credito.socio.cedula],
        ['Banco', credito.get_banco_display(), 'Cuenta', credito.numero_cuenta_bancaria],
        ['Titular Cuenta', credito.titular_cuenta, 'Cedula Titular', credito.cedula_titular],
    ]
    story.append(Paragraph("DATOS DEL SOCIO Y DEPOSITO", section_style))
    story.append(build_detail_table(persona_data))
    story.append(Spacer(1, 12))

    story.append(Paragraph("RESUMEN FINANCIERO", section_style))
    fin_data = [
        ['Concepto', 'Valor'],
        ['Monto Solicitado', f'${credito.monto_solicitado:.2f}'],
        ['Interes Total', f'${credito.interes_total:.2f}'],
        ['Valor Transferencia', f'${credito.comision_bancaria:.2f}'],
        ['Monto Transferido al Socio', f'${credito.monto_transferir:.2f}'],
    ]
    if credito.tipo != 'mensualizado':
        fin_data.append(['Pago Unico al Vencimiento', f'${credito.monto_pago_final:.2f}'])

    resumen_cards = Table([[
        build_metric_card('Monto Solicitado', f'${credito.monto_solicitado:.2f}'),
        build_metric_card('Interes Total', f'${credito.interes_total:.2f}'),
        build_metric_card('Valor Transferencia', f'${credito.comision_bancaria:.2f}'),
    ]], colWidths=[5.65 * cm, 5.65 * cm, 5.65 * cm])
    resumen_cards.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(resumen_cards)
    story.append(Spacer(1, 8))

    fin_table = Table(fin_data, colWidths=[12.5 * cm, 4.5 * cm])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.7, gris_borde),
        ('INNERGRID', (0, 0), (-1, -1), 0.35, gris_borde),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, verde_suave]),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(fin_table)

    if credito.tipo == 'mensualizado' and credito.fecha_desembolso:
        story.append(Spacer(1, 12))
        story.append(Paragraph("TABLA DE AMORTIZACION PLANA", section_style))
        tabla_data = [['#', 'Fecha', 'Saldo Inicial', 'Capital', 'Interes', 'Cuota', 'Saldo Final']]
        tabla_amortizacion = credito.generar_tabla_amortizacion_plana()
        total_capital = 0
        total_interes = 0
        total_cuota = 0
        for cuota in tabla_amortizacion:
            total_capital += cuota['capital']
            total_interes += cuota['interes']
            total_cuota += cuota['cuota']
            tabla_data.append([
                str(cuota['numero']),
                cuota['fecha'].strftime('%d/%m/%Y'),
                f'${cuota["saldo_inicial"]:.2f}',
                f'${cuota["capital"]:.2f}',
                f'${cuota["interes"]:.2f}',
                f'${cuota["cuota"]:.2f}',
                f'${cuota["saldo_final"]:.2f}',
            ])
        tabla_data.append([
            'TOTAL',
            '',
            '',
            f'${total_capital:.2f}',
            f'${total_interes:.2f}',
            f'${total_cuota:.2f}',
            f'${tabla_amortizacion[-1]["saldo_final"]:.2f}' if tabla_amortizacion else '$0.00',
        ])
        tabla = Table(tabla_data, colWidths=[1.2 * cm, 2.5 * cm, 2.7 * cm, 2.5 * cm, 2.4 * cm, 2.5 * cm, 2.7 * cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), azul_oscuro),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.7, gris_borde),
            ('INNERGRID', (0, 0), (-1, -1), 0.35, gris_borde),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, gris_fondo]),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, -1), (-1, -1), verde_suave),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        story.append(tabla)

    if credito.observaciones:
        story.append(Spacer(1, 10))
        story.append(Paragraph("OBSERVACIONES", section_style))
        story.append(Paragraph(credito.observaciones, body_style))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#DDE3EF'), spaceAfter=10))
    story.append(Paragraph(f"Documento generado por el sistema. Credito {credito.numero}.", small_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


@login_required
def credito_pdf_admin(request, pk):
    credito = get_object_or_404(Credito, pk=pk)
    buffer = generar_pdf_credito(credito)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{credito.numero}.pdf"'
    return response


def credito_pdf_portal(request, pk):
    socio_id = request.session.get('portal_socio_id')
    if not socio_id:
        from django.shortcuts import redirect
        return redirect('portal_login')
    credito = get_object_or_404(Credito, pk=pk, socio_id=socio_id)
    buffer = generar_pdf_credito(credito)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{credito.numero}.pdf"'
    return response
