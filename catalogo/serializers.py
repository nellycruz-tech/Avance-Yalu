from rest_framework import serializers
from .models import Categoria, Marca, Producto, ProductoVariante, ImagenProducto


class CategoriaSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()  # ← NUEVO: generado desde nombre

    class Meta:
        model  = Categoria
        fields = ['id', 'nombre', 'slug', 'descripcion', 'activo']

    def get_slug(self, obj):
        # Genera slug limpio desde nombre: "Útiles Escolares" → "utiles-escolares"
        import unicodedata, re
        valor = unicodedata.normalize('NFKD', obj.nombre)
        valor = valor.encode('ascii', 'ignore').decode('ascii')
        valor = valor.lower().strip()
        valor = re.sub(r'[^\w\s-]', '', valor)
        valor = re.sub(r'[\s_]+', '-', valor)
        return valor


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Marca
        fields = ['id', 'nombre', 'activo']


class ImagenProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model  = ImagenProducto
        fields = ['id', 'imagen_url', 'orden', 'es_principal']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return None


class ProductoVarianteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ProductoVariante
        fields = ['id', 'nombre_variante', 'precio', 'stock', 'sku', 'activo']


class ProductoListSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca     = serializers.CharField(source='marca.nombre', read_only=True)
    marca_id  = serializers.IntegerField(source='marca.id',  read_only=True)
    imagen    = serializers.SerializerMethodField()
    imagenes  = ImagenProductoSerializer(many=True, read_only=True)
    stock     = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_publicacion',
            'precio', 'activo', 'permite_mayor', 'stock_minimo',
            'categoria', 'marca', 'marca_id',
            'imagen', 'imagenes', 'stock', 'creado_en',
        ]

    def get_imagen(self, obj):
        request = self.context.get('request')
        img = obj.imagenes.filter(es_principal=True).first() or obj.imagenes.first()
        if img and img.imagen and request:
            return request.build_absolute_uri(img.imagen.url)
        return None

    def get_stock(self, obj):
        if obj.variantes.exists():
            return sum(v.stock for v in obj.variantes.filter(activo=True))
        return obj.stock_minimo if obj.stock_minimo > 0 else 100


class ProductoDetalleSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca     = MarcaSerializer(read_only=True)
    variantes = ProductoVarianteSerializer(many=True, read_only=True)
    imagenes  = ImagenProductoSerializer(many=True, read_only=True)
    stock     = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'tipo_publicacion',
            'precio', 'activo', 'permite_mayor', 'stock_minimo',
            'categoria', 'marca', 'variantes', 'imagenes',
            'stock', 'creado_en',
        ]

    def get_stock(self, obj):
        if obj.variantes.exists():
            return sum(v.stock for v in obj.variantes.filter(activo=True))
        return obj.stock_minimo if obj.stock_minimo > 0 else 100