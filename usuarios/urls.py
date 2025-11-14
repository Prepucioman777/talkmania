# usuarios/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recuperar-password/', views.recuperar_password, name='recuperar_password'),
    path('historial/', views.historial_reservas, name='historial_reservas'),
    #path('review/<int:reserva_id>/', views.crear_review, name='crear_review'),
    path('admin/usuarios/', views.administrar_usuarios, name='administrar_usuarios'),
    path('qr/<int:reserva_id>/', views.generar_qr_reserva, name='generar_qr'),
    path('verificar-qr/', views.verificar_qr, name='verificar_qr'),
]