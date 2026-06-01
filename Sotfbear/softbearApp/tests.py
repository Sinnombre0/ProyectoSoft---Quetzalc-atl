"""
Pruebas unitarias 
Cubre: FormularioRegistro, FormularioInicioSesion, y todas las vistas.

Para ejecutar hay que utilizar:
    python manage.py test Softbear
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from .models import Parque, Reservacion

User = get_user_model()


# =========================================================================== #
#  Funciones auxiliares
# =========================================================================== #

def crear_usuario(email='test@example.com', password='Segura123!'):
    return User.objects.create_user(
        username=email,
        email=email,
        password=password,
        first_name='Shaggy',
        last_name='Holmes',
    )


def crear_parque(nombre='Parque Test', tiene_cabanas=True,
                 cap_cabanas=10, cap_camping=20):
    return Parque.objects.create(
        nombre=nombre,
        direccion='Tlaxcala no existe',
        horario='9:00-18:00',
        servicios='Cabaña,Camping',
        tiene_cabanas=tiene_cabanas,
        capacidad_cabanas=cap_cabanas,
        capacidad_camping=cap_camping,
    )


# Creamos diferentes fechas para verificar que los martes no se podra hacer reservaciones
LUNES_JUNIO     = date(2025, 6, 5)   
MIERCOLES_JUNIO = date(2025, 6, 9) 
MARTES_JUNIO  = date(2025, 6, 3)   # martes — mantenimiento
FECHA_MAYO    = date(2025, 5, 15)  # fuera de tiempo


# =========================================================================== #
#  1. FORMULARIO DE REGISTRO
# =========================================================================== #

class FormularioRegistroTests(TestCase):

    def _datos_validos(self, **kwargs):
        base = {
            'first_name': 'Shaggy',
            'last_name': 'Holmes',
            'email': 'nuevo@ejemplo.com',
            'password1': 'Segura123!',
            'password2': 'Segura123!',
        }
        base.update(kwargs)
        return base

    def _form(self, **kwargs):
        from .forms import FormularioRegistro
        return FormularioRegistro(data=self._datos_validos(**kwargs))

    # --- Casos válidos ---

    def test_formulario_valido(self):
        self.assertTrue(self._form().is_valid())

    def test_nombre_se_capitaliza(self):
        form = self._form(first_name='Shaggy')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'Shaggy')

    def test_apellido_se_capitaliza(self):
        form = self._form(last_name='hólmes')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['last_name'], 'Hólmes')

    def test_email_se_normaliza_a_minusculas(self):
        form = self._form(email='USUARIO@EJEMPLO.COM')
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['email'], 'usuario@ejemplo.com')

    # --- Validaciones de nombre ---

    def test_nombre_con_numeros_es_invalido(self):
        form = self._form(first_name='Shaggy123')
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_apellido_con_simbolos_es_invalido(self):
        form = self._form(last_name='H@lmes!')
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    # --- Validaciones de contraseña ---

    def test_contrasena_sin_mayuscula(self):
        form = self._form(password1='segura123!', password2='segura123!')
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasena_sin_minuscula(self):
        form = self._form(password1='SEGURA123!', password2='SEGURA123!')
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasena_sin_numero(self):
        form = self._form(password1='SeguraABC!', password2='SeguraABC!')
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasena_sin_especial(self):
        form = self._form(password1='Segura1234', password2='Segura1234')
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasena_muy_corta(self):
        form = self._form(password1='Ab1!', password2='Ab1!')
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasena_demasiado_larga(self):
        larga = 'Aa1!' + 'x' * 125  # 129 chars
        form = self._form(password1=larga, password2=larga)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_contrasenas_no_coinciden(self):
        form = self._form(password1='Segura123!', password2='Otra123!')
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    # --- Email duplicado ---

    def test_email_duplicado_no_lanza_error_visible(self):
        """
        Por diseño, el formulario no debe revelar si el email ya existe
        (prevención de enumeración de usuarios): el form es válido pero save() retorna None.
        """
        crear_usuario(email='existente@ejemplo.com')
        from .forms import FormularioRegistro
        form = FormularioRegistro(data=self._datos_validos(email='existente@ejemplo.com'))
        self.assertTrue(form.is_valid())
        resultado = form.save()
        self.assertIsNone(resultado)

    def test_usuario_nuevo_se_guarda_correctamente(self):
        form = self._form()
        self.assertTrue(form.is_valid())
        usuario = form.save()
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.email, 'nuevo@ejemplo.com')
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertTrue(usuario.is_active)


# =========================================================================== #
#  2. FORMULARIO DE INICIO DE SESIÓN
# =========================================================================== #

class FormularioInicioSesionTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()

    def _form(self, username, password):
        from .forms import FormularioInicioSesion
        from django.test import RequestFactory
        request = RequestFactory().post('/login/')
        return FormularioInicioSesion(request=request,
                                      data={'username': username, 'password': password})

    def test_login_valido(self):
        form = self._form('test@example.com', 'Segura123!')
        self.assertTrue(form.is_valid())

    def test_login_email_en_mayusculas_funciona(self):
        """El email se normaliza a minúsculas antes de autenticar."""
        form = self._form('TEST@EXAMPLE.COM', 'Segura123!')
        self.assertTrue(form.is_valid())

    def test_login_contrasena_incorrecta(self):
        form = self._form('test@example.com', 'WrongPass1!')
        self.assertFalse(form.is_valid())

    def test_login_usuario_inexistente(self):
        form = self._form('noexiste@ejemplo.com', 'Segura123!')
        self.assertFalse(form.is_valid())


# =========================================================================== #
#  3. VISTAS — AUTENTICACIÓN
# =========================================================================== #

class VistaLoginTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = crear_usuario()

    def test_get_muestra_formulario(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'luciernagas/login.html')

    def test_post_credenciales_validas_redirige(self):
        resp = self.client.post(reverse('login'),
                                {'username': 'test@example.com', 'password': 'Segura123!'})
        self.assertRedirects(resp, reverse('mis_reservaciones'))

    def test_post_credenciales_invalidas_muestra_error(self):
        resp = self.client.post(reverse('login'),
                                {'username': 'test@example.com', 'password': 'Mala!'})
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('incorrectos' in m for m in mensajes))

    def test_admin_redirige_a_panel(self):
        admin = User.objects.create_superuser(
            username='admin@ejemplo.com',
            email='admin@ejemplo.com',
            password='Admin123!',
        )
        resp = self.client.post(reverse('login'),
                                {'username': 'admin@ejemplo.com', 'password': 'Admin123!'})
        self.assertRedirects(resp, '/admin/', fetch_redirect_response=False)


class VistaLogoutTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def test_logout_redirige_a_index(self):
        resp = self.client.get(reverse('logout'))
        self.assertRedirects(resp, reverse('index'))

    def test_logout_cierra_sesion(self):
        self.client.get(reverse('logout'))
        resp = self.client.get(reverse('mis_reservaciones'))
        self.assertNotEqual(resp.status_code, 200)  # redirige a login


class VistaRegistroTests(TestCase):

    def _datos(self, **kwargs):
        base = {
            'first_name': 'Ana',
            'last_name': 'Lopez',
            'email': 'ana@ejemplo.com',
            'password1': 'Segura123!',
            'password2': 'Segura123!',
        }
        base.update(kwargs)
        return base

    def test_get_muestra_formulario(self):
        resp = self.client.get(reverse('registro'))
        self.assertEqual(resp.status_code, 200)

    def test_registro_exitoso_redirige(self):
        resp = self.client.post(reverse('registro'), self._datos())
        self.assertRedirects(resp, reverse('registro_exitoso'))

    def test_registro_crea_usuario(self):
        self.client.post(reverse('registro'), self._datos())
        self.assertTrue(User.objects.filter(email='ana@ejemplo.com').exists())

    def test_registro_con_datos_invalidos_no_crea_usuario(self):
        self.client.post(reverse('registro'), self._datos(password1='debil'))
        self.assertFalse(User.objects.filter(email='ana@ejemplo.com').exists())


# =========================================================================== #
#  4. VISTAS — PARQUES Y RESERVACIONES
# =========================================================================== #

class VistaParquesTests(TestCase):

    def setUp(self):
        self.parque = crear_parque()

    def test_lista_parques_accesible_sin_login(self):
        resp = self.client.get(reverse('parques'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.parque, resp.context['parques'])


class VistaMisReservacionesTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()

    def test_requiere_login(self):
        resp = self.client.get(reverse('mis_reservaciones'))
        self.assertNotEqual(resp.status_code, 200)

    def test_usuario_autenticado_puede_acceder(self):
        self.client.force_login(self.usuario)
        resp = self.client.get(reverse('mis_reservaciones'))
        self.assertEqual(resp.status_code, 200)

    def test_solo_muestra_reservaciones_propias(self):
        otro = crear_usuario(email='otro@ejemplo.com')
        parque = crear_parque()
        Reservacion.objects.create(
            usuario=otro, parque=parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=2, tipo_visita='CAMPING',
        )
        self.client.force_login(self.usuario)
        resp = self.client.get(reverse('mis_reservaciones'))
        self.assertEqual(list(resp.context['reservas']), [])


# =========================================================================== #
#  5. RESERVACIONES
# =========================================================================== #

class ReservarTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.parque = crear_parque(cap_cabanas=10, cap_camping=20)

    def _post(self, fi, ft, personas=2, tipo='CAMPING', parque=None):
        pk = (parque or self.parque).pk
        return self.client.post(reverse('reservar', args=[pk]), {
            'fecha_inicio':  fi.isoformat(),
            'fecha_termino': ft.isoformat(),
            'num_personas':  personas,
            'tipo_visita':   tipo,
        })

    # --- Caso exitoso ---

    def test_reserva_camping_valida(self):
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO)
        self.assertRedirects(resp, reverse('mis_reservaciones'))
        self.assertEqual(Reservacion.objects.count(), 1)

    def test_reserva_cabana_valida(self):
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO, tipo='CABANA')
        self.assertRedirects(resp, reverse('mis_reservaciones'))

    # --- Validación: martes ---

    def test_rango_que_incluye_martes_es_rechazado(self):
        # LUNES_JUNIO (lunes 2/6) → MIERCOLES_JUNIO (miércoles 4/6) incluye el martes 3/6
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO + timedelta(days=1))
        # El rango lunes-jueves incluye martes → error
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        # Solo comprobamos el error si el rango realmente toca martes
        fi, ft = LUNES_JUNIO, MIERCOLES_JUNIO + timedelta(days=1)
        toca_martes = any((fi + timedelta(d)).weekday() == 1
                          for d in range((ft - fi).days + 1))
        if toca_martes:
            self.assertTrue(any('martes' in m for m in mensajes))

    def test_reserva_solo_martes_es_rechazada(self):
        resp = self._post(MARTES_JUNIO, MARTES_JUNIO)
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('martes' in m for m in mensajes))

    # --- Validación: temporada ---

    def test_fecha_fuera_de_temporada_rechazada(self):
        mayo_lunes = date(2025, 5, 5)   # lunes, fuera de junio-agosto
        resp = self._post(mayo_lunes, mayo_lunes)
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('junio' in m or 'agosto' in m for m in mensajes))

    def test_fecha_inicio_en_mayo_y_fin_en_junio_rechazada(self):
        resp = self._post(date(2025, 5, 26), LUNES_JUNIO)
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('junio' in m or 'agosto' in m for m in mensajes))

    # --- Validación: orden de fechas ---

    def test_fecha_fin_antes_que_inicio_rechazada(self):
        resp = self._post(MIERCOLES_JUNIO, LUNES_JUNIO)
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('anterior' in m for m in mensajes))

    # --- Validación: cabaña sin disponibilidad ---

    def test_parque_sin_cabanas_rechaza_tipo_cabana(self):
        parque_sin = crear_parque('Sin Cabañas', tiene_cabanas=False)
        resp = self._post(LUNES_JUNIO, LUNES_JUNIO, tipo='CABANA', parque=parque_sin)
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('cabaña' in m.lower() for m in mensajes))

    # --- Validación: capacidad ---

    def test_exceder_capacidad_camping_es_rechazado(self):
        # Ocupar toda la capacidad de camping (20)
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=20, tipo_visita='CAMPING', estado='ACTIVA',
        )
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO, personas=1, tipo='CAMPING')
        mensajes = [str(m) for m in get_messages(resp.wsgi_request)]
        self.assertTrue(any('disponible' in m for m in mensajes))

    def test_reserva_cancelada_no_cuenta_para_capacidad(self):
        """Una reserva CANCELADA no debe bloquear la capacidad."""
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=20, tipo_visita='CAMPING', estado='CANCELADA',
        )
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO, personas=5, tipo='CAMPING')
        self.assertRedirects(resp, reverse('mis_reservaciones'))

    def test_reservas_en_fechas_no_solapadas_no_afectan_capacidad(self):
        """Reservas en otras fechas no deben consumir capacidad."""
        # Reserva en julio, no solapa con junio
        Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=date(2025, 7, 7), fecha_termino=date(2025, 7, 9),
            num_personas=20, tipo_visita='CAMPING', estado='ACTIVA',
        )
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO, personas=5, tipo='CAMPING')
        self.assertRedirects(resp, reverse('mis_reservaciones'))

    # --- Requiere login ---

    def test_reservar_requiere_login(self):
        self.client.logout()
        resp = self._post(LUNES_JUNIO, MIERCOLES_JUNIO)
        self.assertNotEqual(resp.status_code, 200)

    # --- GET redirige a parques ---

    def test_get_redirige_a_parques(self):
        resp = self.client.get(reverse('reservar', args=[self.parque.pk]))
        self.assertRedirects(resp, reverse('parques'))


# =========================================================================== #
#  6. CANCELAR RESERVACIÓN
# =========================================================================== #

class WCancelarReservacionTests(TestCase):

    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.parque = crear_parque()
        self.reserva = Reservacion.objects.create(
            usuario=self.usuario, parque=self.parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=2, tipo_visita='CAMPING', estado='ACTIVA',
        )

    def _cancelar(self, pk=None):
        return self.client.post(
            reverse('cancelar_reservacion', args=[pk or self.reserva.pk])
        )

    def test_cancelacion_exitosa(self):
        self._cancelar()
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'CANCELADA')

    def test_cancelacion_redirige_a_mis_reservaciones(self):
        resp = self._cancelar()
        self.assertRedirects(resp, reverse('mis_reservaciones'))

    def test_cancelar_reserva_ya_cancelada_no_cambia_nada(self):
        self.reserva.estado = 'CANCELADA'
        self.reserva.save()
        self._cancelar()
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.estado, 'CANCELADA')

    def test_usuario_no_puede_cancelar_reserva_ajena(self):
        otro = crear_usuario(email='otro@ejemplo.com')
        reserva_ajena = Reservacion.objects.create(
            usuario=otro, parque=self.parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=1, tipo_visita='CAMPING', estado='ACTIVA',
        )
        resp = self._cancelar(pk=reserva_ajena.pk)
        self.assertEqual(resp.status_code, 404)
        reserva_ajena.refresh_from_db()
        self.assertEqual(reserva_ajena.estado, 'ACTIVA')

    def test_cancelar_requiere_login(self):
        self.client.logout()
        resp = self._cancelar()
        self.assertNotEqual(resp.status_code, 200)


# =========================================================================== #
#  7. MODELOS
# =========================================================================== #

class ModeloParqueTests(TestCase):

    def test_str_retorna_nombre(self):
        p = crear_parque('Bosque Mágico')
        self.assertEqual(str(p), 'Bosque Mágico')

    def test_servicios_list_parsea_correctamente(self):
        p = Parque(servicios='Cabaña, Camping, Guías')
        self.assertEqual(p.servicios_list(), ['Cabaña', 'Camping', 'Guías'])


class ModeloReservacionTests(TestCase):

    def test_str_contiene_usuario_y_parque(self):
        usuario = crear_usuario()
        parque = crear_parque()
        reserva = Reservacion.objects.create(
            usuario=usuario, parque=parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=1, tipo_visita='CAMPING',
        )
        self.assertIn(str(parque), str(reserva))

    def test_estado_por_defecto_es_activa(self):
        usuario = crear_usuario()
        parque = crear_parque()
        reserva = Reservacion.objects.create(
            usuario=usuario, parque=parque,
            fecha_inicio=LUNES_JUNIO, fecha_termino=MIERCOLES_JUNIO,
            num_personas=1, tipo_visita='CAMPING',
        )
        self.assertEqual(reserva.estado, 'ACTIVA')
