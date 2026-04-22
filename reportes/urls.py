from django.urls import path
from . import views
urlpatterns = [
    path('', views.reportes_index, name='reportes_index'),
    path('cartera/', views.reporte_cartera, name='reporte_cartera'),
    path('morosidad/', views.reporte_morosidad, name='reporte_morosidad'),
    path('ahorros/', views.reporte_ahorros, name='reporte_ahorros'),
    path('multas/', views.reporte_multas, name='reporte_multas'),
    path('aportes/', views.reporte_aportes, name='reporte_aportes'),
    path('exportar/socios/', views.exportar_socios, name='exportar_socios'),
    path('exportar/creditos/', views.exportar_creditos, name='exportar_creditos'),
    path('exportar/multas/', views.exportar_multas, name='exportar_multas'),
    path('movimientos/', views.reporte_movimientos, name='reporte_movimientos'),
    path('exportar/movimientos/', views.exportar_movimientos, name='exportar_movimientos'),
    path('general/', views.reporte_general, name='reporte_general'),
    path('exportar/general/', views.exportar_general_excel, name='exportar_general'),
]
