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
    path('login/',                        views.login_view,        name='login'),
    path('logout/',                       views.logout_view,       name='logout'),
    path('registro/',                     views.registro,          name='registro'),
    path('parques/',                      views.parques,           name='parques'),
    path('mis-reservaciones/',            views.mis_reservaciones, name='mis_reservaciones'),
]