from django.contrib import admin
from .models import Zone, Location, Aisle, Rack, Level, Bin

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'warehouse', 'zone_type')
    list_filter = ('warehouse', 'zone_type')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'zone', 'location_type', 'min_temp', 'max_temp')
    list_filter = ('zone__warehouse', 'location_type')

@admin.register(Aisle)
class AisleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location', 'epc')

@admin.register(Rack)
class RackAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'aisle', 'rack_type')

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'rack', 'max_weight')

@admin.register(Bin)
class BinAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level', 'max_units')