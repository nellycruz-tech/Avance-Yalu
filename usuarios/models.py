from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"


class Usuario(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    nombres = models.CharField(max_length=100)
    alias = models.CharField(max_length=50, blank=True, null=True)  # <-- NUEVO
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT)
    estado = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    # --- PROPIEDADES PARA COMPATIBILIDAD CON DRF ---
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Direccion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="direcciones")
    departamento = models.CharField(max_length=100)
    provincia = models.CharField(max_length=100)
    distrito = models.CharField(max_length=100)
    direccion_detallada = models.TextField()
    referencia = models.TextField(blank=True)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.distrito} - {self.direccion_detallada[:40]}"

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"
