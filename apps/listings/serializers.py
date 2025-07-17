from rest_framework import serializers
from .models import (
    Location,
    Listing,
    ListingImage,
    Application,
    ListingLike
)


# ───── Локация ─────
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'district']


# ───── Фото ─────
class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image']


# ───── Объявление ─────
class ListingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'rooms', 'area',
            'location', 'address', 'deal_type', 'is_active', 'created_at',
            'images', 'likes_count'
        ]


# ───── Заявка ─────
class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'listing', 'message', 'contact_phone', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        return Application.objects.create(user=user, **validated_data)


# ───── Лайк (опциональный вывод) ─────
class ListingLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingLike
        fields = ['id', 'listing', 'ip_address', 'created_at']
        read_only_fields = fields
