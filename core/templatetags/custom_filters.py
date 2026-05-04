from django import template
from django.conf import settings
import os

register = template.Library()

@register.filter
def money_fmt(value):
    try:
        if value is None:
            return "0,00"
        val = float(value)
        fmt = f"{val:,.2f}"
        fmt = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        return fmt
    except (ValueError, TypeError):
        return value


@register.filter
def comprobante_url(field):
    if not field:
        return ''
    name = getattr(field, 'name', str(field))
    result = '/media/' + name
    return result
