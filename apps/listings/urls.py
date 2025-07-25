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
    ImageUploadView,
    admin_stats,
    ApplicationSubmitView, 
    TextMessageView
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
    path('images/', ImageUploadView.as_view(), name='image-upload-list'),
    path('images/<int:pk>/', ImageUploadView.as_view(), name='image-upload-detail'),
    path('admin/stats/', admin_stats, name='admin-stats'),
    path('listings/applications/submit/', ApplicationSubmitView.as_view(), name='application-submit'), 
    path('text-message/', TextMessageView.as_view(), name='text-message'),
]   