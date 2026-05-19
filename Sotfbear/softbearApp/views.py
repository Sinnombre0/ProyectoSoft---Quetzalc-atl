from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import admin

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Parque, Reservacion

from . import views

# Importamos los formularios que creamos
from .forms import SignUpForm, LoginForm


# Create your views here.
def index(request):
    return render(request, 'luciernagas/index.html')

def login_view(request):
    if request.method == 'POST':
        email    = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('mis_reservaciones')
        messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'luciernagas/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def registro(request):
    if request.method == 'POST':
        nombre   = request.POST['nombre']
        apellidos = request.POST['apellidos']
        email    = request.POST['email']
        password = request.POST['password']

        # Verificar que el correo no esté ya registrado
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese correo.')
            return render(request, 'luciernagas/registro.html')

        # Crear el usuario
        user = User.objects.create_user(
            username=email,       # usamos el email como username
            email=email,
            password=password,
            first_name=nombre,
            last_name=apellidos,
        )

        # Iniciar sesión automáticamente
        login(request, user)
        return redirect('index')

    return render(request, 'luciernagas/registro.html')

def parques(request):
    parques_qs = Parque.objects.all()
    return render(request, 'luciernagas/parques.html', {'parques': parques_qs})

@login_required
def mis_reservaciones(request):
    reservas = Reservacion.objects.filter(usuario=request.user).select_related('parque')
    return render(request, 'luciernagas/mis_reservaciones.html', {'reservas': reservas})