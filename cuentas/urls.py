from django.urls import path
from . import views
urlpatterns = [
    path('', views.rifas_list, name='rifas_list'),
    path('crear/', views.rifa_crear, name='rifa_crear'),
    path('<int:pk>/', views.rifa_detalle, name='rifa_detalle'),
]
