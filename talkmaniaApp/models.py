from django.db import models

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.CharField(max_length=150)
    telefono = models.IntegerField(max_length=9)
    fecha_nacimiento = models.DateField()
    fecha_registro = models.DateField()

class Admin(models.Model):
    usuario = models.CharField(max_length=100)
    contraseña = models.CharField(max_length=50)
    email=models.CharField(max_length=150)
    nombre= models.CharField(max_length=100)
    fecha_creacion=models.DateField()
    ultimo_acceso=models.DateField()
    estado= models.BooleanField()

class Hotel(models.Model):
    nombre=models.CharField(max_length=100)
    direccion=models.CharField(max_length=200)
    telefono=models.IntegerField(max_length=9)
    email=models.CharField(max_length=150)
    estrellas = models.IntegerField(choices=[(i, i) for i in range(1, 5)])
    descripcion=models.TextField()
    estado=models.BooleanField()
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
    
    numero=models.IntegerField()
    tipo=models.CharField(max_length=2, choices=TIPOS_HABITACION) 
    precio=models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=1, choices=ESTADOS_HABITACION)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)

    def __str__(self):
        return f'Habitación {self.numero}'
    

class tipo_pago(models.Model):
    metodos = [
        ('E', 'Efectivo'),
        ('D', 'Debito'),
        ('C', 'Credito'),
        ('T', 'Transferencia'), 
        ('P', 'PayPal'),
    ]
    metodo_pago = models.CharField(max_length=1, choices=metodos)

class Reserva(models.Model):
    fecha_reserva = models.DateField()
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    estado = models.BooleanField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField()
    Cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    Hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    tipo_pago= models.ForeignKey('tipo_pago', on_delete=models.CASCADE)

class Reserva_Habitacion(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)