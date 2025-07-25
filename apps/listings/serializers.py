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
        required=False,
        allow_null=True,
        source='location'
    )

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
            'location', 'location_id', 'address', 'deal_type',
            'is_active', 'created_at', 'likes_count',
            'images', 'video', 
            'media',       
            'media_files'    
        ]

    def create(self, validated_data):
        media_files = validated_data.pop('media_files', [])
        listing = Listing.objects.create(**validated_data)

        for file in media_files:
            if file.content_type.startswith("image/"):
                ListingImage.objects.create(listing=listing, image=file)
            elif file.content_type.startswith("video/"):
                listing.video = file
                listing.save()
        return listing

    def update(self, instance, validated_data):
        media_files = validated_data.pop('media_files', [])
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        for file in media_files:
            if file.content_type.startswith("image/"):
                ListingImage.objects.create(listing=instance, image=file)
            elif file.content_type.startswith("video/"):
                instance.video = file
                instance.save()
        return instance

    def get_media(self, obj):
        media = []
        for img in obj.images.all():
            media.append({
                "type": "image",
                "url": img.image.url
            })
        if obj.video:
            media.append({
                "type": "video",
                "url": obj.video.url
            })
        return media

    
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
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'name', 'contact_phone', 'listing', 'image', 'created_at', 'image_file']
        read_only_fields = ['id', 'created_at', 'image']

    def get_image(self, obj):
        return obj.image.image.url if obj.image else None

    def create(self, validated_data):
        image_file = validated_data.pop('image_file', None)
        app = Application.objects.create(**validated_data)
        if image_file:
            img = SingleImage.objects.create(image=image_file)
            app.image = img
            app.save()
        return app

class SimpleApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['id', 'name', 'contact_phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']

class ApplicationPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['name', 'contact_phone', 'listing', 'image']



class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ['id', 'text']