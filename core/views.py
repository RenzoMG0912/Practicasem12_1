from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User

from .forms import ContactoForm, ProductoForm, RegistroUsuarioForm
from .models import Producto, LogAcceso, Contacto


def home(request):
    productos_destacados = Producto.objects.filter(activo=True).order_by('-fecha_creacion')[:6]
    context = {
        'productos_destacados': productos_destacados,
        'total_productos': Producto.objects.filter(activo=True).count(),
    }
    return render(request, 'core/home.html', context)


def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f'¡Bienvenido {user.first_name}! Tu cuenta fue creada exitosamente.'
            )
            return redirect('dashboard')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'registration/registro.html', {'form': form})


@login_required
def dashboard(request):
    mis_productos = Producto.objects.filter(creado_por=request.user)
    stats = {
        'total': mis_productos.count(),
        'activos': mis_productos.filter(activo=True).count(),
        'sin_stock': mis_productos.filter(stock=0).count(),
    }
    ultimos_accesos = LogAcceso.objects.filter(usuario=request.user).order_by('-timestamp')[:10]
    ultima_actividad = request.session.get('ultima_actividad', 'No disponible')

    context = {
        'stats': stats,
        'mis_productos': mis_productos[:5],
        'ultimos_accesos': ultimos_accesos,
        'ultima_actividad': ultima_actividad,
        'session_key': request.session.session_key,
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.creado_por = request.user
            producto.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" creado exitosamente.')
            return redirect('lista_productos')
        else:
            messages.error(request, '⚠️ Revisa los errores del formulario.')
    else:
        form = ProductoForm()

    return render(request, 'core/producto_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Producto',
        'accion': 'Crear',
    })


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk, creado_por=request.user)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" actualizado.')
            return redirect('lista_productos')
        else:
            messages.error(request, '⚠️ Corrige los errores antes de guardar.')
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'core/producto_form.html', {
        'form': form,
        'titulo': f'Editar: {producto.nombre}',
        'accion': 'Actualizar',
        'producto': producto,
    })


@login_required
def lista_productos(request):
    productos = Producto.objects.filter(creado_por=request.user).order_by('-fecha_creacion')
    categoria = request.GET.get('categoria')
    if categoria:
        productos = productos.filter(categoria=categoria)

    return render(request, 'core/lista_productos.html', {
        'productos': productos,
        'categorias': Producto.CATEGORIA_CHOICES,
        'categoria_activa': categoria,
    })


@require_http_methods(["GET", "POST"])
def contacto(request):
    if request.method == 'POST':
        form = ContactoForm(request.POST)
        if form.is_valid():
            Contacto.objects.create(
                nombre=form.cleaned_data['nombre'],
                email=form.cleaned_data['email'],
                asunto=form.cleaned_data['asunto'],
                mensaje=form.cleaned_data['mensaje'],
            )
            messages.success(
                request,
                f'✅ Gracias {form.cleaned_data["nombre"]}, tu mensaje fue enviado correctamente.'
            )
            return redirect('contacto_exito')
        else:
            messages.error(request, '⚠️ Hay errores en el formulario. Revísalos.')
    else:
        form = ContactoForm()

    return render(request, 'core/contacto.html', {'form': form})


def contacto_exito(request):
    return render(request, 'core/contacto_exito.html')


@login_required
def perfil(request):
    context = {
        'usuario': request.user,
        'session_info': {
            'key': request.session.session_key,
            'ultima_actividad': request.session.get('ultima_actividad'),
            'expira': request.session.get_expiry_date(),
        }
    }
    return render(request, 'core/perfil.html', context)


@login_required
def cerrar_sesion_seguro(request):
    nombre = request.user.first_name or request.user.username
    request.session.flush()
    logout(request)
    messages.info(request, f'👋 Hasta luego, {nombre}. Sesión cerrada correctamente.')
    return redirect('login')


@login_required
def api_stats(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Sin permisos'}, status=403)

    stats = {
        'total_usuarios': User.objects.count(),
        'total_productos': Producto.objects.count(),
        'productos_activos': Producto.objects.filter(activo=True).count(),
        'total_contactos': Contacto.objects.count(),
        'contactos_no_leidos': Contacto.objects.filter(leido=False).count(),
    }
    return JsonResponse(stats)
