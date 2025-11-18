# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Review

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'rol', 'bloqueado', 'fecha_registro']
    list_filter = ['rol', 'bloqueado', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'telefono']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol', 'telefono', 'bloqueado', 'fecha_registro')}),
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'reserva', 'calificacion', 'fecha']
    list_filter = ['calificacion', 'fecha']
    search_fields = ['usuario__username', 'comentario']
    readonly_fields = ['fecha']
