# Softbear 🌿

Desarrollaremos un sistema para el Festival de las Luciérnagas como parte
de nuestro proyecto final de Ingeniería de Software con ayuda del framework
Django.

---

## Instalación

1. Clonar el repositorio

2. Crear el entorno virtual con los requerimientos del archivo `environment.yml`:

```bash
conda env create -f environment.yml
```

3. Activar el entorno:

```bash
conda activate Softbear
```

4. Aplicar las migraciones para crear la base de datos:

```bash
python manage.py migrate
```

5. Cargar datos iniciales:

```bash
python manage.py loaddata parques.json
```

6. Crear un superusuario para acceder al panel de administración:

```bash
python manage.py createsuperuser
```

7. Correr el servidor:

```bash
python manage.py runserver
```

Entrar a http://127.0.0.1:8000

---

## Páginas disponibles

| URL | Descripción |
|-----|-------------|
| `/` | Inicio |
| `/parques/` | Mapa de parques oficiales |
| `/login/` | Iniciar sesión |
| `/registro/` | Crear cuenta |
| `/mis-reservaciones/` | Reservas del usuario (requiere login) |
| `/admin/` | Panel de administración |

---

## Forma de trabajo

- Trabajamos en ramas separadas para mantener una correcta organización
- Se hacen ramas distintas para back y front
- Se realiza un pull request antes de integrar cambios a las ramas principales

---

## Integrantes

| Nombre | Rol |
|--------|-----|
| Lechuga Hervert Maximiliano | Scrum Master |
| Díaz Reyes Lilith Jaquelin | Product Owner |
| Hernández Islas Leonardo Daniel | Developer |
| Camacho Gutiérrez Karla Alejandra | Developer |
| Vargas Herrera Eduardo | Developer |
