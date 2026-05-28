from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    PedidoViewSet,
    CrearPedidoView,
    CrearPedidoInvitadoView,
    ProcesarPagoCulqiView,
    ProcesarPagoYapeView,
    ConfirmarPagoView,
)

router = DefaultRouter()
router.register('pedidos', PedidoViewSet, basename='pedido')

urlpatterns = [
    path('pedidos/crear/', CrearPedidoView.as_view(), name='crear-pedido'),
    path('pedidos/crear-invitado/', CrearPedidoInvitadoView.as_view(), name='crear-pedido-invitado'),
    path('pagos/procesar/', ProcesarPagoCulqiView.as_view(), name='procesar-pago-culqi'),
    path('pagos/yape/', ProcesarPagoYapeView.as_view(), name='procesar-pago-yape'),
    path('pagos/confirmar/', ConfirmarPagoView.as_view(), name='confirmar-pago'),
] + router.urls