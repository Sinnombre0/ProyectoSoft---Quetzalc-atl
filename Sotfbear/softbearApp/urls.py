from django.contrib import admin
from django.urls import path


from . import views

app_name = 'softbearApp'

urlpatterns = [
    # Nada de momento
    path('', views.pagina_principal, name='pagina_principal'),

    path('login/', views.login, name='login'),
]