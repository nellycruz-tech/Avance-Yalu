# trabajos/serializers.py

from rest_framework import serializers
from catalogo.models import Producto  # <--- Importamos tus productos
from .models import TrabajoManual, TrabajoManualFoto


class TrabajoFotoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = TrabajoManualFoto
        fields = ['id', 'imagen_url', 'orden']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class ProductoResumidoSerializer(serializers.ModelSerializer):
    # Si quieres enviar el link directamente, puedes calcularlo:
    url = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'url']

    def get_url(self, obj):
        # Ajusta esto a la estructura de tu URL en el frontend
        return f"/producto/{obj.id}"

class TrabajoManualSerializer(serializers.ModelSerializer):
    fotos = TrabajoFotoSerializer(many=True, read_only=True)
    productos_usados = ProductoResumidoSerializer(many=True, read_only=True)  # <--- Nuevo: Serializer anidado

    class Meta:
        model = TrabajoManual
        fields = [
            'id', 
            'titulo', 
            'descripcion', 
            'categoria',       # <--- Añadido para que el frontend reciba el ID de la categoría
            'whatsapp_link', 
            'fotos', 
            'productos_usados', # <--- Añadido para listar los productos detallados
            'created_at'
        ]

