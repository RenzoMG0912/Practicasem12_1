from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Producto(models.Model):
    CATEGORIA_CHOICES = [
        ('electronica', 'Electrónica'),
        ('ropa', 'Ropa'),
        ('alimentos', 'Alimentos'),
        ('libros', 'Libros'),
        ('otros', 'Otros'),
    ]

    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES, default='otros')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"

    @property
    def valor_inventario(self):
        return self.precio * self.stock

    @property
    def estado_stock(self):
        if self.stock == 0:
            return 'Sin stock'
        elif self.stock < 5:
            return 'Stock bajo'
        return 'Disponible'


class LogAcceso(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=200)
    ip = models.GenericIPAddressField(null=True, blank=True)
    ruta = models.CharField(max_length=300)
    metodo = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    tiempo_respuesta_ms = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = 'Log de Acceso'
        verbose_name_plural = 'Logs de Acceso'
        ordering = ['-timestamp']

    def __str__(self):
        user = self.usuario.username if self.usuario else 'Anónimo'
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {user} - {self.ruta}"


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"
