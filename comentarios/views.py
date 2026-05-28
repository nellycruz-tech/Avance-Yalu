from rest_framework import viewsets, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Comentario, ComentarioImagen, Valoracion
from .serializers import ComentarioSerializer
from core.utils import optimizar_imagen

# 1. Definición del permiso personalizado para que solo el dueño pueda editar/borrar
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.usuario == request.user

class ComentarioViewSet(viewsets.ModelViewSet):
    serializer_class = ComentarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        qs = Comentario.objects.select_related('usuario').prefetch_related('imagenes').all()
        ct = self.request.query_params.get('ct')
        obj = self.request.query_params.get('obj')
        if ct: qs = qs.filter(content_type_id=ct)
        if obj: qs = qs.filter(object_id=obj)
        return qs

    def perform_create(self, serializer):  # ← 4 espacios de indentación
        ct_id = self.request.data.get('content_type')
        obj_id = self.request.data.get('object_id')
        comentario = serializer.save(
            usuario=self.request.user,
            content_type_id=ct_id,
            object_id=obj_id
        )
        for f in self.request.FILES.getlist('imagenes'):
            imagen_optimizada = optimizar_imagen(f)
            ComentarioImagen.objects.create(comentario=comentario, imagen=imagen_optimizada)

        puntuacion = self.request.data.get('puntuacion')
        if puntuacion:
            Valoracion.objects.update_or_create(
                usuario=self.request.user,
                content_type_id=ct_id,
                object_id=obj_id,
                defaults={'puntuacion': int(puntuacion)}
            )