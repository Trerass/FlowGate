from django.contrib import admin
from .models import Parqueadero, Entrada, PerfilUsuario, Vehiculo, Historial


@admin.register(Parqueadero)
class ParqueaderoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'capacidad', 'ocupancia')
    search_fields = ('nombre',)

@admin.register(Entrada)
class EntradaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'parqueadero', 'fila')
    list_filter = ('parqueadero',)
    search_fields = ('nombre',)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'telefono', 'tipo_usuario')
    list_filter = ('tipo_usuario',)
    search_fields = ('user__username', 'codigo_estudiantil')

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'usuario', 'marca', 'modelo', 'tipo_vehiculo', 'es_electrico', 'precio_diario')
    list_filter = ('tipo_vehiculo', 'es_electrico')
    search_fields = ('placa', 'usuario__user__username')
    readonly_fields = ('precio_diario',)

@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'parqueadero', 'fecha', 'hora_entrada', 'hora_salida', 'costo')
    list_filter = ('parqueadero', 'fecha')
    search_fields = ('usuario__user__username',)
    readonly_fields = ('costo',)
