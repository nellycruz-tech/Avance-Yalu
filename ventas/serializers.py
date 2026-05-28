from rest_framework import serializers
from .models import Pedido, PedidoDetalle, Pago, Comprobante
from catalogo.serializers import ProductoListSerializer, ProductoVarianteSerializer


class PedidoDetalleSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    variante_nombre = serializers.CharField(source='variante.nombre_variante', read_only=True)

    class Meta:
        model = PedidoDetalle
        fields = [
            'id', 'producto', 'producto_nombre',
            'variante', 'variante_nombre',
            'cantidad', 'precio_unitario', 'subtotal'
        ]


class CrearPedidoDetalleSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    variante_id = serializers.IntegerField(required=False, allow_null=True)
    cantidad = serializers.IntegerField(min_value=1)


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'metodo_pago', 'estado', 'monto', 'referencia_transaccion', 'created_at']


class ComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = ['id', 'tipo', 'serie', 'numero', 'estado_sunat', 'emitido_en']


class PedidoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = [
            'id', 'codigo', 'estado', 'total',
            'metodo_entrega', 'fecha'
        ]


class PedidoDetalladoSerializer(serializers.ModelSerializer):
    detalles = PedidoDetalleSerializer(many=True, read_only=True)
    pago = PagoSerializer(read_only=True)
    comprobante = ComprobanteSerializer(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'codigo', 'estado',
            'subtotal', 'descuento', 'costo_envio', 'total',
            'metodo_entrega', 'observacion', 'fecha',
            'detalles', 'pago', 'comprobante'
        ]


class CrearPedidoSerializer(serializers.Serializer):
    uid = serializers.CharField()
    metodo_entrega = serializers.ChoiceField(choices=['recojo', 'delivery', 'courier'])
    observacion = serializers.CharField(required=False, allow_blank=True)
    costo_envio = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    tipo_comprobante = serializers.ChoiceField(choices=['boleta', 'factura'])
    items = CrearPedidoDetalleSerializer(many=True)
