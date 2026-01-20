from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "superadmin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("superadmin", "Super Admin"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("DEO", "DEO"),
        ("Allocator", "Allocator"),
        ("client", "Client"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_by_user = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return f"{self.email} ({self.role})"


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)


class Warehouse(models.Model):
    # Basic Info
    name = models.CharField(max_length=255)
    warehouse_code = models.CharField(max_length=50, unique=True, null=True, blank=True, help_text="Unique identifier for the warehouse")
    
    # Location
    address = models.TextField()
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    # Contact
    contact_number = models.CharField(max_length=20)
    
    # Capacity Specifications
    storage_capacity_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total storage area in sq ft")
    pallet_capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of pallets")
    bin_capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of small item bins")
    
    # Operational Details
    # e.g., "Mon-Fri" or "All Days"
    working_days = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., Mon-Fri")
    shift_start_time = models.TimeField(null=True, blank=True)
    shift_end_time = models.TimeField(null=True, blank=True)
    
    # Compliance & Legal
    fire_certificate_no = models.CharField(max_length=100, null=True, blank=True)
    insurance_policy_no = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.warehouse_code or 'No Code'})"


class WarehouseUserManagement(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("warehouse", "user")


class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    max_warehouses = models.PositiveIntegerField(default=1)
    max_managers_per_warehouse = models.PositiveIntegerField(default=1)
    max_deos_per_warehouse = models.PositiveIntegerField(default=2)
    max_allocators_per_warehouse = models.PositiveIntegerField(default=2)