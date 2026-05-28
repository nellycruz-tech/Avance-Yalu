from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import TerminoBusqueda, Categoria, Marca, Producto, ProductoVariante, ImagenProducto, TipoVariante, OpcionVariante


class OpcionVarianteInline(TabularInline):
    model = OpcionVariante
    extra = 1


class TipoVarianteInline(TabularInline):
    model = TipoVariante
    extra = 1
    show_change_link = True


class VarianteInline(TabularInline):
    model = ProductoVariante
    extra = 1


class ImagenInline(TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Marca)
class MarcaAdmin(ModelAdmin):
    list_display = ["nombre", "activo"]
    list_filter = ["activo"]
    search_fields = ["nombre"]


@admin.register(Producto)
class ProductoAdmin(ModelAdmin):
    list_display = ["nombre", "categoria", "marca", "precio", "tipo_publicacion", "activo", "permite_mayor"]
    list_filter = ["categoria", "marca", "activo", "tipo_publicacion"]
    search_fields = ["nombre", "descripcion"]
    readonly_fields = ["activo"]
    inlines = [VarianteInline, TipoVarianteInline, ImagenInline]


@admin.register(TipoVariante)
class TipoVarianteAdmin(ModelAdmin):
    list_display = ["producto", "nombre", "obligatorio"]
    inlines = [OpcionVarianteInline]

@admin.register(TerminoBusqueda)
class TerminoBusquedaAdmin(admin.ModelAdmin):
    list_display = ('termino', 'contador', 'ultima_busqueda')
    search_fields = ('termino',)