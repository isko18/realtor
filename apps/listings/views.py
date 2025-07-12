from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Listing, Location, Favorite, Application
from .serializers import (
    ListingSerializer,
    LocationSerializer,
    FavoriteSerializer,
    ApplicationSerializer,
)
from apps.users.models import User


# ─── Права ─────────────────────────────────────────────────────
class IsRealtor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'realtor'

class IsAdminOrRealtor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['realtor', 'admin'] or request.user.is_staff
        )


# ─── Локации ───────────────────────────────────────────────────
class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]


# ─── Объявления ────────────────────────────────────────────────
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'location__city': ['exact'],
        'location__district': ['exact'],
        'deal_type': ['exact'],
        'price': ['gte', 'lte'],
        'rooms': ['exact'],
        'area': ['gte', 'lte'],
    }
    search_fields = ['title', 'description', 'address']
    ordering_fields = ['price', 'created_at', 'area']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_listings']:
            return [permissions.IsAuthenticated(), IsRealtor()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return Listing.objects.all()
        return Listing.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        listing = self.get_object()
        listing.is_active = False
        listing.save()
        return Response(status=204)

    @action(detail=False, methods=['get'], permission_classes=[IsRealtor])
    def my_listings(self, request):
        listings = Listing.objects.filter(owner=request.user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


# ─── Избранное ─────────────────────────────────────────────────
class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── Заявки ────────────────────────────────────────────────────
class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'realtor':
            return Application.objects.filter(listing__owner=user)
        return Application.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_applications(self, request):
        apps = Application.objects.filter(user=request.user)
        serializer = self.get_serializer(apps, many=True)
        return Response(serializer.data)


# ─── Статистика администратора ─────────────────────────────────
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_stats(request):
    week_ago = timezone.now() - timedelta(days=7)
    data = {
        'users': {
            'total': User.objects.count(),
            'realtors': User.objects.filter(role='realtor').count(),
            'admins': User.objects.filter(role='admin').count(),
        },
        'listings': {
            'total': Listing.objects.count(),
            'active': Listing.objects.filter(is_active=True).count(),
            'inactive': Listing.objects.filter(is_active=False).count(),
        },
        'applications_last_7_days': Application.objects.filter(created_at__gte=week_ago).count()
    }
    return Response(data)
