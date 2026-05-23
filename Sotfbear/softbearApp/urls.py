from django.contrib import admin
from django.urls import path


from . import views

#app_name = 'softbearApp'

#urlpatterns = [
    # Nada de momento
    #path('', views.pagina_principal, name='pagina_principal'),
    #path('login/', views.login, name='login'),
#]

urlpatterns = [
    path('',                              views.index,             name='index'),
    path('login/',                        views.vista_iniciar_sesion,        name='login'),
    path('logout/',                       views.vista_cerrar_sesion,       name='logout'),
    path('registro/',                     views.vista_registro,          name='registro'),
    path('parques/',                      views.parques,           name='parques'),
    path('mis-reservaciones/',            views.mis_reservaciones, name='mis_reservaciones'),
    path('registro/exitoso/',             views.vista_registro_exitoso, name='registro_exitoso'),
]