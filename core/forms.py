import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.html import escape

from .models import Producto, Contacto
from .validators import (
    validar_solo_letras, validar_precio_positivo,
    validar_sin_html, validar_email_corporativo,
    sanitize_input, validar_no_sql_injection
)


class ContactoForm(forms.Form):
    nombre = forms.CharField(
        max_length=100,
        label='Nombre completo',
        validators=[validar_solo_letras, validar_sin_html],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu nombre completo',
            'autocomplete': 'off',
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        validators=[validar_email_corporativo],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'tu@email.com',
        })
    )
    asunto = forms.CharField(
        max_length=200,
        label='Asunto',
        validators=[validar_sin_html, validar_no_sql_injection],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Asunto del mensaje',
        })
    )
    mensaje = forms.CharField(
        label='Mensaje',
        validators=[validar_sin_html, validar_no_sql_injection],
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Escribe tu mensaje aquí...',
        })
    )
    confirmar_email = forms.EmailField(
        label='Confirmar correo',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu email',
        })
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        nombre = sanitize_input(nombre)
        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre.title()

    def clean_asunto(self):
        asunto = self.cleaned_data.get('asunto', '')
        asunto = sanitize_input(asunto)
        palabras_prohibidas = ['spam', 'publicidad', 'promo', 'oferta gratis']
        for palabra in palabras_prohibidas:
            if palabra.lower() in asunto.lower():
                raise ValidationError(f'El asunto contiene contenido no permitido: "{palabra}".')
        return asunto

    def clean_mensaje(self):
        mensaje = self.cleaned_data.get('mensaje', '')
        mensaje = sanitize_input(mensaje)
        if len(mensaje) < 20:
            raise ValidationError('El mensaje debe tener al menos 20 caracteres.')
        if len(mensaje) > 2000:
            raise ValidationError('El mensaje no puede exceder 2000 caracteres.')
        return mensaje

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').lower()
        confirmar_email = cleaned_data.get('confirmar_email', '').lower()

        if email and confirmar_email and email != confirmar_email:
            self.add_error('confirmar_email', 'Los correos electrónicos no coinciden.')

        nombre = cleaned_data.get('nombre', '')
        mensaje = cleaned_data.get('mensaje', '')
        if nombre and mensaje and nombre.lower() in mensaje.lower():
            self.add_error(
                'mensaje',
                'Por seguridad, evita incluir tu nombre dentro del mensaje.'
            )

        return cleaned_data


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio (S/.)',
            'stock': 'Cantidad en Stock',
            'categoria': 'Categoría',
            'activo': '¿Producto activo?',
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre del producto es obligatorio.',
                'max_length': 'El nombre no puede superar 150 caracteres.',
            },
            'precio': {
                'required': 'Debes ingresar un precio.',
                'invalid': 'Ingresa un precio válido (ej: 29.99).',
            },
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '')
        nombre = sanitize_input(nombre)
        if len(nombre) < 3:
            raise ValidationError('El nombre del producto debe tener al menos 3 caracteres.')
        if Producto.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk).exists():
            raise ValidationError(f'Ya existe un producto con el nombre "{nombre}".')
        return nombre.capitalize()

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None:
            validar_precio_positivo(precio)
        return precio

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion', '')
        if descripcion:
            descripcion = sanitize_input(descripcion)
            validar_sin_html(descripcion)
        return descripcion

    def clean(self):
        cleaned_data = super().clean()
        precio = cleaned_data.get('precio')
        stock = cleaned_data.get('stock')
        activo = cleaned_data.get('activo')

        if activo and stock == 0:
            self.add_error(
                'stock',
                'No puedes activar un producto sin stock. Agrega unidades o márcalo como inactivo.'
            )

        if precio and stock:
            valor_total = precio * stock
            if valor_total > 5000000:
                raise ValidationError(
                    f'El valor total de inventario (S/. {valor_total:,.2f}) excede el límite permitido.'
                )

        return cleaned_data


class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        validators=[validar_email_corporativo],
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'tu@email.com'})
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nombre',
        validators=[validar_solo_letras],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Apellido',
        validators=[validar_solo_letras],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tu apellido'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if len(username) < 4:
            raise ValidationError('El nombre de usuario debe tener al menos 4 caracteres.')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError('El usuario solo puede contener letras, números y guion bajo.')
        return username.lower()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name'].capitalize()
        user.last_name = self.cleaned_data['last_name'].capitalize()
        if commit:
            user.save()
        return user
