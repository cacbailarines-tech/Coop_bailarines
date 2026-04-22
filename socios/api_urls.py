from django.urls import path
from . import libreta_views
urlpatterns = [
    path('', libreta_views.api_libretas_disponibles, name='api_libretas_disponibles'),
]
