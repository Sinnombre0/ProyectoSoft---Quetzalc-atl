from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import admin

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Parque, Reservacion

from datetime import date, datetime, timedelta

from . import views

# Importamos los formularios que creamos
from .forms import FormularioRegistro, FormularioInicioSesion

def es_admin(user):
    return user.is_superuser or user.is_staff

def index(request):
    return render(request, 'luciernagas/index.html')

def vista_iniciar_sesion(request):
    form = FormularioInicioSesion(request, data=request.POST or None)

    if request.method == 'POST':
        print("POST data:", request.POST)
        print("Form válido:", form.is_valid())
        print("Errores:", form.errors)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if es_admin(user):
                request.session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
                return redirect('/admin/')
            else:
                return redirect('mis_reservaciones')

        else:
            if not form.errors.as_data().keys() - {'__all__'}:
                messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'luciernagas/login.html', {'form': form})


def vista_cerrar_sesion(request):
    logout(request)
    return redirect('index')


def vista_registro(request):
    form = FormularioRegistro(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # No se loggea directamente al usuario en caso de que el correo haya sido duplicado,
            # de esta forma un atacante no puede distinguir entre ambos casos
            form.save()
            return redirect('registro_exitoso')
    # Los errores del form (email duplicado, contraseñas distintas, etc.)
        # se renderizan automáticamente en el template con {{ form.errors }}

    return render(request, 'luciernagas/registro.html', {'form': form})

def vista_registro_exitoso(request):
    return render(request, 'luciernagas/registro_exitoso.html')

def parques(request):
    parques_qs = Parque.objects.all()
    return render(request, 'luciernagas/parques.html', {'parques': parques_qs})

@login_required
def mis_reservaciones(request):
    reservas = Reservacion.objects.filter(usuario=request.user).select_related('parque')
    return render(request, 'luciernagas/mis_reservaciones.html', {'reservas': reservas})

@login_required
def reservar(request, parque_id):
    parque = get_object_or_404(Parque, pk=parque_id)

    if request.method == 'POST':
        fecha_inicio  = request.POST.get('fecha_inicio')
        fecha_termino = request.POST.get('fecha_termino')
        num_personas  = int(request.POST.get('num_personas'))
        tipo_visita   = request.POST.get('tipo_visita')

        fi = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        ft = datetime.strptime(fecha_termino, '%Y-%m-%d').date()

        # Validar que ningún día del rango sea martes
        fecha_actual = fi
        while fecha_actual <= ft:
            if fecha_actual.weekday() == 1:
                messages.error(request, 'Tu estancia incluye un martes, día de mantenimiento. Por favor elige otras fechas.')
                return redirect('parques')
            fecha_actual += timedelta(days=1)

        # Validar junio-agosto
        if not (6 <= fi.month <= 8) or not (6 <= ft.month <= 8):
            messages.error(request, 'Solo se puede reservar entre junio y agosto.')
            return redirect('parques')

        # Validar fechas
        if fi > ft:
            messages.error(request, 'La fecha de salida no puede ser anterior a la de entrada.')
            return redirect('parques')

        # Validar que el parque tenga cabañas si se pide cabaña
        if tipo_visita == 'CABANA' and not parque.tiene_cabanas:
            messages.error(request, 'Este parque no tiene cabañas.')
            return redirect('parques')

        # Calcular disponibilidad por fechas (traslape)
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
            messages.error(request, f'Solo hay {disponible} lugares disponibles para esas fechas.')
            return redirect('parques')

        # Crear reservación
        Reservacion.objects.create(
            usuario      = request.user,
            parque       = parque,
            fecha_inicio = fi,
            fecha_termino= ft,
            num_personas = num_personas,
            tipo_visita  = tipo_visita,
            estado       = 'ACTIVA',
        )

        messages.success(request, f'¡Reserva en {parque.nombre} confirmada! 🌟')
        return redirect('mis_reservaciones')

    return redirect('parques')

@login_required
def cancelar_reservacion(request, pk):
    reserva = get_object_or_404(Reservacion, pk=pk, usuario=request.user)

    if request.method == 'POST' and reserva.estado == 'ACTIVA':
        reserva.estado = 'CANCELADA'
        reserva.save()

        messages.success(request, 'Reservación cancelada correctamente.')

    return redirect('mis_reservaciones')