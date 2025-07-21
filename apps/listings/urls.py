from django.urls import path
from .views import (
    ListingListCreateView,
    ListingRetrieveUpdateDestroyView,
    MyListingsView,
    ListingLikeView,
    LocationListView,
    LocationCreateView,
    LocationDeleteView,
    ApplicationView,
    admin_stats
)

urlpatterns = [
    path('locations/list/', LocationListView.as_view(), name='location-list'),
    path('locations/create/', LocationCreateView.as_view(), name='location-create'),
    path('locations/<int:pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
    path('listings/', ListingListCreateView.as_view(), name='listing-list-create'),
    path('listings/<int:pk>/', ListingRetrieveUpdateDestroyView.as_view(), name='listing-detail'),
    path('listings/<int:pk>/like/', ListingLikeView.as_view(), name='listing-like'),
    path('listings/my/', MyListingsView.as_view(), name='my-listings'),
    path('applications/', ApplicationView.as_view(), name='application-list'),
    path('applications/<int:pk>/', ApplicationView.as_view(), name='application-detail'),
    path('admin/stats/', admin_stats, name='admin-stats'),
]