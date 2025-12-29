from rest_framework.routers import DefaultRouter
from django.urls import path, include
from tasks.api.views import TaskViewSet

router = DefaultRouter()
router.register('tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include(router.urls)),
]