from django import template
from django.conf import settings
import os
import json
from decimal import Decimal

register = template.Library()

class DjangoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


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
    bucket = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
    region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
    if bucket:
        return f'https://{bucket}.s3.{region}.amazonaws.com/media/{name}'
    return '/media/' + name


@register.filter
def to_json(value):
    if value is None:
        return '[]'
    return json.dumps(value, cls=DjangoEncoder)
