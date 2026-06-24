import re
from django.core.exceptions import ValidationError
from django.utils.html import escape


def validar_solo_letras(value):
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', value):
        raise ValidationError(
            'Este campo solo acepta letras y espacios. No se permiten números ni caracteres especiales.'
        )


def validar_precio_positivo(value):
    if value <= 0:
        raise ValidationError('El precio debe ser mayor a cero.')
    if value > 999999:
        raise ValidationError('El precio no puede exceder 999,999.')


def validar_sin_html(value):
    patron_html = re.compile(r'<[^>]+>')
    if patron_html.search(value):
        raise ValidationError('No se permite contenido HTML en este campo.')


def validar_email_corporativo(value):
    dominios_bloqueados = ['tempmail.com', 'guerrillamail.com', 'throwam.com', '10minutemail.com']
    dominio = value.split('@')[-1].lower()
    if dominio in dominios_bloqueados:
        raise ValidationError(f'No se permiten correos de {dominio}. Usa un email válido.')


def sanitize_input(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    value = ' '.join(value.split())
    return escape(value)


def validar_no_sql_injection(value):
    patrones_peligrosos = [
        r'(\bSELECT\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b|\bDROP\b|\bUNION\b)',
        r'(--|;|\/\*|\*\/)',
        r'(\bOR\b\s+\d+=\d+|\bAND\b\s+\d+=\d+)',
    ]
    for patron in patrones_peligrosos:
        if re.search(patron, value, re.IGNORECASE):
            raise ValidationError('Se detectó contenido no permitido en este campo.')
