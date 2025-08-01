from rest_framework import serializers
from .models import Location, Listing, SingleField, ListingImage, Application, Bit, SingleImage, TextMessage
from apps.users.models import User

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'avatar']

# ───── Объявление ─────
class ListingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        required=True,
        source='location'
    )
    owner = UserSerializer(read_only=True)  # ← Показываем создателя объявления

    # Обязательные поля
    title = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    area = serializers.DecimalField(max_digits=8, decimal_places=2, required=True)
    address = serializers.CharField(required=True)
    deal_type = serializers.CharField(required=True)
    property_type = serializers.CharField(required=True)

    # Необязательные поля
    rooms = serializers.IntegerField(required=False, allow_null=True)
    floor = serializers.IntegerField(required=False, allow_null=True)
    land_area = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    commercial_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    condition = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    utilities = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    purpose = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    parking = serializers.BooleanField(required=False)
    document = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    single_field = serializers.PrimaryKeyRelatedField(
        queryset=SingleField.objects.all(),
        required=False,
        allow_null=True
    )
    series = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Медиа
    media_files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=True),
        write_only=True,
        required=False
    )
    images = ListingImageSerializer(many=True, read_only=True)
    media = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'rooms', 'area',
            'floor', 'land_area', 'commercial_type', 'condition',
            'utilities', 'purpose', 'parking', 'property_type',
            'location', 'location_id', 'address', 'deal_type',
            'is_active', 'created_at', 'likes_count',
            'images', 'media', 'media_files', 'document', 'single_field',
            'series', 'owner'  # ← Показываем владельца
        ]

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        user = self.context['request'].user
        listing = Listing.objects.create(owner=user, **validated_data)
        for file in media_files:
            if file.content_type.startswith("image/"):
                ListingImage.objects.create(listing=listing, image=file)
        return listing

    def update(self, instance, validated_data):
        media_files = validated_data.pop('media_files', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for file in media_files:
            if file.content_type.startswith("image/"):
                ListingImage.objects.create(listing=instance, image=file)
        return instance

    def get_media(self, obj):
        media = []
        for img in obj.images.all():
            media.append({"type": "image", "url": img.image.url})
        return media
    

class SingleFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleField
        fields = ['id', 'value']

# ───── Одиночное изображение ─────
class SingleImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = SingleImage
        fields = ['id', 'image']
        read_only_fields = ['id']


# ───── Заявка ─────
class ApplicationSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Application
        fields = ['id', 'name', 'contact_phone', 'listing', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_image_url(self, obj):
        if obj.image and obj.image.image:
            return obj.image.image.url
        return None



class BitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bit
        fields = ['id', 'name', 'contact_phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ['id', 'text_ru', 'text_ky']