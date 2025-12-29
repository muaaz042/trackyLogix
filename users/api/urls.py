from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    UserViewSet,
    WarehouseViewSet,
    WarehouseUserManagementViewSet,
    ClientProfileViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("warehouses", WarehouseViewSet, basename="warehouses")
router.register("warehouse-users", WarehouseUserManagementViewSet, basename="warehouse-users")
router.register("client-profile", ClientProfileViewSet, basename="client-profile")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("", include(router.urls)),
]
