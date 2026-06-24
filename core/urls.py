from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('logout-seguro/', views.cerrar_sesion_seguro, name='logout_seguro'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('contacto/', views.contacto, name='contacto'),
    path('contacto/exito/', views.contacto_exito, name='contacto_exito'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
