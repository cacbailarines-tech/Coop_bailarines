from django.contrib import admin
from .models import RifaMensual
@admin.register(RifaMensual)
class RifaMensualAdmin(admin.ModelAdmin):
    list_display = ['periodo','mes','anio','libreta_ganadora','estado']
