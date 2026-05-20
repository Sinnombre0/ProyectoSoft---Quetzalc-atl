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


# Create your views here.
def index(request):
    return render(request, 'luciernagas/index.html')

def vista_iniciar_sesion(request):
    form = FormularioInicioSesion(data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('mis_reservaciones')
        messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'luciernagas/login.html', {'form': form})


def vista_cerrar_sesion(request):
    logout(request)
    return redirect('index')


def vista_registro(request):
    form = FormularioRegistro(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        # Los errores del form (email duplicado, contraseñas distintas, etc.)
        # se renderizan automáticamente en el template con {{ form.errors }}

    return render(request, 'luciernagas/registro.html', {'form': form})

def parques(request):
    parques_qs = Parque.objects.all()
    return render(request, 'luciernagas/parques.html', {'parques': parques_qs})

@login_required
def mis_reservaciones(request):
    reservas = Reservacion.objects.filter(usuario=request.user).select_related('parque')
    return render(request, 'luciernagas/mis_reservaciones.html', {'reservas': reservas})