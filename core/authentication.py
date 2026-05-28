#core/authentication.py


import firebase_admin
from firebase_admin import auth
from rest_framework import authentication, exceptions
from usuarios.models import Usuario

class FirebaseUser:
    is_authenticated = True
    is_anonymous = False
    def __init__(self, usuario):
        self.usuario = usuario
        self.pk = usuario.pk
        self.id = usuario.pk
    def __str__(self): return str(self.usuario)

class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        h = request.headers.get('Authorization')
        if not h or not h.startswith('Bearer '): return None
        token = h.split(' ', 1)[1]
        try:
            decoded = auth.verify_id_token(token)
            uid = decoded.get('uid')
            # Intentar obtener el usuario
            user = Usuario.objects.get(firebase_uid=uid)
            return (user, token)
        except Exception:
            # retornamos None para que DRF continúe con el siguiente método de autenticación
            # o trate la petición como anónima.
            return None