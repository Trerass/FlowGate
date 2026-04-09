from django.db import models
from django.contrib.auth.models import User


class Parqueadero(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.IntegerField()
    ocupancia = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre

class Entrada(models.Model):
    nombre = models.CharField(max_length=100)
    parqueadero = models.ForeignKey(Parqueadero, on_delete=models.CASCADE)
    fila = models.IntegerField(default=0)  # Vehículos en fila

    def __str__(self):
        return f"{self.parqueadero.nombre} - {self.nombre}"

    class Meta:
        unique_together = ('parqueadero', 'nombre')

class PerfilUsuario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True)
    codigo_estudiantil = models.CharField(max_length=50, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='estudiante')
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

class Vehiculo(models.Model):
    TIPO_VEHICULO_CHOICES = [
        ('carro', 'Carro'),
        ('moto', 'Moto'),
    ]
    
    usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    tipo_vehiculo = models.CharField(max_length=20, choices=TIPO_VEHICULO_CHOICES)
    es_electrico = models.BooleanField(default=False)
    precio_diario = models.IntegerField(default=0)
    
    def calcular_precio(self):
        """Calcula el precio diario basado en el tipo de vehículo."""
        if self.es_electrico:
            return 0
        elif self.tipo_vehiculo == 'carro':
            return 8700
        elif self.tipo_vehiculo == 'moto':
            return 5000
        return 0
    
    def save(self, *args, **kwargs):
        self.precio_diario = self.calcular_precio()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa})"

class Historial(models.Model):
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    parqueadero = models.ForeignKey(Parqueadero, on_delete=models.CASCADE)
    entrada = models.ForeignKey(Entrada, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField()
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    costo = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.usuario.user.username} - {self.parqueadero.nombre} ({self.fecha})"
    
    class Meta:
        ordering = ['-fecha', '-hora_entrada']
