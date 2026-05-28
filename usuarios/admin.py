from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Rol, Usuario, Direccion


class DireccionInline(TabularInline):
    model = Direccion
    extra = 0


@admin.register(Rol)
class RolAdmin(ModelAdmin):
    list_display = ["nombre", "descripcion"]


@admin.register(Usuario)
class UsuarioAdmin(ModelAdmin):
    list_display = ["nombres", "apellidos", "email", "rol", "estado", "created_at"]
    list_filter = ["rol", "estado"]
    search_fields = ["nombres", "apellidos", "email"]
    inlines = [DireccionInline]


@admin.register(Direccion)
class DireccionAdmin(ModelAdmin):
    list_display = ["usuario", "distrito", "provincia", "es_principal"]
    list_filter = ["es_principal"]
    search_fields = ["usuario__nombres", "distrito"]