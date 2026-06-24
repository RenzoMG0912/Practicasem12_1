# Practica Django 5.x - Seguridad y Gestion de Datos

## Estructura del Proyecto

```
practica_django/
├── config/
│   ├── settings.py      # Configuracion: SESSION, CSRF, MIDDLEWARE, LOGGING
│   └── urls.py          # Rutas principales + auth views
├── core/
│   ├── models.py        # Producto, LogAcceso, Contacto
│   ├── forms.py         # ContactoForm (clasico) + ProductoForm (ModelForm) + RegistroForm
│   ├── validators.py    # Validadores personalizados + sanitize_input()
│   ├── middleware.py    # AuditoriaMiddleware + TiempoRespuestaMiddleware
│   ├── admin.py         # Admin personalizado: display, filtros, acciones, campos calculados
│   ├── views.py         # Vistas con @login_required, @permission_required
│   └── urls.py          # Rutas de la app
├── templates/
│   ├── base.html        # Template base con navbar
│   ├── registration/    # login.html, registro.html
│   └── core/            # home, dashboard, producto_form, lista, contacto, perfil
├── seed_datos.py        # Script para poblar la BD con datos de prueba
├── requirements.txt
└── logs/
    └── auditoria.log    # Generado al ejecutar el servidor
```

## Instalacion y Ejecucion

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones
python manage.py migrate

# 4. Poblar base de datos (opcional)
python seed_datos.py

# 5. Ejecutar servidor
python manage.py runserver
```

## Credenciales de Prueba

| Usuario  | Password      | Rol             |
|----------|---------------|-----------------|
| admin    | Admin1234!    | Superusuario    |
| editor   | Editor1234!   | Staff (permisos)|
| cliente  | Cliente1234!  | Usuario normal  |

## URLs Principales

| URL                    | Descripcion                        | Acceso       |
|------------------------|------------------------------------|--------------|
| /                      | Pagina de inicio                   | Publico      |
| /login/                | Inicio de sesion                   | Publico      |
| /registro/             | Registro de usuario                | Publico      |
| /dashboard/            | Panel de usuario                   | Autenticado  |
| /productos/            | Lista de productos                 | Autenticado  |
| /productos/nuevo/      | Crear producto                     | Autenticado  |
| /contacto/             | Formulario de contacto             | Publico      |
| /perfil/               | Info sesion y usuario              | Autenticado  |
| /logout-seguro/        | Cerrar sesion (flush session)      | Autenticado  |
| /admin/                | Django Admin personalizado         | Staff        |
| /api/stats/            | Estadisticas JSON                  | Staff        |

## Conceptos Implementados por Fase

### Fase 1 - Formularios y Templates
- `ContactoForm`: formulario clasico (forms.Form)
- `ProductoForm`: ModelForm con Meta, widgets, labels, error_messages
- `RegistroUsuarioForm`: extiende UserCreationForm
- Templates: uso de {{ form.as_p }}, {{ form.errors }}, {% csrf_token %}

### Fase 2 - Validacion y Sanitizacion
- `clean_campo()`: validacion a nivel de campo en cada formulario
- `clean()`: validacion cross-field (ej: email == confirmar_email)
- `validators.py`: validar_solo_letras, validar_sin_html, validar_no_sql_injection
- `sanitize_input()`: strip() + colapso de espacios + escape() para XSS

### Fase 3 - Django Admin
- `ProductoAdmin`: list_display, list_filter, search_fields, readonly_fields, fieldsets
- Campos calculados con @admin.display (precio_formateado, estado_stock_display)
- Acciones masivas: activar, desactivar, exportar CSV
- `LogAccesoAdmin`: readonly, sin add/change permissions
- `admin.site.site_header`, `index_title` personalizados

### Fase 4 - Middleware y Sesiones
- `AuditoriaMiddleware`: process_request, process_response, process_view
- `TiempoRespuestaMiddleware`: patron __init__/__call__ (nuevo estilo)
- `SESSION_ENGINE`, `SESSION_COOKIE_AGE`, `SESSION_COOKIE_HTTPONLY`
- `@login_required` en todas las vistas protegidas
- `request.session.flush()` en logout para invalidar completamente
- Headers personalizados: X-Tiempo-Respuesta, X-Content-Type-Options

### Fase 5 - Integracion y Auditoria
- Flujo completo: registro -> login -> dashboard -> productos -> admin -> logout
- LOGGING configurado: archivo logs/auditoria.log + consola
- Verificar: python manage.py check
- Headers de seguridad: X-Frame-Options (DENY por defecto Django), X-Content-Type-Options
