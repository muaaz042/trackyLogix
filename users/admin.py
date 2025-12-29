from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    ClientProfile,
    Warehouse,
    WarehouseUserManagement,
    Subscription,
)
from .forms import CustomUserCreationForm, CustomUserChangeForm

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The form to use for adding new users
    add_form = CustomUserCreationForm
    # The form to use for editing existing users
    form = CustomUserChangeForm
    model = User

    ordering = ("email",)
    list_display = ("id", "email", "role", "first_name", "last_name", "created_by_user")
    list_filter = ("role", "is_active")
    search_fields = ("email", "first_name", "last_name")

    # Layout for EDITING
    fieldsets = (
        ("Login Info", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        ("Role & Hierarchy", {"fields": ("role", "created_by_user")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "created_at")}),
    )

    # Layout for ADDING (Must match CustomUserCreationForm fields EXACTLY)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password_1", 
                    "password_2",
                    "first_name",
                    "last_name",
                    "role",
                    "created_by_user",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )
    
    readonly_fields = ("created_at", "last_login")

    def save_model(self, request, obj, form, change):
        if not change and not obj.created_by_user:
            obj.created_by_user = request.user
        super().save_model(request, obj, form, change)


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "company_name", "contact_number")
    search_fields = ("user__email", "company_name")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_number", "address")
    search_fields = ("name", "address")


@admin.register(WarehouseUserManagement)
class WarehouseUserManagementAdmin(admin.ModelAdmin):
    list_display = ("id", "warehouse", "user")
    list_filter = ("warehouse", "user__role")
    search_fields = ("warehouse__name", "user__email")
    autocomplete_fields = ["warehouse", "user"] # Easier selection for foreign keys


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "max_warehouses",
        "max_managers_per_warehouse",
        "max_deos_per_warehouse",
        "max_allocators_per_warehouse",
    )
    list_filter = ("id", "user")