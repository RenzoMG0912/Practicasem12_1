import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Permission
from core.models import Producto, Contacto
from decimal import Decimal

print("Creando usuarios de prueba...")

if not User.objects.filter(username='editor').exists():
    editor = User.objects.create_user(
        username='editor',
        password='Editor1234!',
        email='editor@practica.com',
        first_name='Maria',
        last_name='Garcia',
        is_staff=True
    )
    perm = Permission.objects.get(codename='change_producto')
    editor.user_permissions.add(perm)
    print(f"  Usuario 'editor' creado (Staff: Si)")

if not User.objects.filter(username='cliente').exists():
    cliente = User.objects.create_user(
        username='cliente',
        password='Cliente1234!',
        email='cliente@practica.com',
        first_name='Carlos',
        last_name='Lopez'
    )
    print(f"  Usuario 'cliente' creado (Staff: No)")

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='Admin1234!',
        email='admin@practica.com',
        first_name='Admin',
        last_name='Sistemas'
    )
    print("  Superusuario 'admin' creado")
else:
    admin = User.objects.get(username='admin')

print("\nCreando productos de ejemplo...")
productos_data = [
    {'nombre': 'Laptop Pro X1', 'descripcion': 'Laptop de alta gama para profesionales', 'precio': Decimal('2500.00'), 'stock': 15, 'categoria': 'electronica'},
    {'nombre': 'Auriculares Bluetooth', 'descripcion': 'Auriculares inalambricos con cancelacion de ruido', 'precio': Decimal('299.99'), 'stock': 3, 'categoria': 'electronica'},
    {'nombre': 'Camiseta Polo', 'descripcion': 'Camiseta polo de algodon premium', 'precio': Decimal('49.90'), 'stock': 50, 'categoria': 'ropa'},
    {'nombre': 'Python para Principiantes', 'descripcion': 'Libro completo de programacion en Python', 'precio': Decimal('75.00'), 'stock': 0, 'categoria': 'libros'},
    {'nombre': 'Cafe Organico 500g', 'descripcion': 'Cafe de altura tostado artesanalmente', 'precio': Decimal('35.00'), 'stock': 100, 'categoria': 'alimentos'},
    {'nombre': 'Mochila Urbana', 'descripcion': 'Mochila resistente con compartimento laptop', 'precio': Decimal('120.00'), 'stock': 8, 'categoria': 'otros'},
]

for data in productos_data:
    activo = data['stock'] > 0
    p, creado = Producto.objects.get_or_create(
        nombre=data['nombre'],
        defaults={**data, 'activo': activo, 'creado_por': admin}
    )
    if creado:
        print(f"  Producto creado: {p.nombre}")

print("\nCreando mensajes de contacto...")
contactos_data = [
    {'nombre': 'Ana Torres', 'email': 'ana@email.com', 'asunto': 'Consulta sobre productos', 'mensaje': 'Buenos dias, me gustaria saber mas sobre sus productos electronicos disponibles.'},
    {'nombre': 'Pedro Sanchez', 'email': 'pedro@email.com', 'asunto': 'Problema con mi pedido', 'mensaje': 'Hola, tengo un inconveniente con mi ultimo pedido y necesito asistencia urgente.', 'leido': True},
]
for data in contactos_data:
    c, creado = Contacto.objects.get_or_create(email=data['email'], defaults=data)
    if creado:
        print(f"  Contacto creado: {c.nombre}")

print("\n=== DATOS DE ACCESO ===")
print("Admin:   usuario=admin      | password=Admin1234!")
print("Editor:  usuario=editor     | password=Editor1234!")
print("Cliente: usuario=cliente    | password=Cliente1234!")
print("URL Admin: http://127.0.0.1:8000/admin/")
print("URL App:   http://127.0.0.1:8000/")
print("======================")
