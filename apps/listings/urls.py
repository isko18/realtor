from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet,
    LocationViewSet,
    FavoriteViewSet,
    ApplicationViewSet,
    admin_stats,  # 👈 импортируем функцию статистики
)

router = DefaultRouter()
router.register('listings', ListingViewSet, basename='listings')
router.register('locations', LocationViewSet, basename='locations')
router.register('favorites', FavoriteViewSet, basename='favorites')
router.register('applications', ApplicationViewSet, basename='applications')

urlpatterns = router.urls + [
    path('admin/stats/', admin_stats, name='admin-stats'),  # 👈 добавляем вручную
]
