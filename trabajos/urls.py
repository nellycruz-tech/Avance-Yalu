# trabajos/urls.py
from rest_framework.routers import DefaultRouter
from .views import TrabajoManualViewSet

router = DefaultRouter()
router.register('', TrabajoManualViewSet, basename='trabajo')

urlpatterns = router.urls
