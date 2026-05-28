from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Comentario(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    texto = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('usuario', 'content_type', 'object_id')  # ← NUEVO


class ComentarioImagen(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='comentarios/')
    created_at = models.DateTimeField(auto_now_add=True)


class Valoracion(models.Model):
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    puntuacion = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('usuario', 'content_type', 'object_id')