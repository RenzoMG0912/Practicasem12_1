import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger('core.middleware')


class AuditoriaMiddleware(MiddlewareMixin):
    RUTAS_EXCLUIDAS = ['/static/', '/favicon.ico']

    def process_request(self, request):
        request._inicio_tiempo = time.time()

        for ruta in self.RUTAS_EXCLUIDAS:
            if request.path.startswith(ruta):
                return None

        usuario = request.user.username if request.user.is_authenticated else 'Anónimo'
        ip = self._obtener_ip(request)

        logger.info(
            f"REQUEST | Usuario: {usuario} | IP: {ip} | "
            f"Método: {request.method} | Ruta: {request.path}"
        )

        request.session['ultima_actividad'] = timezone.now().isoformat()
        if request.user.is_authenticated:
            request.session.modified = True

        return None

    def process_response(self, request, response):
        for ruta in self.RUTAS_EXCLUIDAS:
            if request.path.startswith(ruta):
                return response

        tiempo_ms = None
        if hasattr(request, '_inicio_tiempo'):
            tiempo_ms = (time.time() - request._inicio_tiempo) * 1000

        usuario = request.user.username if request.user.is_authenticated else 'Anónimo'

        logger.info(
            f"RESPONSE | Usuario: {usuario} | Ruta: {request.path} | "
            f"Status: {response.status_code} | Tiempo: {tiempo_ms:.2f}ms"
        )

        response['X-Tiempo-Respuesta'] = f"{tiempo_ms:.2f}ms" if tiempo_ms else '0ms'
        response['X-Powered-By'] = 'Django 5.x'
        response['X-Content-Type-Options'] = 'nosniff'

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        usuario = request.user.username if request.user.is_authenticated else 'Anónimo'
        logger.info(
            f"VIEW | Usuario: {usuario} | Vista: {view_func.__name__} | Ruta: {request.path}"
        )
        return None

    def _obtener_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')


class TiempoRespuestaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        inicio = time.time()

        response = self.get_response(request)

        duracion = (time.time() - inicio) * 1000

        if duracion > 2000:
            logger.warning(
                f"RESPUESTA LENTA: {request.path} tardó {duracion:.2f}ms"
            )

        return response
