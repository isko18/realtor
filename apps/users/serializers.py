from rest_framework import serializers
from django.contrib.auth import get_user_model
import random
import string

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role']
        read_only_fields = ['id', 'role']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'phone', 'role']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password2': "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)

        # Автоматически назначаем роль админа
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        return user


class ManagerCreationSerializer(serializers.ModelSerializer):
    password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'role', 'password']
        read_only_fields = ['id', 'role', 'password']

    def generate_password(self, length=10):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    def create(self, validated_data):
        # Генерация пароля
        generated_password = self.generate_password()

        user = User(**validated_data)
        user.set_password(generated_password)
        user.role = 'realtor'
        user.is_staff = False
        user.save()

        # Сохраняем пароль во внутреннее поле для доступа в get_password
        self._generated_password = generated_password

        return user

    def get_password(self, obj):
        # Только для администратора возвращаем сгенерированный пароль
        request = self.context.get('request')
        if request and request.user.is_staff:
            return getattr(self, '_generated_password', None)
        return None