from django.db.models.signals import post_save
from django.dispatch import receiver
from locations.models import Aisle, Rack, Level, Bin, Location, Zone
from locations.services.business_logic import refresh_related_location_codes

# 1. If a BIN is updated (e.g. moved to a new Level)
@receiver(post_save, sender=Bin)
def update_locations_for_bin(sender, instance, **kwargs):
    # Find locations pointing directly to this Bin
    locations = Location.objects.filter(bin=instance)
    refresh_related_location_codes(locations)

# 2. If a LEVEL is updated (e.g. moved to a new Rack)
@receiver(post_save, sender=Level)
def update_locations_for_level(sender, instance, **kwargs):
    # Locations pointing directly to this Level
    locs_via_level = Location.objects.filter(level=instance)
    # Locations pointing to Bins inside this Level
    locs_via_bin = Location.objects.filter(bin__level=instance)
    
    refresh_related_location_codes(locs_via_level | locs_via_bin)

# 3. If a RACK is updated (e.g. moved to a new Aisle)
@receiver(post_save, sender=Rack)
def update_locations_for_rack(sender, instance, **kwargs):
    # Locations via Level -> Rack
    locs_via_level = Location.objects.filter(level__rack=instance)
    # Locations via Bin -> Level -> Rack
    locs_via_bin = Location.objects.filter(bin__level__rack=instance)

    refresh_related_location_codes(locs_via_level | locs_via_bin)

# 4. If an AISLE is updated (e.g. moved to a new Zone)
@receiver(post_save, sender=Aisle)
def update_locations_for_aisle(sender, instance, **kwargs):
    # Locations via Level -> Rack -> Aisle
    locs_via_level = Location.objects.filter(level__rack__aisle=instance)
    # Locations via Bin -> Level -> Rack -> Aisle
    locs_via_bin = Location.objects.filter(bin__level__rack__aisle=instance)

    refresh_related_location_codes(locs_via_level | locs_via_bin)

# 5. If a ZONE is updated
@receiver(post_save, sender=Zone)
def update_locations_for_zone(sender, instance, **kwargs):
    # Locations pointing directly to this Zone
    locs_direct = Location.objects.filter(zone=instance)
    # Locations via hierarchy
    locs_via_level = Location.objects.filter(level__rack__aisle__zone=instance)
    locs_via_bin = Location.objects.filter(bin__level__rack__aisle__zone=instance)

    refresh_related_location_codes(locs_direct | locs_via_level | locs_via_bin)