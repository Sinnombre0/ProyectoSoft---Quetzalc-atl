# Logica del negocio de la aplicacion, como funciones para manejar datos, etc.
from datetime import datetime, timedelta
from django.db.models import Sum
from .models import Parque, Reservacion


def validar_fechas(fi, ft):
    """Valida orden, rango junio-agosto y que no haya martes."""
    if fi > ft:
        return 'La fecha de salida no puede ser anterior a la de entrada.'

    if not (6 <= fi.month <= 8) or not (6 <= ft.month <= 8):
        return 'Solo se puede reservar entre junio y agosto.'

    fecha_actual = fi
    while fecha_actual <= ft:
        if fecha_actual.weekday() == 1:
            return 'Tu estancia incluye un martes, día de mantenimiento. Por favor elige otras fechas.'
        fecha_actual += timedelta(days=1)

    return None  # None = sin errores


def validar_disponibilidad(parque, fi, ft, tipo_visita, num_personas):
    """Valida cabañas y disponibilidad por fechas."""
    if tipo_visita == 'CABANA' and not parque.tiene_cabanas:
        return 'Este parque no tiene cabañas.'

    reservas_solapadas = Reservacion.objects.filter(
        parque             = parque,
        estado             = 'ACTIVA',
        tipo_visita        = tipo_visita,
        fecha_inicio__lte  = ft,
        fecha_termino__gte = fi,
    )
    personas_ocupadas = reservas_solapadas.aggregate(
        total=Sum('num_personas')
    )['total'] or 0

    capacidad_total = parque.capacidad_cabanas if tipo_visita == 'CABANA' else parque.capacidad_camping

    if personas_ocupadas + num_personas > capacidad_total:
        disponible = capacidad_total - personas_ocupadas
        return f'Solo hay {disponible} lugares disponibles para esas fechas.'

    return None  # None = sin errores


def crear_reservacion(usuario, parque, fi, ft, num_personas, tipo_visita):
    """Crea y guarda la reservación."""
    return Reservacion.objects.create(
        usuario      = usuario,
        parque       = parque,
        fecha_inicio = fi,
        fecha_termino= ft,
        num_personas = num_personas,
        tipo_visita  = tipo_visita,
        estado       = 'ACTIVA',
    )