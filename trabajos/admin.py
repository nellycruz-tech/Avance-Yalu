#trabajos/admin.py

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    TrabajoManual,
    TrabajoManualFoto,
    CategoriaTrabajo,
    ContactoWhatsApp,
)


class FotoInline(TabularInline):
    model = TrabajoManualFoto
    extra = 1


@admin.register(CategoriaTrabajo)
class CategoriaTrabajoAdmin(ModelAdmin):
    list_display = ["nombre"]


@admin.register(TrabajoManual)
class TrabajoManualAdmin(ModelAdmin):
    # 1. Agregamos "whatsapp_link" al final de los campos del formulario
    fields = [
        "categoria",
        "titulo",
        "descripcion",
        "whatsapp_contacto",
        "productos_usados",
        "whatsapp_link",  # <-- Lo añadimos aquí
    ]

    # 2. Le decimos a Django que este campo es solo para mirar (así no da error por ser editable=False)
    readonly_fields = ["whatsapp_link"]

    # También lo agregamos al list_display por si quieres ver el link directamente en la tabla principal
    list_display = ["titulo", "categoria", "whatsapp_contacto", "whatsapp_link"]
    list_filter = ["categoria"]
    search_fields = ["titulo", "descripcion"]
    inlines = [FotoInline]
    filter_horizontal = ["productos_usados"]


@admin.register(ContactoWhatsApp)
class ContactoWhatsAppAdmin(ModelAdmin):
    list_display = ["nombre_referencia", "numero"]


@admin.register(TrabajoManualFoto)
class TrabajoManualFotoAdmin(ModelAdmin):
    list_display = ["trabajo", "orden"]
    search_fields = ["trabajo__titulo"]