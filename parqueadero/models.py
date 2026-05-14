from django.db import models
from django.contrib.auth.models import User


class Parqueadero(models.Model):
    TIPO_ACCESO_CHOICES = [
        ('general', 'General'),
        ('profesores', 'Solo profesores'),
    ]

    nombre = models.CharField(max_length=100, unique=True)
    capacidad = models.IntegerField()
    ocupancia = models.IntegerField(default=0)
    tipo_acceso = models.CharField(max_length=20, choices=TIPO_ACCESO_CHOICES, default='general')

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
        ('trabajador', 'Trabajador'),
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


class MetodoPago(models.Model):
    usuario = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.CASCADE,
        related_name='metodos_pago',
    )
    titular = models.CharField(max_length=100)
    marca = models.CharField(max_length=40, default='Tarjeta')
    ultimos_cuatro = models.CharField(max_length=4)
    mes_expiracion = models.PositiveSmallIntegerField()
    anio_expiracion = models.PositiveSmallIntegerField()
    es_activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def numero_enmascarado(self):
        return f"**** **** **** {self.ultimos_cuatro}"

    @property
    def vencimiento(self):
        return f"{self.mes_expiracion:02d}/{str(self.anio_expiracion)[-2:]}"

    def __str__(self):
        return f"{self.marca} {self.numero_enmascarado} - {self.usuario.user.username}"

    class Meta:
        ordering = ['-es_activa', '-actualizado_en']


class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallet',
    )
    balance_cop = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet de {self.user.username}: ${self.balance_cop} COP"


class RechargeTransaction(models.Model):
    PROVIDER_DEMO = 'demo'
    PROVIDER_WOMPI = 'wompi'
    PROVIDER_CHOICES = [
        (PROVIDER_DEMO, 'Demo'),
        (PROVIDER_WOMPI, 'Wompi'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_APPROVED = 'APPROVED'
    STATUS_DECLINED = 'DECLINED'
    STATUS_ERROR = 'ERROR'
    STATUS_VOIDED = 'VOIDED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_APPROVED, 'Aprobada'),
        (STATUS_DECLINED, 'Rechazada'),
        (STATUS_ERROR, 'Error'),
        (STATUS_VOIDED, 'Anulada'),
    ]

    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recharge_transactions',
    )
    session_key = models.CharField(max_length=64, blank=True)
    amount_cop = models.PositiveIntegerField()
    amount_in_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default='COP')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_DEMO)
    payment_method = models.CharField(max_length=40, blank=True)
    reference = models.CharField(max_length=80, unique=True)
    provider_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    wompi_transaction_id = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    credited = models.BooleanField(default=False)
    is_credited = models.BooleanField(default=False)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.reference} - {self.status} - ${self.amount_cop} COP"

    class Meta:
        ordering = ['-created_at']


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


class AvisoEnCamino(models.Model):
    usuario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE)
    parqueadero = models.ForeignKey(Parqueadero, on_delete=models.CASCADE)
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE)
    eta_minutos = models.IntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)
    llegada_estimada = models.DateTimeField()
    agregado_a_fila = models.BooleanField(default=False)
    cancelado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.user.username} -> {self.entrada.nombre}"

    class Meta:
        ordering = ['-creado_en']
