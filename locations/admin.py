from django.contrib import admin
from .models import Zone, Location, Aisle, Rack, Level, Bin

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'warehouse', 'zone_type')
    list_filter = ('warehouse', 'zone_type')
    search_fields = ('name', 'warehouse__name')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    # Added 'status' to display
    list_display = ('id', 'name', 'zone', 'location_type', 'status', 'min_temp', 'max_temp')
    # Added 'status' to filters
    list_filter = ('zone__warehouse', 'location_type', 'status', 'hazard_allowed')
    search_fields = ('name', 'zone__name')

@admin.register(Aisle)
class AisleAdmin(admin.ModelAdmin):
    # Added 'status' to display
    list_display = ('id', 'name', 'location', 'status', 'epc')
    # Added 'status' to filters
    list_filter = ('status', 'location__zone__warehouse')
    search_fields = ('name', 'epc', 'location__name')

@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'aisle', 'rack_type', 'status')
    list_filter = ('status', 'rack_type')
    search_fields = ('name', 'epc', 'aisle__name')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rack', 'max_weight', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'epc', 'rack__name')

@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level', 'max_units', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'epc', 'level__name')