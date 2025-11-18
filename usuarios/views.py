from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .forms import RegistroForm, LoginForm  # , ReviewForm  
from .models import User  # , Review  
# import qrcode
from io import BytesIO
import base64

# Al inicio del archivo, agrega esta vista:
def home(request):
    return render(request, 'usuarios/home.html')
# Registro
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso!')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})
def logout_view(request):
    logout(request)
    return redirect('home')

# Recuperación de contraseña
def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.scheme}://{request.get_host()}/usuarios/reset/{uid}/{token}/"
            send_mail(
                'Recuperación de contraseña',
                f'Usa este link para resetear tu contraseña: {reset_url}',
                'noreply@talkmania.com',
                [email],
            )
            messages.success(request, 'Email enviado. Revisa tu bandeja.')
        except User.DoesNotExist:
            messages.error(request, 'Email no registrado.')
    return render(request, 'usuarios/recuperar_password.html')

# HU 12: Sistema de reseñas 
# @login_required
# def crear_review(request, reserva_id):
#     return render(request, 'usuarios/crear_review.html')

#Versión temporal sin Review
@login_required
def crear_review(request, reserva_id):
    messages.info(request, 'La funcionalidad de reviews estará disponible cuando se implemente el módulo de reservas.')
    return redirect('historial_reservas')

# HU 13: Historial de reservas
@login_required
def historial_reservas(request):
    # reservas = request.user.reservas.all().order_by('-fecha')  # ⚠️ Comentar cuando no existe modelo Reserva
    reservas = []  # ✅ Temporal
    return render(request, 'usuarios/historial_reservas.html', {'reservas': reservas})

# HU 19: Administración de usuarios (solo admin)
@login_required
def administrar_usuarios(request):
    if request.user.rol != 'administrador':
        messages.error(request, 'No tienes permisos.')
        return redirect('home')
    
    usuarios = User.objects.all()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        accion = request.POST.get('accion')
        user = get_object_or_404(User, id=user_id)
        
        if accion == 'bloquear':
            user.bloqueado = not user.bloqueado
            user.save()
        elif accion == 'cambiar_rol':
            nuevo_rol = request.POST.get('rol')
            user.rol = nuevo_rol
            user.save()
        
        messages.success(request, f'Usuario {user.username} actualizado.')
        return redirect('administrar_usuarios')
    
    return render(request, 'usuarios/administrar_usuarios.html', {'usuarios': usuarios})

# HU 20: Verificación QR (COMENTADO TEMPORALMENTE - necesita modelo Reserva)
# @login_required
# def generar_qr_reserva(request, reserva_id):
#     return render(request, 'usuarios/qr_reserva.html')

# ✅ Versión temporal
@login_required
def generar_qr_reserva(request, reserva_id):
    qr_data = f"RESERVA-{reserva_id}-{request.user.id}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'usuarios/qr_reserva.html', {'qr': qr_base64, 'reserva_id': reserva_id})

@login_required
def verificar_qr(request):
    if request.user.rol not in ['administrador', 'staff']:
        messages.error(request, 'No tienes permisos.')
        return redirect('home')
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            parts = codigo.split('-')
            reserva_id = int(parts[1])
            messages.success(request, f'Reserva #{reserva_id} verificada.')
        except:
            messages.error(request, 'Código QR inválido.')
    
    return render(request, 'usuarios/verificar_qr.html')

