from django.contrib import admin
from .models import Listing, ListingImage, Location, Favorite, Application


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'district')
    search_fields = ('city', 'district')


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ['image']


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'deal_type', 'price', 'is_active', 'created_at')
    list_filter = ('deal_type', 'is_active', 'location__city')
    search_fields = ('title', 'description', 'address')
    inlines = [ListingImageInline]
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='Опубликовать выбранные объявления')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Снять с публикации')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    search_fields = ('user__username', 'listing__title')
    autocomplete_fields = ['user', 'listing']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'contact_phone', 'created_at')
    search_fields = ('user__username', 'listing__title', 'contact_phone')
    list_filter = ('created_at',)
    readonly_fields = ('message',)
