from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    ManagerCreationSerializer,
)

User = get_user_model()


class RegisterAdminView(generics.CreateAPIView):
    """Регистрация администратора (разрешено всем)"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class CreateRealtorView(generics.CreateAPIView):
    """Создание менеджера (реалтора), только для админов"""
    queryset = User.objects.all()
    serializer_class = ManagerCreationSerializer
    permission_classes = [permissions.IsAdminUser]


class MeView(APIView):
    """Получение текущего пользователя"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
