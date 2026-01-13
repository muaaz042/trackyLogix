from django.contrib import admin
from .models import Zone, Aisle, Rack, Level, Bin, Location

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'warehouse', 
        'zone_type', 
        'allowed_client_type', 
        'min_temp', 
        'max_temp', 
        'hazard_allowed'
    )
    list_filter = ('warehouse', 'zone_type', 'allowed_client_type', 'hazard_allowed')
    search_fields = ('name', 'warehouse__name')

@admin.register(Aisle)
class AisleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zone', 'epc')
    list_filter = ('zone__warehouse', 'zone')
    search_fields = ('name', 'zone__name', 'epc')

@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'aisle', 'rack_type', 'max_weight', 'epc')
    list_filter = ('aisle__zone__warehouse', 'rack_type')
    search_fields = ('name', 'aisle__name', 'epc')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rack', 'max_weight', 'epc')
    list_filter = ('rack__aisle__zone__warehouse',)
    search_fields = ('name', 'rack__name', 'epc')

@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level', 'max_units', 'max_weight', 'epc')
    list_filter = ('level__rack__aisle__zone__warehouse',)
    search_fields = ('name', 'level__name', 'epc')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'location_code', 
        'location_type', 
        'warehouse', 
        'zone', 
        'level', 
        'bin'
    )
    list_filter = ('warehouse', 'location_type', 'zone')
    search_fields = ('location_code', 'warehouse__name')
    readonly_fields = ('location_code',)