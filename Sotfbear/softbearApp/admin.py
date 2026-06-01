from django.contrib import admin
from .models import Parque, Reservacion


admin.site.site_header = "Panel de Control Softbear"       
admin.site.site_title = "Softbear Admin"                 
admin.site.index_title = "Gestión del Festival de Luciérnagas" 


@admin.register(Parque)
class ParqueAdmin(admin.ModelAdmin):
    # Columnas organizadas en la tabla principal de parques
    list_display = ('id', 'nombre', 'direccion', 'horario', 'tiene_cabanas', 'capacidad_cabanas', 'capacidad_camping')
    
    # Filtros laterales 
    list_filter = ('tiene_cabanas', 'horario')
    
    # Barra de búsqueda superior
    search_fields = ('nombre', 'direccion', 'servicios')
    
    # Estructuración visual del formulario interno usando bloques 
    fieldsets = (
        ('Información General del Parque', {
            'fields': ('nombre', 'direccion', 'horario', 'servicios'),
            'classes': ('wide',), # Clase CSS nativa de Django para usar todo el ancho
        }),
        ('Capacidades de Hospedaje', {
            'fields': ('tiene_cabanas', 'capacidad_cabanas', 'capacidad_camping'),
            'description': 'Define las limitantes físicas para campamentos o cabañas disponibles.',
        }),
        ('Coordenadas de Interfaz (Mapa)', {
            'fields': ('latitud', 'longitud'),
            'description': 'Porcentajes de ubicación (0-100) del pin luminoso dentro de la interfaz web.',
        }),
    )


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    # Visualización del estado financiero y logístico de las reservaciones
    list_display = ('id', 'usuario', 'parque', 'fecha_inicio', 'fecha_termino', 'num_personas', 'tipo_visita', 'estado')
    
    # Filtros laterales para auditorías 
    list_filter = ('estado', 'tipo_visita', 'fecha_inicio', 'parque')
    
    # Buscador  que vincula relaciones ForeignKey
    search_fields = ('usuario__email', 'usuario__first_name', 'parque__nombre')
    
    # Muestra un widget interactivo de búsqueda para no saturar el servidor con miles de usuarios
    raw_id_fields = ('usuario',)
    
    # Ordenación
    ordering = ('-fecha_inicio',)
    
    # Acciones masivas de administración 
    actions = ['marcar_como_canceladas', 'marcar_como_activas']

    @admin.action(description='🔴 Cambiar estado de seleccionadas a CANCELADA')
    def marcar_como_canceladas(self, request, queryset):
        cantidad = queryset.update(estado='CANCELADA')
        self.message_user(request, f'Se actualizaron exitosamente {cantidad} reservación(es) a CANCELADA.')

    @admin.action(description='🟢 Cambiar estado de seleccionadas a ACTIVA')
    def marcar_como_activas(self, request, queryset):
        cantidad = queryset.update(estado='ACTIVA')
        self.message_user(request, f'Se restauraron exitosamente {cantidad} reservación(es) a ACTIVA.')