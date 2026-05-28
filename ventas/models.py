from django.db import models
from usuarios.models import Usuario
from catalogo.models import Producto, ProductoVariante


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pagado", "Pagado"),
        ("en_preparacion", "En preparación"),
        ("enviado", "Enviado"),
        ("entregado", "Entregado"),
        ("cancelado", "Cancelado"),
    ]
    ENTREGA_CHOICES = [
        ("recojo", "Recojo en tienda"),
        ("delivery", "Delivery propio"),
        ("courier", "Courier"),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, null=True, blank=True)
    cliente_nombre = models.CharField(max_length=150, blank=True)
    cliente_dni = models.CharField(max_length=8, blank=True)
    cliente_correo = models.EmailField(blank=True)
    codigo = models.CharField(max_length=20, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_entrega = models.CharField(max_length=20, choices=ENTREGA_CHOICES)
    observacion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.codigo} — {self.usuario}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-fecha"]


class PedidoDetalle(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    variante = models.ForeignKey(ProductoVariante, on_delete=models.PROTECT, null=True, blank=True)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"


class Pago(models.Model):
    METODO_CHOICES = [
        ("yape", "Yape"),
        ("plin", "Plin"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
        ("culqi", "Culqi"),
    ]
    ESTADO_CHOICES = [
        ("pendiente", "Pendiente"),
        ("pendiente_revision", "Pendiente revisión"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    ]
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    referencia_transaccion = models.CharField(max_length=200, blank=True)
    voucher = models.ImageField(upload_to="vouchers/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pago de {self.pedido.codigo}"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"


class Comprobante(models.Model):
    TIPO_CHOICES = [
        ("boleta", "Boleta"),
        ("factura", "Factura"),
    ]
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    serie = models.CharField(max_length=10)
    numero = models.CharField(max_length=20)
    estado_sunat = models.CharField(max_length=50, blank=True)
    emitido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo.upper()} {self.serie}-{self.numero}"

    class Meta:
        verbose_name = "Comprobante"
        verbose_name_plural = "Comprobantes"