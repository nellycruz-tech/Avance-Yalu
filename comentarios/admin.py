from django.contrib import admin
from .models import Comentario, ComentarioImagen, Valoracion

class ComentarioImagenInline(admin.TabularInline):
    model = ComentarioImagen
    extra = 1

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'content_object', 'created_at', 'texto_corto')
    list_filter = ('content_type', 'created_at')
    search_fields = ('usuario__username', 'texto')
    inlines = [ComentarioImagenInline]
    
    def texto_corto(self, obj):
        return obj.texto[:50] + "..." if len(obj.texto) > 50 else obj.texto

@admin.register(Valoracion)
class ValoracionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntuacion', 'content_object')
    list_filter = ('puntuacion', 'content_type')