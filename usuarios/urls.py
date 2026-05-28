# usuarios/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import FirebaseLoginView, PerfilView, DireccionViewSet

router = DefaultRouter()
router.register('direcciones', DireccionViewSet, basename='direccion')

urlpatterns = [
    path('login/', FirebaseLoginView.as_view(), name='firebase-login'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
] + router.urls