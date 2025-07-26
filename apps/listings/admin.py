from django.contrib import admin
from .models import Listing, ListingImage, Location, Application


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'district')
    search_fields = ('city', 'district')


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ['image']
    fields = ['image']  

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'deal_type', 'price', 'likes_count',
        'is_active', 'created_at', 'floor', 'land_area', 'parking'
    )
    list_filter = (
        'deal_type', 'is_active', 'location__city',
        'commercial_type', 'condition', 'parking'
    )
    search_fields = (
        'title', 'description', 'address',
        'commercial_type', 'condition', 'purpose'
    )
    inlines = [ListingImageInline]
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='Опубликовать выбранные объявления')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Снять с публикации')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)



@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_phone', 'created_at')  
    search_fields = ('name', 'contact_phone')               
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)

    fields = ('name', 'contact_phone', 'listing', 'image', 'created_at')