from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('socios/', include('socios.urls')),
    path('libretas/', include('socios.libreta_urls')),
    path('creditos/', include('creditos.urls')),
    path('multas/', include('multas.urls')),
    path('reuniones/', include('multas.reunion_urls')),
    path('reportes/', include('reportes.urls')),
    path('portal/', include('socios.portal_urls')),
    path('api/libretas-disponibles/', include('socios.api_urls')),
    path('rifas/', include('cuentas.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
