from django.db import models
from django.conf import settings  # ✅ Para referenciar el modelo User

class Cliente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='cliente')  # ✅ NUEVO
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    telefono = models.CharField(max_length=9)  # ✅ Cambié IntegerField por CharField
    fecha_nacimiento = models.DateField()
    fecha_registro = models.DateField()
    
    def __str__(self):
        return self.nombre

class Admin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='admin_profile')  # ✅ NUEVO
    usuario = models.CharField(max_length=100)
    contraseña = models.CharField(max_length=50)
    email = models.CharField(max_length=150)
    nombre = models.CharField(max_length=100)
    fecha_creacion = models.DateField()
    ultimo_acceso = models.DateField()
    estado = models.BooleanField()
    
    def __str__(self):
        return self.nombre

class Hotel(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=9)  # ✅ Cambié IntegerField por CharField
    email = models.CharField(max_length=150)
    estrellas = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # ✅ Cambié rango a 1-5
    descripcion = models.TextField()
    estado = models.BooleanField()
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nombre} ({self.estrellas} estrellas)"

class Habitacion(models.Model):
    TIPOS_HABITACION = [
        ('S', 'Simple'),
        ('D', 'Doble'),
        ('SU', 'Suite'),
        ('F', 'Familiar'),
    ]
    ESTADOS_HABITACION = [
        ('D', 'Disponible'),
        ('O', 'Ocupada'),
        ('M', 'Mantenimiento'),
        ('R', 'Reservada'),
    ]
    
    numero = models.IntegerField()
    tipo = models.CharField(max_length=2, choices=TIPOS_HABITACION) 
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=1, choices=ESTADOS_HABITACION, default='D')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='habitaciones')

    def __str__(self):
        return f'Habitación {self.numero} - {self.hotel.nombre}'

class tipo_pago(models.Model):
    metodos = [
        ('E', 'Efectivo'),
        ('D', 'Débito'),
        ('C', 'Crédito'),
        ('T', 'Transferencia'), 
        ('P', 'PayPal'),
    ]
    metodo_pago = models.CharField(max_length=1, choices=metodos)
    
    def __str__(self):
        return self.get_metodo_pago_display()

class Reserva(models.Model):
    fecha_reserva = models.DateField()
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    estado = models.BooleanField(default=False)  # False = Pendiente, True = Completada
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(null=True, blank=True)
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='reservas')
    Hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reservas')
    tipo_pago = models.ForeignKey('tipo_pago', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Reserva #{self.id} - {self.Cliente.nombre}"

class Reserva_Habitacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='habitaciones')
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ['reserva', 'habitacion']
    
    def __str__(self):
        return f"{self.reserva} - {self.habitacion}"