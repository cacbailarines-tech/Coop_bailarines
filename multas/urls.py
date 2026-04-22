from django.urls import path
from . import views
urlpatterns = [
    path('', views.multas_list, name='multas_list'),
    path('crear/', views.multa_crear, name='multa_crear'),
    path('<int:pk>/pagar/', views.multa_pagar, name='multa_pagar'),
    path('tipos/', views.tipos_multa_list, name='tipos_multa_list'),
    path('tipos/crear/', views.tipo_multa_crear, name='tipo_multa_crear'),
]
