from rest_framework import serializers
from .models import Location, Listing, ListingImage, Application, SingleImage, TextMessage

from rest_framework import serializers
from .models import Location, Listing, ListingImage, Application, SingleImage, TextMessage

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
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(),
        write_only=True,
        source='location'
    )
    images = ListingImageSerializer(many=True, read_only=True)
    image_files = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=True),
        write_only=True,
        required=False
    )
    video_file = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'description', 'price', 'rooms', 'area',
            'location', 'location_id',
            'address', 'deal_type', 'is_active', 'created_at',
            'images', 'image_files', 'likes_count', 'video', 'video_file'  
        ]

    def create(self, validated_data):
        image_files = validated_data.pop('image_files', [])
        video_file = validated_data.pop('video_file', None)
        listing = Listing.objects.create(**validated_data)
        for image_file in image_files:
            if image_file:
                ListingImage.objects.create(listing=listing, image=image_file)
        if video_file:
            listing.video = video_file
            listing.save()
        return listing

    def update(self, instance, validated_data):
        image_files = validated_data.pop('image_files', [])
        video_file = validated_data.pop('video_file', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        for image_file in image_files:
            if image_file:
                ListingImage.objects.create(listing=instance, image=image_file)
        if video_file:
            instance.video = video_file
            instance.save()
        return instance
# ───── Одиночное изображение ─────
class SingleImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = SingleImage
        fields = ['id', 'image']
        read_only_fields = ['id']


# ───── Заявка ─────
class ApplicationSerializer(serializers.ModelSerializer):
    listing = serializers.PrimaryKeyRelatedField(queryset=Listing.objects.all(), required=True)
    image_file = serializers.ImageField(write_only=True, required=False)
    image = SingleImageSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'name', 'contact_phone', 'message', 'listing', 'image_file', 'image', 'created_at']
        read_only_fields = ['id', 'created_at', 'image']

    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        application = Application.objects.create(**validated_data)
        if image_file:
            single_image = SingleImage.objects.create(image=image_file)
            application.image = single_image
            application.save()
        return application


class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ['id', 'text']