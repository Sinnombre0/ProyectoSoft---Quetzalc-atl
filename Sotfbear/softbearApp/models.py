from django.db import models
from django.contrib.auth.models import User

class Parque(models.Model):
    id                = models.AutoField(primary_key=True)
    nombre            = models.CharField(max_length=120)
    direccion         = models.CharField(max_length=200)
    horario           = models.CharField(max_length=80)
    servicios         = models.CharField(max_length=200)  # "Cabaña,Camping,Guías"
    tiene_cabanas     = models.BooleanField(default=False)
    capacidad_cabanas = models.IntegerField(default=0)
    capacidad_camping = models.IntegerField(default=0)
    latitud = models.FloatField(default=0)  # % posición mapa visual
    longitud = models.FloatField(default=0)

    def servicios_list(self):
        return [s.strip() for s in self.servicios.split(',')]

    def __str__(self):
        return self.nombre

class Reservacion(models.Model):
    TIPO_CHOICES   = [('CABANA', 'Cabaña'), ('CAMPING', 'Camping')]
    ESTADO_CHOICES = [('ACTIVA', 'Activa'), ('CANCELADA', 'Cancelada')]

    usuario       = models.ForeignKey(User, on_delete=models.CASCADE)
    parque        = models.ForeignKey(Parque, on_delete=models.CASCADE)
    fecha_inicio  = models.DateField()
    fecha_termino = models.DateField()
    num_personas  = models.PositiveSmallIntegerField(default=1)
    tipo_visita   = models.CharField(max_length=10, choices=TIPO_CHOICES)
    estado        = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ACTIVA')

    def __str__(self):
        return f"{self.usuario} → {self.parque} ({self.fecha_inicio})"