from django.urls import path
from . import libreta_views
urlpatterns = [
    path('', libreta_views.libretas_list, name='libretas_list'),
    path('crear/', libreta_views.libreta_crear, name='libreta_crear'),
    path('<int:pk>/', libreta_views.libreta_detalle, name='libreta_detalle'),
    path('<int:pk>/aporte/<int:mes>/', libreta_views.aporte_verificar, name='aporte_verificar'),
    path('aportes/', libreta_views.aportes_list, name='aportes_list'),
    path('aportes/<int:pk>/verificar/', libreta_views.aporte_accion, name='aporte_accion'),
]

urlpatterns += [
    path('api/disponibles/', libreta_views.api_libretas_disponibles, name='api_libretas'),
]
