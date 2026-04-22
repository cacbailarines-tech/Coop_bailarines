from django.urls import path
from . import views, pdf_views

urlpatterns = [
    path('', views.creditos_list, name='creditos_list'),
    path('crear/', views.credito_crear, name='credito_crear'),
    path('<int:pk>/', views.credito_detalle, name='credito_detalle'),
    path('<int:pk>/aprobar/', views.credito_aprobar, name='credito_aprobar'),
    path('<int:pk>/pago/', views.registrar_pago, name='registrar_pago'),
    path('<int:pk>/verificar-pago/<int:pago_pk>/', views.verificar_pago, name='verificar_pago'),
    path('<int:pk>/multa/agregar/', views.agregar_multa_credito, name='agregar_multa_credito'),
    path('<int:pk>/multa/<int:multa_pk>/editar/', views.editar_multa_credito, name='editar_multa_credito'),
    path('<int:pk>/pdf/', pdf_views.credito_pdf_admin, name='credito_pdf'),
]
