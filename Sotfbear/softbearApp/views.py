from django.shortcuts import render, redirect
from django.contrib import admin

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from . import views

# Importamos los formularios que creamos
from .forms import SignUpForm, LoginForm


# Create your views here.
def pagina_principal(request):
    return render(request, 'pagina_principal.html')

#Creamos la vista para el login
def login(request):
    signup_form = SignUpForm()
    login_form = LoginForm()
    active_tab = 'login'  # tab activo por defecto

    if request.method == 'POST':

        if 'signup_submit' in request.POST:
            signup_form = SignUpForm(request.POST)
            active_tab = 'signup'
            if signup_form.is_valid():
                user = signup_form.save()
                login(request, user)
                return redirect('softbearApp:pagina_principal')  # redirige a la página principal después de registrarse

        elif 'login_submit' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            active_tab = 'login'
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('softbearApp:pagina_principal')  # redirige a la página principal después de iniciar sesión

    return render(request, 'login.html', {
        'signup_form': signup_form,
        'login_form': login_form,
        'active_tab': active_tab,
    })
