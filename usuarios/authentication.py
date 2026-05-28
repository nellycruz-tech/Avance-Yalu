#usuarios\authentication.py

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario

try:
    from firebase_admin import auth as firebase_auth
    FIREBASE_DISPONIBLE = True
except ImportError:
    FIREBASE_DISPONIBLE = False


class FirebaseAuthentication(BaseAuthentication):
    """
    Middleware de autenticación Firebase para DRF.

    Lee el header:  Authorization: Bearer <firebase_id_token>
    Verifica el token con Firebase Admin SDK y devuelve el Usuario local.

    Si no hay header → devuelve (None, None), DRF trata la petición como anónima.
    Si el token es inválido → lanza AuthenticationFailed (401).
    Si el usuario no existe en BD → lanza AuthenticationFailed (401).
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')

        # Si no viene el header simplemente no autenticamos (petición anónima)
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split('Bearer ')[1].strip()

        if not token:
            return None

        if not FIREBASE_DISPONIBLE:
            raise AuthenticationFailed('Firebase no está configurado en el servidor.')

        # Verificar el token con Firebase Admin SDK
        try:
            decoded = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            raise AuthenticationFailed('El token de Firebase ha expirado.')
        except firebase_auth.InvalidIdTokenError:
            raise AuthenticationFailed('Token de Firebase inválido.')
        except Exception:
            raise AuthenticationFailed('No se pudo verificar el token de Firebase.')

        uid = decoded.get('uid')

        # Buscar el usuario local que corresponde a ese UID
        try:
            usuario = Usuario.objects.select_related('rol').get(firebase_uid=uid)
        except Usuario.DoesNotExist:
            raise AuthenticationFailed(
                'Usuario no registrado. Inicia sesión primero en /api/usuarios/login/'
            )

        # DRF espera (user, auth) — el segundo valor queda disponible como request.auth
        return (usuario, token)

    def authenticate_header(self, request):
        """Indica a DRF qué esquema de autenticación usar en el header WWW-Authenticate."""
        return 'Bearer realm="api"'