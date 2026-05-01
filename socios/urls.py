from django.urls import path
from . import views
urlpatterns = [
    path('', views.socios_list, name='socios_list'),
    path('dashboard/', views.dashboard_aportes, name='dashboard_aportes'),
    path('crear/', views.socio_crear, name='socio_crear'),
    path('<int:pk>/', views.socio_detalle, name='socio_detalle'),
    path('<int:pk>/editar/', views.socio_editar, name='socio_editar'),
    path('<int:pk>/acceso/', views.socio_crear_acceso, name='socio_crear_acceso'),
]
