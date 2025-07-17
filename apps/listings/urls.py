from django.urls import path
from .views import (
    ListingListCreateView,
    ListingRetrieveUpdateDestroyView,
    MyListingsView,
    ListingLikeToggleView,
    LocationListView,
    LocationCreateView,
    ApplicationListCreateView,
    MyApplicationsView,
    admin_stats
)

urlpatterns = [
    path('locations/list/', LocationListView.as_view()),
    path('locations/create/', LocationCreateView.as_view()),
    path('listings/', ListingListCreateView.as_view()),
    path('listings/<int:pk>/', ListingRetrieveUpdateDestroyView.as_view()),
    path('listings/<int:pk>/like/', ListingLikeToggleView.as_view()),
    path('listings/my/', MyListingsView.as_view()),

    path('applications/', ApplicationListCreateView.as_view()),
    path('applications/my/', MyApplicationsView.as_view()),

    path('admin/stats/', admin_stats),
]
