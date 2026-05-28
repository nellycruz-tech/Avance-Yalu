from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "ok", "message": "API funcionando 🚀"})

urlpatterns = [
    path('', home),

    path('admin/', admin.site.urls),
    path('api/catalogo/', include('catalogo.urls')),
    path('api/usuarios/', include('usuarios.urls')),
    path('api/ventas/', include('ventas.urls')),
    path('api/', include('comentarios.urls')),
    path('api/trabajos/', include('trabajos.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)