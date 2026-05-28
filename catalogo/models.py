# catalogo/models.py 

from django.db import models
from django.contrib.postgres.indexes import GinIndex
from core.utils import optimizar_imagen

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"


class Marca(models.Model):
    nombre = models.CharField(max_length=100)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


class Producto(models.Model):
    TIPO_CHOICES = [
        ("producto", "Producto"),
        ("paquete", "Paquete"),
        ("servicio", "Servicio"),
    ]
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo_publicacion = models.CharField(max_length=20, choices=TIPO_CHOICES, default="producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)
    permite_mayor = models.BooleanField(default=False, help_text="Marcar si el producto puede venderse al por mayor (cantidad grande con precio especial)")
    stock_minimo = models.PositiveIntegerField(default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    def stock_total(self):
        return sum(v.stock for v in self.variantes.filter(activo=True))

    def actualizar_estado(self):
        tiene_stock = self.stock_total() > 0
        if self.activo != tiene_stock:
            self.activo = tiene_stock
            self.save(update_fields=["activo"])

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


class ProductoVariante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="variantes")
    nombre_variante = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                  help_text="Si no se especifica, usa el precio del producto")
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    def precio_final(self):
        return self.precio if self.precio is not None else self.producto.precio

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.producto.actualizar_estado()

    def __str__(self):
        return f"{self.producto.nombre} — {self.nombre_variante}"

    class Meta:
        verbose_name = "Variante"
        verbose_name_plural = "Variantes"


class TipoVariante(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="tipos_variante")
    nombre = models.CharField(max_length=100, help_text="Ej: Color, Tamaño, Tipo")
    obligatorio = models.BooleanField(default=False, help_text="¿El cliente debe elegir esta variante?")

    def __str__(self):
        return f"{self.producto.nombre} — {self.nombre}"

    class Meta:
        verbose_name = "Tipo de variante"
        verbose_name_plural = "Tipos de variante"


class OpcionVariante(models.Model):
    tipo = models.ForeignKey(TipoVariante, on_delete=models.CASCADE, related_name="opciones")
    nombre = models.CharField(max_length=100, help_text="Ej: Rojo, A4, Rayado")
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                        help_text="Precio adicional sobre el precio base (0 = sin costo extra)")
    stock = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo.nombre}: {self.nombre}"

    class Meta:
        verbose_name = "Opción de variante"
        verbose_name_plural = "Opciones de variante"


class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(upload_to="productos/")
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # 1. Guardamos primero para obtener un ID válido
        super().save(*args, **kwargs)
        
        # 2. Si no es webp, lanzamos la tarea asíncrona
        if self.imagen and not self.imagen.name.lower().endswith('.webp'):
            from core.utils import optimizar_imagen_async
            optimizar_imagen_async(self.id)

    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        ordering = ["orden"]
        
class TerminoBusqueda(models.Model):
    termino = models.CharField(max_length=200, unique=True)
    contador = models.PositiveIntegerField(default=1)
    ultima_busqueda = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.termino} ({self.contador})"

    class Meta:
        verbose_name = "Término de búsqueda"
        verbose_name_plural = "Términos de búsqueda"
        ordering = ['-contador']
        indexes =[
            GinIndex(fields=['termino'], name='termino_trgm_idx', opclasses=['gin_trgm_ops']),
        ]