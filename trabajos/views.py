# trabajos/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import TrabajoManual
from .serializers import TrabajoManualSerializer


class TrabajoManualViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/trabajos/          → lista de trabajos para la galería
    GET /api/trabajos/{id}/     → detalle de un trabajo con fotos
    """
    queryset = TrabajoManual.objects.prefetch_related('fotos').order_by('-created_at')
    serializer_class = TrabajoManualSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def relacionados(self, request, pk=None):
        trabajo = self.get_object()
        # Busca trabajos de la misma categoría, excluyendo el actual
        relacionados = TrabajoManual.objects.filter(categoria=trabajo.categoria).exclude(pk=trabajo.id)[:4]
        serializer = TrabajoManualSerializer(relacionados, many=True)
        return Response(serializer.data)

