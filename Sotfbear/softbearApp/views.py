from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import admin

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Parque, Reservacion

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