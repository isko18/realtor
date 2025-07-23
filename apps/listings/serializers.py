from rest_framework import serializers
from .models import Location, Listing, ListingImage, Application, SingleImage

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
    image_files = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'rooms', 'area',
            'location', 'address', 'deal_type', 'is_active', 'created_at',
            'images', 'image_files', 'likes_count'
        ]

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        listing = Listing.objects.create(**validated_data)
        for image_file in image_files:
            ListingImage.objects.create(listing=listing, image=image_file)
        return listing

    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for image_file in image_files:
            ListingImage.objects.create(listing=instance, image=image_file)
        return instance

# ───── Заявка ─────
class ApplicationSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), required=True)
    image = serializers.ImageField(required=False, allow_empty_file=True)

    class Meta:
        model = Application
        fields = ['id', 'name', 'contact_phone', 'message', 'listing', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        image_file = validated_data.pop('image', None)
        application = Application.objects.create(**validated_data)
        if image_file:
            single_image = SingleImage.objects.create(image=image_file)
            application.image = single_image
            application.save()
        return application
# ───── Одиночное изображение ─────
class SingleImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = SingleImage
        fields = ['id', 'image']
        read_only_fields = ['id']