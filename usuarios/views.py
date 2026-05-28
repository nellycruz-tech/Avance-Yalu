from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers, status
from .models import Rol, Usuario, Direccion
from .serializers import UsuarioSerializer, DireccionSerializer, FirebaseLoginSerializer
from .authentication import FirebaseAuthentication

try:
    import firebase_admin
    from firebase_admin import auth as firebase_auth
    FIREBASE_DISPONIBLE = True
except ImportError:
    FIREBASE_DISPONIBLE = False


class FirebaseLoginView(APIView):
    """
    POST /api/usuarios/login/

    Único endpoint público. Recibe el Firebase ID Token, lo verifica,
    y crea o recupera el usuario local. No requiere autenticación previa.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = FirebaseLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        token = serializer.validated_data['firebase_token']

        if not FIREBASE_DISPONIBLE:
            return Response(
                {'error': 'Firebase no configurado en el servidor'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        try:
            decoded = firebase_auth.verify_id_token(token)
        except firebase_auth.ExpiredIdTokenError:
            return Response(
                {'error': 'El token ha expirado. Vuelve a iniciar sesión.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception:
            return Response(
                {'error': 'Token inválido o expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        uid = decoded.get('uid')
        email = decoded.get('email', '')
        nombre = decoded.get('name', '')
        partes = nombre.split(' ', 1)
        nombres = partes[0] if partes else ''
        apellidos = partes[1] if len(partes) > 1 else ''

        rol_cliente, _ = Rol.objects.get_or_create(nombre='cliente')

        usuario, creado = Usuario.objects.get_or_create(
            firebase_uid=uid,
            defaults={
                'email': email,
                'nombres': nombres,
                'apellidos': apellidos,
                'rol': rol_cliente,
            }
        )

        return Response({
            'usuario': UsuarioSerializer(usuario).data,
            'creado': creado
        }, status=status.HTTP_200_OK)


class PerfilView(APIView):
    """
    GET  /api/usuarios/perfil/   → devuelve el perfil del usuario autenticado
    PATCH /api/usuarios/perfil/  → actualiza datos permitidos del usuario autenticado

    Requiere: Authorization: Bearer <firebase_id_token>
    El UID ya no se pasa por query param — se extrae del token verificado.
    """
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user es el objeto Usuario resuelto por FirebaseAuthentication
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        # Filtramos explícitamente los campos que el usuario puede editar
        datos_permitidos = {
            key: request.data[key]
            for key in ('nombres', 'apellidos', 'alias', 'telefono')
            if key in request.data
        }

        serializer = UsuarioSerializer(request.user, data=datos_permitidos, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DireccionViewSet(ModelViewSet):
    """
    CRUD de direcciones del usuario autenticado.

    GET    /api/usuarios/direcciones/        → lista sus direcciones
    POST   /api/usuarios/direcciones/        → crea una nueva dirección
    GET    /api/usuarios/direcciones/<id>/   → detalle de una dirección
    PATCH  /api/usuarios/direcciones/<id>/   → edita una dirección
    DELETE /api/usuarios/direcciones/<id>/   → elimina una dirección

    Requiere: Authorization: Bearer <firebase_id_token>
    """
    serializer_class = DireccionSerializer
    authentication_classes = [FirebaseAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Solo devuelve las direcciones del usuario que hace la petición
        return Direccion.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Asocia la nueva dirección al usuario autenticado automáticamente
        serializer.save(usuario=self.request.user)