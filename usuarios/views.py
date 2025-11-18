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

# Página de inicio (landing)
def index(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'index.html')

# Dashboard (después del login)
@login_required
def home(request):
    # Obtener estadísticas del usuario
    context = {
        'total_reservas': 0,
        'total_reviews': request.user.reviews.count(),
    }
    
    try:
        cliente = request.user.cliente
        context['total_reservas'] = cliente.reservas.count()
    except:
        pass
    
    return render(request, 'usuarios/home.html', context)

# HU 1: Registro
def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear automáticamente un Cliente asociado al User
            try:
                Cliente.objects.create(
                    user=user,
                    nombre=user.username,
                    email=user.email,
                    telefono=user.telefono if user.telefono else '000000000',
                    fecha_nacimiento=timezone.now().date(),
                    fecha_registro=timezone.now().date()
                )
            except Exception as e:
                # Si falla la creación del cliente, eliminar el usuario
                user.delete()
                messages.error(request, f'Error al crear el perfil de cliente: {str(e)}')
                return render(request, 'usuarios/registro.html', {'form': form})
            
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a Talkmania.')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# HU 2: Login
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('index')

# HU 2: Recuperación de contraseña
def recuperar_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = f"{request.scheme}://{request.get_host()}/usuarios/reset/{uid}/{token}/"
            
            # Enviar email (asegúrate de tener configurado SMTP en settings.py)
            send_mail(
                'Recuperación de contraseña - Talkmania',
                f'Hola {user.username},\n\nUsa este enlace para resetear tu contraseña:\n{reset_url}\n\nSi no solicitaste esto, ignora este email.',
                'noreply@talkmania.com',
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Se ha enviado un email con instrucciones. Revisa tu bandeja de entrada.')
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese email.')
        except Exception as e:
            messages.error(request, f'Error al enviar el email: {str(e)}')
    
    return render(request, 'usuarios/recuperar_password.html')

# HU 12: Sistema de reseñas
@login_required
def crear_review(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que la reserva pertenezca al usuario
    try:
        if reserva.Cliente.user != request.user:
            messages.error(request, 'Esta reserva no te pertenece.')
            return redirect('historial_reservas')
    except AttributeError:
        messages.error(request, 'No tienes permisos para dejar una reseña en esta reserva.')
        return redirect('historial_reservas')
    
    # Verificar que la reserva esté completada
    if not reserva.estado:
        messages.warning(request, 'Solo puedes dejar reseñas en reservas completadas.')
        return redirect('historial_reservas')
    
    # Verificar si ya existe una review
    if Review.objects.filter(usuario=request.user, reserva=reserva).exists():
        messages.warning(request, 'Ya has dejado una reseña para esta reserva.')
        return redirect('historial_reservas')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.usuario = request.user
            review.reserva = reserva
            review.save()
            messages.success(request, '¡Reseña publicada exitosamente!')
            return redirect('historial_reservas')
    else:
        form = ReviewForm()
    
    return render(request, 'usuarios/crear_review.html', {'form': form, 'reserva': reserva})

# HU 13: Historial de reservas
@login_required
def historial_reservas(request):
    reservas = []
    sin_perfil = False
    reservas_completadas = 0
    reservas_pendientes = 0
    
    try:
        cliente = request.user.cliente
        reservas = Reserva.objects.filter(Cliente=cliente).order_by('-fecha_reserva')
        
        # Calcular estadísticas
        reservas_completadas = reservas.filter(estado=True).count()
        reservas_pendientes = reservas.filter(estado=False).count()
        
    except AttributeError:
        sin_perfil = True
    
    context = {
        'reservas': reservas,
        'sin_perfil': sin_perfil,
        'total_reservas': reservas.count() if reservas else 0,
        'reservas_completadas': reservas_completadas,
        'reservas_pendientes': reservas_pendientes,
    }
    
    return render(request, 'usuarios/historial_reservas.html', context)

# HU 19: Administración de usuarios (solo admin)
@login_required
def administrar_usuarios(request):
    if request.user.rol != 'administrador':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    usuarios = User.objects.all().order_by('-fecha_registro')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        accion = request.POST.get('accion')
        user = get_object_or_404(User, id=user_id)
        
        if accion == 'bloquear':
            user.bloqueado = not user.bloqueado
            user.save()
            estado = "bloqueado" if user.bloqueado else "desbloqueado"
            messages.success(request, f'Usuario {user.username} ha sido {estado}.')
        elif accion == 'cambiar_rol':
            nuevo_rol = request.POST.get('rol')
            user.rol = nuevo_rol
            user.save()
            messages.success(request, f'Rol de {user.username} actualizado a {nuevo_rol}.')
        
        return redirect('administrar_usuarios')
    
    return render(request, 'usuarios/administrar_usuarios.html', {'usuarios': usuarios})

# HU 20: Verificación QR - Generar
@login_required
def generar_qr_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    # Verificar que la reserva pertenezca al usuario (opcional)
    try:
        if reserva.Cliente.user != request.user and request.user.rol not in ['administrador', 'staff']:
            messages.error(request, 'No tienes permisos para ver este QR.')
            return redirect('historial_reservas')
    except AttributeError:
        pass
    
    # Generar QR con información de la reserva
    qr_data = f"RESERVA-{reserva.id}-{reserva.Cliente.id}"
    qr = qrcode.make(qr_data)
    buffer = BytesIO()
    qr.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'usuarios/qr_reserva.html', {
        'qr': qr_base64, 
        'reserva': reserva,
        'codigo': qr_data
    })

# HU 20: Verificación QR - Verificar
@login_required
def verificar_qr(request):
    if request.user.rol not in ['administrador', 'staff']:
        messages.error(request, 'No tienes permisos para verificar códigos QR.')
        return redirect('home')
    
    reserva_verificada = None
    
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        try:
            # Formato esperado: "RESERVA-123-456"
            parts = codigo.split('-')
            if len(parts) != 3 or parts[0] != 'RESERVA':
                raise ValueError('Formato inválido')
            
            reserva_id = int(parts[1])
            reserva = Reserva.objects.get(id=reserva_id)
            
            if reserva.estado:
                messages.warning(request, f'⚠️ La reserva #{reserva_id} ya estaba verificada anteriormente.')
            else:
                # Marcar como completada (estado = True)
                reserva.estado = True
                reserva.save()
                messages.success(request, f'✅ Reserva #{reserva_id} verificada y marcada como completada.')
            
            reserva_verificada = reserva
            
        except Reserva.DoesNotExist:
            messages.error(request, '❌ No existe una reserva con ese código.')
        except (IndexError, ValueError):
            messages.error(request, '❌ Código QR inválido. Formato esperado: RESERVA-ID-CLIENTE')
    
    return render(request, 'usuarios/verificar_qr.html', {'reserva_verificada': reserva_verificada})