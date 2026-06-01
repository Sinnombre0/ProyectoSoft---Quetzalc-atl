from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import admin

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Parque, Reservacion
from . import services

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

        # 1. Validar orden de fechas primero
        # 2. Validar junio-agosto (solo mes, independiente del año)
        # 3. Validar que ningún día del rango sea martes
        error = services.validar_fechas(fi, ft)
        if error:
            messages.error(request, error)
            return redirect('parques')
        
        # 4. Validar que el parque tenga cabañas si se pide cabaña
        # 5. Calcular disponibilidad por fechas (traslape)
        error = services.validar_disponibilidad(parque, fi, ft, tipo_visita, num_personas)
        if error:
            messages.error(request, error)
            return redirect('parques')

        # Crear reservación
        services.crear_reservacion(request.user, parque, fi, ft, num_personas, tipo_visita)

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