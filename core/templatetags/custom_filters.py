from django import template

register = template.Library()

@register.filter
def money_fmt(value):
    """
    Formatea un número con separador de miles '.' y separador decimal ','.
    Ejemplo: 10150.5 -> 10.150,50
    """
    try:
        if value is None:
            return "0,00"
        val = float(value)
        # Convertir a string con comas en miles y punto decimal
        fmt = f"{val:,.2f}"
        # Intercambiar comas por puntos y viceversa
        fmt = fmt.replace(',', 'X').replace('.', ',').replace('X', '.')
        return fmt
    except (ValueError, TypeError):
        return value
