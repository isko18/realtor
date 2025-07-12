from rest_framework import serializers
from .models import (
    Location,
    Listing,
    ListingImage,
    Favorite,
    Application,
)


# ───── Локация ─────
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'district']
        read_only_fields = ['id']


# ───── Фото квартиры (только read) ─────
class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image']
        read_only_fields = ['id', 'image']


# ───── Объявление ─────
class ListingSerializer(serializers.ModelSerializer):
    # READ
    location = LocationSerializer(read_only=True)
    images = ListingImageSerializer(many=True, read_only=True)

    # WRITE
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        source='location',
        write_only=True
    )
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=5_000_000, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = Listing
        fields = [
            'id',
            'owner',
            'title',
            'description',
            'price',
            'rooms',
            'area',
            'location',
            'location_id',
            'address',
            'deal_type',
            'is_active',
            'created_at',
            'images',
            'uploaded_images',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'is_active', 'images']

    def create(self, validated_data):
        images = validated_data.pop('uploaded_images', [])
        listing = Listing.objects.create(**validated_data)
        for img in images:
            ListingImage.objects.create(listing=listing, image=img)
        return listing

    def update(self, instance, validated_data):
        images = validated_data.pop('uploaded_images', None)
        if images is not None:
            instance.images.all().delete()
            for img in images:
                ListingImage.objects.create(listing=instance, image=img)
        return super().update(instance, validated_data)


# ───── Избранное ─────
class FavoriteSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'listing', 'listing_id', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        return Favorite.objects.create(user=self.context['request'].user, **validated_data)


# ───── Заявка ─────
class ApplicationSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    listing_id = serializers.PrimaryKeyRelatedField(
        queryset=Listing.objects.filter(is_active=True),
        source='listing',
        write_only=True
    )

    class Meta:
        model = Application
        fields = [
            'id',
            'listing',
            'listing_id',
            'message',
            'contact_phone',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        return Application.objects.create(user=self.context['request'].user, **validated_data)
