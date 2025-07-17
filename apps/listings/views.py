from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta

from .models import Listing, Location, Application, ListingLike
from .serializers import ListingSerializer, LocationSerializer, ApplicationSerializer
from apps.users.models import User


# ─── Права ───────────────────────────────────────────────
class IsRealtor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'realtor'


class IsAdminOrRealtor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role in ['realtor', 'admin'] or request.user.is_staff
        )


# ─── Локации ──────────────────────────────────────────────
class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]
    
class LocationCreateView(generics.CreateAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.IsAuthenticated]

# ─── Объявления ───────────────────────────────────────────
class ListingListCreateView(generics.ListCreateAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
    ordering_fields = ['price', 'created_at', 'area', 'likes_count']

    def get_queryset(self):
        qs = Listing.objects.annotate(likes_count=Count('likes'))
        if self.request.user.is_authenticated and self.request.user.role == 'admin':
            return qs
        return qs.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def get_queryset(self):
        return Listing.objects.annotate(likes_count=Count('likes'))


class MyListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.IsAuthenticated, IsRealtor]

    def get_queryset(self):
        return Listing.objects.filter(owner=self.request.user).annotate(likes_count=Count('likes'))


class ListingLikeToggleView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        ip = self.get_client_ip(request)
        like, created = ListingLike.objects.get_or_create(listing=listing, ip_address=ip)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        count = ListingLike.objects.filter(listing=listing).count()
        return Response({'liked': liked, 'likes_count': count}, status=200)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


# ─── Заявки ───────────────────────────────────────────────
class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role in ['realtor', 'admin']:
                return Application.objects.filter(listing__owner=user)
            return Application.objects.filter(user=user)
        return Application.objects.none()

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)


class MyApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


# ─── Статистика администратора ───────────────────────────
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
