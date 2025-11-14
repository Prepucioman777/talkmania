from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
        ('staff', 'Staff'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    fecha_registro = models.DateTimeField(default=timezone.now)
    bloqueado = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    def __str__(self):
        return self.username

# class Review(models.Model):
#     usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
#     reserva = models.ForeignKey('reservas.Reserva', on_delete=models.CASCADE)
#     calificacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
#     comentario = models.TextField()
#     fecha = models.DateTimeField(auto_now_add=True)
#     
#     class Meta:
#         unique_together = ['usuario', 'reserva']
#     
#     def __str__(self):
#         return f"Review de {self.usuario.username} - {self.calificacion}★"