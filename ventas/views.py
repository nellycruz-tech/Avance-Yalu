import uuid
import requests as http_requests
from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
from .models import Pedido, PedidoDetalle, Pago, Comprobante
from .serializers import (
    PedidoListSerializer, PedidoDetalladoSerializer,
    CrearPedidoSerializer
)
from usuarios.models import Usuario
from usuarios.authentication import FirebaseAuthentication
from catalogo.models import Producto, ProductoVariante

class PedidoViewSet(ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def get_queryset(self):
        uid = self.request.query_params.get('uid')
        if uid:
            return Pedido.objects.filter(
                usuario__firebase_uid=uid
            ).select_related('usuario').prefetch_related(
                'detalles', 'pago', 'comprobante'
            )
        return Pedido.objects.none()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PedidoDetalladoSerializer
        return PedidoListSerializer

class CrearPedidoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [FirebaseAuthentication]

    @transaction.atomic
    def post(self, request):
        serializer = CrearPedidoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Validamos identidad: el UID debe coincidir con el usuario logueado
        if data['uid'] != request.user.firebase_uid:
            return Response({'error': 'Acceso denegado: UID no coincide con usuario autenticado'}, status=403)

        usuario = request.user
        subtotal = Decimal('0')
        items_validados = []

        for item in data['items']:
            try:
                producto = Producto.objects.get(id=item['producto_id'], activo=True)
            except Producto.DoesNotExist:
                return Response({'error': f"Producto {item['producto_id']} no encontrado"}, status=400)

            variante = None
            precio = producto.precio

            if item.get('variante_id'):
                try:
                    variante = ProductoVariante.objects.get(
                        id=item['variante_id'], producto=producto, activo=True
                    )
                    precio = variante.precio
                    if variante.stock < item['cantidad']:
                        return Response({'error': f"Stock insuficiente"}, status=400)
                    variante.stock -= item['cantidad']
                    variante.save()
                except ProductoVariante.DoesNotExist:
                    return Response({'error': 'Variante no encontrada'}, status=400)

            item_subtotal = precio * item['cantidad']
            subtotal += item_subtotal
            items_validados.append({
                'producto': producto,
                'variante': variante,
                'cantidad': item['cantidad'],
                'precio_unitario': precio,
                'subtotal': item_subtotal,
            })

        descuento = data.get('descuento', Decimal('0'))
        costo_envio = data.get('costo_envio', Decimal('0'))
        total = subtotal - descuento + costo_envio
        codigo = f"YAL-{uuid.uuid4().hex[:8].upper()}"

        pedido = Pedido.objects.create(
            usuario=usuario,
            codigo=codigo,
            estado='pendiente',
            subtotal=subtotal,
            descuento=descuento,
            costo_envio=costo_envio,
            total=total,
            metodo_entrega=data['metodo_entrega'],
            observacion=data.get('observacion', ''),
        )

        for item in items_validados:
            PedidoDetalle.objects.create(pedido=pedido, **item)

        Pago.objects.create(pedido=pedido, metodo_pago='culqi', estado='pendiente', monto=total)
        Comprobante.objects.create(pedido=pedido, tipo=data['tipo_comprobante'], serie='B001', numero=str(pedido.id).zfill(8), estado_sunat='pendiente')

        return Response(PedidoDetalladoSerializer(pedido).data, status=status.HTTP_201_CREATED)

class CrearPedidoInvitadoView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        # Validación básica de datos
        nombre = request.data.get('nombre', '').strip()
        dni = request.data.get('dni', '').strip()
        correo = request.data.get('correo', '').strip()
        items = request.data.get('items',[])

        if not nombre or not dni or not correo or not items:
            return Response({'error': 'Faltan campos requeridos'}, status=400)

        # Cálculo de totales
        subtotal = Decimal('0')
        items_validados =[]

        for item in items:
            try:
                producto = Producto.objects.get(id=item['producto_id'], activo=True)
            except Producto.DoesNotExist:
                return Response({'error': f"Producto {item['producto_id']} no encontrado"}, status=400)

            precio = producto.precio
            if item.get('variante_id'):
                try:
                    variante = ProductoVariante.objects.get(id=item['variante_id'], producto=producto, activo=True)
                    precio = variante.precio
                    variante.stock -= item['cantidad']
                    variante.save()
                except ProductoVariante.DoesNotExist:
                    return Response({'error': 'Variante no encontrada'}, status=400)

            item_subtotal = precio * item['cantidad']
            subtotal += item_subtotal
            items_validados.append({'producto': producto, 'variante': None, 'cantidad': item['cantidad'], 'precio_unitario': precio, 'subtotal': item_subtotal})

        total = subtotal + Decimal(str(request.data.get('costo_envio', '0')))
        codigo = f"YAL-INV-{uuid.uuid4().hex[:8].upper()}"

        pedido = Pedido.objects.create(
            usuario=None,
            cliente_nombre=nombre,
            cliente_dni=dni,
            cliente_correo=correo,
            codigo=codigo,
            subtotal=subtotal,
            total=total,
            metodo_entrega=request.data.get('metodo_entrega', 'courier')
        )

        for item in items_validados:
            PedidoDetalle.objects.create(pedido=pedido, **item)

        Pago.objects.create(pedido=pedido, metodo_pago='culqi', estado='pendiente', monto=total)
        
        return Response({'codigo': pedido.codigo, 'total': str(total)}, status=201)

class ProcesarPagoCulqiView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        pedido_codigo = request.data.get('pedido_codigo')
        token_id = request.data.get('token_id')
        email = request.data.get('email')

        if not all([pedido_codigo, token_id, email]):
            return Response({'error': 'Faltan campos'}, status=400)

        try:
            pedido = Pedido.objects.get(codigo=pedido_codigo)
            monto_centimos = int(pedido.total * 100)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=404)

        culqi_resp = http_requests.post(
            'https://api.culqi.com/v2/charges',
            headers={'Authorization': f'Bearer {settings.CULQI_SECRET_KEY}', 'Content-Type': 'application/json'},
            json={
                'amount': monto_centimos,
                'currency_code': 'PEN',
                'email': email,
                'source_id': token_id,
                'description': f'Pago de pedido {pedido_codigo}',
            }, timeout=15
        )

        culqi_data = culqi_resp.json()
        if culqi_resp.status_code != 201:
            return Response({'error': culqi_data.get('user_message', 'Error en pago')}, status=402)

        pago = Pago.objects.get(pedido=pedido)
        pago.estado = 'aprobado'
        pago.referencia_transaccion = culqi_data.get('id')
        pago.save()
        pedido.estado = 'pagado'
        pedido.save()

        return Response({'success': True}, status=200)

class SincronizarCarritoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pedido_id = request.data.get('pedido_id')
        try:
            usuario = request.user
            pedido = Pedido.objects.get(id=pedido_id, usuario__isnull=True)
            pedido.usuario = usuario
            pedido.save()
            return Response({'status': 'Carrito vinculado exitosamente'})
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado o ya vinculado'}, status=404)

class ProcesarPagoYapeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        pedido_codigo = request.data.get('pedido_codigo')
        voucher = request.FILES.get('voucher')

        if not pedido_codigo or not voucher:
            return Response(
                {'error': 'Faltan campos: pedido_codigo, voucher'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pedido = Pedido.objects.get(codigo=pedido_codigo)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=404)

        pago, _ = Pago.objects.get_or_create(
            pedido=pedido,
            defaults={'metodo_pago': 'yape', 'monto': pedido.total, 'estado': 'pendiente'}
        )
        pago.metodo_pago = 'yape'
        pago.estado = 'pendiente_revision'
        pago.voucher = voucher
        pago.save()

        pedido.estado = 'pendiente'
        pedido.save()

        return Response({
            'success': True,
            'mensaje': 'Voucher recibido. Tu pago está en revisión.'
        }, status=status.HTTP_200_OK)

class ConfirmarPagoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        pedido_codigo = request.data.get('pedido_codigo')

        if not pedido_codigo:
            return Response({'error': 'Falta pedido_codigo'}, status=400)

        try:
            pedido = Pedido.objects.get(codigo=pedido_codigo)
        except Pedido.DoesNotExist:
            return Response({'error': 'Pedido no encontrado'}, status=404)

        try:
            pago = Pago.objects.get(pedido=pedido)
        except Pago.DoesNotExist:
            return Response({'error': 'Pago no encontrado'}, status=404)

        return Response({
            'success': True,
            'status': pago.estado,
            'metodo': pago.metodo_pago,
            'monto': str(pago.monto),
            'pedido_codigo': pedido.codigo,
        }, status=200)