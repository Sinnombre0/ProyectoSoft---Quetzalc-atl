from django.db import models
from django.contrib.auth.models import User

class Parque(models.Model):
    nombre    = models.CharField(max_length=120)
    direccion = models.CharField(max_length=200)
    horario   = models.CharField(max_length=80)
    x         = models.IntegerField(default=50)   # % para posición en mapa
    y         = models.IntegerField(default=50)
    servicios = models.CharField(max_length=200)  # "Cabaña,Camping,Guías"

    def servicios_list(self):
        return [s.strip() for s in self.servicios.split(',')]

    def __str__(self):
        return self.nombre

class Reservacion(models.Model):
    TIPO_CHOICES = [('Cabaña', 'Cabaña'), ('Camping', 'Camping')]
    usuario      = models.ForeignKey(User, on_delete=models.CASCADE)
    parque       = models.ForeignKey(Parque, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    noches       = models.PositiveSmallIntegerField(default=1)
    personas     = models.PositiveSmallIntegerField(default=1)
    tipo         = models.CharField(max_length=20, choices=TIPO_CHOICES)

    def __str__(self):
        return f"{self.usuario} → {self.parque} ({self.fecha_inicio})"