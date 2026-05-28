from rest_framework import serializers
from .models import Comentario, ComentarioImagen, Valoracion

class ComentarioImagenSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ComentarioImagen
        fields = ['id', 'imagen_url']
        
    def get_imagen_url(self, obj):
        req = self.context.get('request')
        return req.build_absolute_uri(obj.imagen.url) if req and obj.imagen else None


class ComentarioSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    usuario_ubicacion = serializers.SerializerMethodField()
    puntuacion = serializers.SerializerMethodField()
    usuario_id = serializers.IntegerField(source='usuario.id', read_only=True)  # ← NUEVO
    imagenes = ComentarioImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Comentario
        fields = ['id', 'texto', 'created_at', 'object_id', 'content_type',
                  'usuario_nombre', 'usuario_ubicacion', 'usuario_id', 'puntuacion', 'imagenes']
        read_only_fields = ['id', 'created_at', 'content_type', 'object_id']
        
    def get_usuario_nombre(self, obj):
        return obj.usuario.alias or obj.usuario.nombres

    def get_usuario_ubicacion(self, obj):
        d = obj.usuario.direcciones.filter(es_principal=True).first() or obj.usuario.direcciones.first()
        return d.departamento if d else None

    def get_puntuacion(self, obj):
        v = Valoracion.objects.filter(usuario=obj.usuario, content_type=obj.content_type, object_id=obj.object_id).first()
        return v.puntuacion if v else 0