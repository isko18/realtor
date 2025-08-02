from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterAdminView, CreateRealtorView, MeView, UserUpdateView, UserDeleteView, UserListView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAdminView.as_view(), name='register'),  
    path('create-realtor/', CreateRealtorView.as_view(), name='create-realtor'),
    path('list/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('me/', MeView.as_view(), name='me'),                
]
