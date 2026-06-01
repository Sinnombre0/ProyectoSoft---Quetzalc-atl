from django.contrib import admin
from .models import Parque, Reservacion

# Configuración de textos globales del Panel de Control
admin.site.site_header = "Panel de Control Softbear"        
admin.site.site_title = "Softbear Admin"                  
admin.site.index_title = "Gestión del Festival de Luciérnagas"  

@admin.register(Parque)
class ParqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'horario', 'tiene_cabanas', 'capacidad_cabanas', 'capacidad_camping')
    list_filter = ('tiene_cabanas', 'horario')
    search_fields = ('nombre', 'direccion', 'servicios')
    
    def get_fieldsets(self, request, obj=None):
    
        campos_modelo = [f.name for f in Parque._meta.get_fields()]
        
        if 'latitud' in campos_modelo and 'longitud' in campos_modelo:
            coordenadas = ('latitud', 'longitud')
        else:
            coordenadas = ('x', 'y')

        return (
            ('Información General del Parque', {
                'fields': ('nombre', 'direccion', 'horario', 'servicios'),
                'classes': ('wide',), 
            }),
            ('Capacidades de Hospedaje', {
                'fields': ('tiene_cabanas', 'capacidad_cabanas', 'capacidad_camping'),
                'description': 'Define las limitantes físicas para campamentos o cabañas disponibles.',
            }),
            ('Coordenadas de Interfaz (Mapa)', {
                'fields': coordenadas,
                'description': 'Ubicación del pin luminoso dentro de la interfaz web.',
            }),
        )

@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'parque', 'fecha_inicio', 'fecha_termino', 'num_personas', 'tipo_visita', 'estado')
    list_filter = ('estado', 'tipo_visita', 'fecha_inicio', 'parque')
    search_fields = ('usuario__email', 'usuario__first_name', 'parque__nombre')
    raw_id_fields = ('usuario',)
    ordering = ('-fecha_inicio',)
    actions = ['marcar_como_canceladas', 'marcar_como_activas']

    @admin.action(description='🔴 Cambiar estado de seleccionadas a CANCELADA')
    def marcar_como_canceladas(self, request, queryset):
        cantidad = queryset.update(estado='CANCELADA')
        self.message_user(request, f'Se actualizaron exitosamente {cantidad} reservación(es) a CANCELADA.')

    @admin.action(description='🟢 Cambiar estado de seleccionadas a ACTIVA')
    def marcar_como_activas(self, request, queryset):
        cantidad = queryset.update(estado='ACTIVA')
        self.message_user(request, f'Se restauraron exitosamente {cantidad} reservación(es) a ACTIVA.')