from django.urls import path
from . import reunion_views
urlpatterns = [
    path('', reunion_views.reuniones_list, name='reuniones_list'),
    path('crear/', reunion_views.reunion_crear, name='reunion_crear'),
    path('<int:pk>/', reunion_views.reunion_detalle, name='reunion_detalle'),
    path('<int:pk>/asistencia/', reunion_views.registrar_asistencia, name='registrar_asistencia'),
    path('<int:pk>/generar-multas/', reunion_views.generar_multas_reunion, name='generar_multas_reunion'),
]
