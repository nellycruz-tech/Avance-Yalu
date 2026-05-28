from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, MarcaViewSet, ProductoViewSet

router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('marcas', MarcaViewSet, basename='marca')
router.register('productos', ProductoViewSet, basename='producto')

urlpatterns = router.urls
