#catalogo/views.py

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as df_filters
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity  # ← FIX: import faltante

from .models import Categoria, Marca, Producto, TerminoBusqueda
from .serializers import (
    CategoriaSerializer, MarcaSerializer,
    ProductoListSerializer, ProductoDetalleSerializer
)


class ProductoFilter(df_filters.FilterSet):
    categoria  = df_filters.CharFilter(field_name='categoria__nombre', lookup_expr='iexact')
    marca      = df_filters.CharFilter(field_name='marca__nombre',     lookup_expr='iexact')
    precio_min = df_filters.NumberFilter(field_name='precio', lookup_expr='gte')  # ← NUEVO
    precio_max = df_filters.NumberFilter(field_name='precio', lookup_expr='lte')  # ← NUEVO

    class Meta:
        model  = Producto
        fields = ['categoria', 'marca', 'tipo_publicacion', 'activo', 'precio_min', 'precio_max']


class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Categoria.objects.filter(activo=True)
    serializer_class   = CategoriaSerializer
    permission_classes = [AllowAny]


class MarcaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Marca.objects.filter(activo=True)
    serializer_class   = MarcaSerializer
    permission_classes = [AllowAny]


class ProductoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class    = ProductoFilter
    search_fields      = ['nombre', 'descripcion']
    ordering_fields    = ['precio', 'creado_en', 'nombre']
    ordering           = ['nombre']

    def get_queryset(self):
        return Producto.objects.filter(activo=True).select_related(
            'categoria', 'marca'
        ).prefetch_related('variantes', 'imagenes')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductoDetalleSerializer
        return ProductoListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        termino = request.query_params.get('search', '').strip().lower()

        if len(termino) >= 3 and not termino.startswith('sugerencias_'):
            coincidencias = Producto.objects.filter(
                Q(nombre__icontains=termino) | Q(descripcion__icontains=termino)
            ).exists()

            if coincidencias:
                obj, created = TerminoBusqueda.objects.get_or_create(termino=termino)
                if not created:
                    obj.contador += 1
                    obj.save()

        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def sugerencias_populares(self, request):
        populares = TerminoBusqueda.objects.all().order_by('-contador')[:5]
        return Response([p.termino for p in populares])

    @action(detail=False, methods=['get'])
    def sugerir_busquedas(self, request):
        query = request.query_params.get('q', '').strip().lower()
        if len(query) < 2:
            return Response([])

        sugerencias = TerminoBusqueda.objects.annotate(
            similarity=TrigramSimilarity('termino', query)  # ← ahora funciona
        ).filter(similarity__gt=0.2).order_by('-similarity', '-contador')[:5]

        return Response([s.termino for s in sugerencias])