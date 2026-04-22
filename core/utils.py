from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .models import AuditoriaSistema


def has_role(user, *roles):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    perfil = getattr(user, 'perfil', None)
    return bool(perfil and perfil.rol in roles)


def require_roles(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if has_role(request.user, *roles):
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            return redirect('dashboard')
        return wrapped
    return decorator


def registrar_auditoria(usuario, area, accion, descripcion, entidad='', objeto_id='', datos=None):
    AuditoriaSistema.objects.create(
        usuario=usuario if getattr(usuario, 'is_authenticated', False) else None,
        area=area,
        accion=accion,
        entidad=entidad,
        objeto_id=str(objeto_id or ''),
        descripcion=descripcion[:300],
        datos=datos or {},
    )
