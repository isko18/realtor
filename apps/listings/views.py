from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import AllowAny


from .models import Listing, Location, Application, SingleImage, TextMessage, ListingImage
from .serializers import ListingSerializer, LocationSerializer, ApplicationSerializer, SingleImageSerializer, TextMessageSerializer
from apps.users.models import User

from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import AllowAny

from .models import Listing, Location, Application, SingleImage, TextMessage
from .serializers import ListingSerializer, LocationSerializer, ApplicationSerializer, SingleImageSerializer, TextMessageSerializer
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

class LocationDeleteView(generics.DestroyAPIView):
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
            if self.request.user.is_authenticated and self.request.user.role == 'admin':
                return Listing.objects.all()
            return Listing.objects.filter(is_active=True)

        def perform_create(self, serializer):
            serializer.save(owner=self.request.user)

        def put(self, request, *args, **kwargs):
            data = request.data
            if not isinstance(data, list):
                return Response({"detail": "Ожидается список объектов"}, status=status.HTTP_400_BAD_REQUEST)
            updated_count = 0
            for item in data:
                try:
                    instance = Listing.objects.get(pk=item.get('id'))
                    serializer = self.get_serializer(instance, data=item, partial=True)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    updated_count += 1
                except Listing.DoesNotExist:
                    continue
            return Response({"message": f"Обновлено {updated_count} объявлений"}, status=status.HTTP_200_OK)


class ListingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
        queryset = Listing.objects.all()
        serializer_class = ListingSerializer
        permission_classes = [permissions.IsAuthenticatedOrReadOnly]

        def perform_destroy(self, instance):
            instance.is_active = False
            instance.save()

class MyListingsView(generics.ListAPIView):
        serializer_class = ListingSerializer
        permission_classes = [permissions.IsAuthenticated, IsRealtor]

        def get_queryset(self):
            return Listing.objects.filter(owner=self.request.user)
        
# ─── Лайки ───────────────────────────────────────────────
class ListingLikeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        listing.likes_count += 1
        listing.save()
        return Response({"likes_count": listing.likes_count}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            listing = Listing.objects.get(pk=pk)
        except Listing.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if listing.likes_count > 0:
            listing.likes_count -= 1
            listing.save()
        return Response({"likes_count": listing.likes_count}, status=status.HTTP_200_OK)

# ─── Заявки ───────────────────────────────────────────────
class ApplicationView(generics.GenericAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Application.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            instance = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            instance = Application.objects.get(pk=pk)
        except Application.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ApplicationSubmitView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ─── Одиночное изображение ───────
class ImageUploadView(generics.GenericAPIView):
    serializer_class = SingleImageSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return SingleImage.objects.all()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk, *args, **kwargs):
        try:
            instance = SingleImage.objects.get(pk=pk)
        except SingleImage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = SingleImage.objects.get(pk=pk)
        except SingleImage.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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


class TextMessageView(generics.ListAPIView):
    queryset = TextMessage.objects.all()
    serializer_class = TextMessageSerializer
    permission_classes = [AllowAny]
    
    def get(self, request, *args, **kwargs):
        messages = self.get_queryset()
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


