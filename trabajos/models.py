#trabajos/models.py

from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto
from urllib.parse import quote

class CategoriaTrabajo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de Trabajo"
        verbose_name_plural = "Categorías de Trabajos"

class ContactoWhatsApp(models.Model):
    nombre_referencia = models.CharField(max_length=50, help_text="Ej: Ventas, Soporte, Reclamos")
    numero = models.CharField(max_length=20)
    
    def __str__(self):
        return f"{self.nombre_referencia} ({self.numero})"

    class Meta:
        verbose_name = "Contacto WhatsApp"
        verbose_name_plural = "Contactos WhatsApp"

class TrabajoManual(models.Model):
    categoria = models.ForeignKey(
        CategoriaTrabajo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="trabajos",
    )
    productos_usados = models.ManyToManyField(
        Producto,
        blank=True,
        help_text="Productos del catálogo usados en este trabajo",
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    whatsapp_contacto = models.ForeignKey(
        ContactoWhatsApp,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Contacto para WhatsApp",
    )

    # Añadimos el campo con más longitud por el texto largo y editable=False para que se gestione solo
    whatsapp_link = models.URLField(max_length=1000, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    # Lógica avanzada para automatizar el link con el mensaje personalizado
    def save(self, *args, **kwargs):
        if self.whatsapp_contacto and self.whatsapp_contacto.numero:
            # 1. Limpiamos el número de espacios, guiones o caracteres raros
            numero_limpio = "".join(
                filter(str.isdigit, self.whatsapp_contacto.numero)
            )

            # 2. Configura aquí tu código de país (51 = Perú)
            codigo_pais = "51"

            # Evitamos duplicar el código de país si ya lo pusieron en el admin
            if not numero_limpio.startswith(codigo_pais):
                telefono_final = f"{codigo_pais}{numero_limpio}"
            else:
                telefono_final = numero_limpio

            # 3. Creamos el texto dinámico usando el título del trabajo actual
            mensaje = f"Hola, estoy interesado en el trabajo: {self.titulo}"

            # 4. Codificamos el texto para que sea seguro en una URL (vuelve los espacios en %20, etc.)
            mensaje_codificado = quote(mensaje)

            # 5. Armamos el enlace final que consumirá tu Front-End
            self.whatsapp_link = (
                f"https://wa.me/{telefono_final}?text={mensaje_codificado}"
            )

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Trabajo Manual"
        verbose_name_plural = "Trabajos Manuales"

class TrabajoManualFoto(models.Model):
    trabajo = models.ForeignKey(TrabajoManual, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="trabajos/")
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Foto {self.orden} de {self.trabajo.titulo}"

    class Meta:
        verbose_name = "Foto de trabajo"
        verbose_name_plural = "Fotos de trabajo"
        ordering = ["orden"]

