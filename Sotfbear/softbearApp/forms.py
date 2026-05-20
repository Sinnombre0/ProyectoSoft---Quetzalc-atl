from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

# ------------------------------------------------------------------ #
#  Para los nombres de las clases deje el nombre en español para que sea mas descriptivo
# y mucho mas facil de checar
# ------------------------------------------------------------------ #
class FormularioRegistro(forms.ModelForm):
    first_name = forms.CharField(
        label="Nombre",
        max_length=50,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=50,
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'autocomplete': 'off'}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    # ------------------------------------------------------------------ #
    #  Verificaciones por cada dato que ingrese el usuario 
    # ------------------------------------------------------------------ #

# Vemos que el nombre y apellido solo tengan letras
    def clean_first_name(self):
        nombre = self.cleaned_data.get('first_name', '').strip()
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError("El nombre solo puede contener letras.")
        return nombre.title()          # "juan" → "Juan"

    def clean_last_name(self):
        apellido = self.cleaned_data.get('last_name', '').strip()
        if not apellido.replace(' ', '').isalpha():
            raise forms.ValidationError("El apellido solo puede contener letras.")
        return apellido.title()

# Verficamos que el correo no esté registrado y lo ponemos en minúscula
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con este correo.")
        return email

# Verificamos que la contraseña sea segura
    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        errores = []

        if len(password) < 8:
            errores.append("debe tener al menos 8 caracteres")
        if not re.search(r'[A-Z]', password):
            errores.append("una letra mayúscula")
        if not re.search(r'[a-z]', password):
            errores.append("una letra minúscula")
        if not re.search(r'\d', password):
            errores.append("un número")
        if not re.search(r'[^A-Za-z0-9]', password):
            errores.append("un carácter especial (!@#$...)")

        if errores:
            raise forms.ValidationError(
                f"La contraseña debe tener: {', '.join(errores)}."
            )
        return password

    # ------------------------------------------------------------------ #
    #  Verificamos que las contraseñas coincidan
    # ------------------------------------------------------------------ #

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    # ------------------------------------------------------------------ #
    #  Guardamos los datos del usuario
    # ------------------------------------------------------------------ #

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class FormularioInicioSesion(AuthenticationForm):
    username = forms.CharField(
        label="Correo electrónico",
        widget=forms.TextInput(attrs={'autocomplete': 'off'}),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
    )

    def clean_username(self):
        # Normaliza el correo antes de autenticar
        return self.cleaned_data.get('username', '').lower().strip()