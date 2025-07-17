from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterAdminView, CreateRealtorView, MeView

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAdminView.as_view(), name='register'),            # POST /register/
    path('create-realtor/', CreateRealtorView.as_view(), name='create-realtor'),# POST /create-realtor/
    path('me/', MeView.as_view(), name='me'),                                    # GET /me/
]
