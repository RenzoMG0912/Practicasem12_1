from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, F
from django.http import HttpResponse
import csv
import datetime

from .models import Producto, LogAcceso, Contacto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'categoria', 'precio_formateado',
        'stock', 'estado_stock_display', 'valor_inventario_display',
        'activo', 'creado_por', 'fecha_creacion'
    ]
    list_filter = ['categoria', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion', 'creado_por__username']
    readonly_fields = ['fecha_creacion', 'creado_por', 'valor_inventario_display', 'estado_stock_display']
    list_per_page = 20
    list_select_related = ['creado_por']
    date_hierarchy = 'fecha_creacion'
    ordering = ['-fecha_creacion']

    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'descripcion', 'categoria')
        }),
        ('Precios y Stock', {
            'fields': ('precio', 'stock', 'activo'),
            'classes': ('wide',),
        }),
        ('Metadata (Solo Lectura)', {
            'fields': ('fecha_creacion', 'creado_por', 'valor_inventario_display', 'estado_stock_display'),
            'classes': ('collapse',),
        }),
    )

    actions = ['activar_productos', 'desactivar_productos', 'exportar_csv']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='Precio', ordering='precio')
    def precio_formateado(self, obj):
        return format_html('<strong>S/. {}</strong>', f"{obj.precio:,.2f}")

    @admin.display(description='Estado Stock', ordering='stock')
    def estado_stock_display(self, obj):
        estado = obj.estado_stock
        colores = {
            'Sin stock': '#dc3545',
            'Stock bajo': '#ffc107',
            'Disponible': '#28a745',
        }
        color = colores.get(estado, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, estado
        )

    @admin.display(description='Valor Inventario')
    def valor_inventario_display(self, obj):
        valor = obj.valor_inventario
        return format_html('S/. {}', f"{valor:,.2f}")

    @admin.action(description='✅ Activar productos seleccionados')
    def activar_productos(self, request, queryset):
        actualizados = queryset.filter(stock__gt=0).update(activo=True)
        sin_stock = queryset.filter(stock=0).count()
        if actualizados:
            self.message_user(request, f'{actualizados} producto(s) activados correctamente.')
        if sin_stock:
            self.message_user(
                request,
                f'{sin_stock} producto(s) no se activaron porque no tienen stock.',
                level='warning'
            )

    @admin.action(description='❌ Desactivar productos seleccionados')
    def desactivar_productos(self, request, queryset):
        actualizados = queryset.update(activo=False)
        self.message_user(request, f'{actualizados} producto(s) desactivados.')

    @admin.action(description='📥 Exportar seleccionados a CSV')
    def exportar_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        fecha = datetime.date.today().strftime('%Y%m%d')
        response['Content-Disposition'] = f'attachment; filename="productos_{fecha}.csv"'

        writer = csv.writer(response)
        writer.writerow(['ID', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Activo', 'Valor Inventario'])

        for p in queryset.select_related('creado_por'):
            writer.writerow([
                p.pk, p.nombre, p.get_categoria_display(),
                p.precio, p.stock, 'Sí' if p.activo else 'No',
                p.valor_inventario
            ])

        return response

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(creado_por=request.user)
        return qs


@admin.register(LogAcceso)
class LogAccesoAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'usuario', 'metodo', 'ruta', 'ip', 'tiempo_respuesta_ms']
    list_filter = ['metodo', 'timestamp']
    search_fields = ['usuario__username', 'ruta', 'ip']
    readonly_fields = ['usuario', 'accion', 'ip', 'ruta', 'metodo', 'timestamp', 'tiempo_respuesta_ms']
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'email', 'asunto', 'fecha_envio', 'estado_lectura']
    list_filter = ['leido', 'fecha_envio']
    search_fields = ['nombre', 'email', 'asunto']
    readonly_fields = ['nombre', 'email', 'asunto', 'mensaje', 'fecha_envio']
    actions = ['marcar_leido', 'marcar_no_leido']

    @admin.display(description='Estado', boolean=False)
    def estado_lectura(self, obj):
        if obj.leido:
            return format_html('<span style="color: green;">✔ Leído</span>')
        return format_html('<span style="color: red;">✉ No leído</span>')

    @admin.action(description='Marcar como leído')
    def marcar_leido(self, request, queryset):
        queryset.update(leido=True)

    @admin.action(description='Marcar como no leído')
    def marcar_no_leido(self, request, queryset):
        queryset.update(leido=False)


admin.site.site_header = '🛡️ Panel de Administración - Práctica Django'
admin.site.site_title = 'Admin Django 5'
admin.site.index_title = 'Gestión del Sistema'
