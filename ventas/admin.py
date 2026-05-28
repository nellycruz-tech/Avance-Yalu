from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Pedido, PedidoDetalle, Pago, Comprobante


class DetalleInline(TabularInline):
    model = PedidoDetalle
    extra = 0
    readonly_fields = ["subtotal"]


@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):
    list_display = ["codigo", "usuario", "estado", "total", "metodo_entrega", "fecha"]
    list_filter = ["estado", "metodo_entrega"]
    search_fields = ["codigo", "usuario__nombres", "usuario__email"]
    inlines = [DetalleInline]
    readonly_fields = ["fecha"]


@admin.register(Pago)
class PagoAdmin(ModelAdmin):
    list_display = ["pedido", "metodo_pago", "estado", "monto", "created_at"]
    list_filter = ["metodo_pago", "estado"]
    search_fields = ["pedido__codigo"]


@admin.register(Comprobante)
class ComprobanteAdmin(ModelAdmin):
    list_display = ["tipo", "serie", "numero", "pedido", "emitido_en"]
    list_filter = ["tipo"]
    search_fields = ["serie", "numero", "pedido__codigo"]