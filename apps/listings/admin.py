from django.contrib import admin
from .models import Listing, ListingImage, Location, Application, ListingLike


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'district')
    search_fields = ('city', 'district')


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    readonly_fields = ['image']


class ListingLikeInline(admin.TabularInline):
    model = ListingLike
    extra = 0
    readonly_fields = ['ip_address', 'created_at']
    can_delete = True


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'deal_type', 'price', 'is_active', 'created_at')
    list_filter = ('deal_type', 'is_active', 'location__city')
    search_fields = ('title', 'description', 'address')
    inlines = [ListingImageInline, ListingLikeInline]
    actions = ['mark_active', 'mark_inactive']

    @admin.action(description='Опубликовать выбранные объявления')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Снять с публикации')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'contact_phone', 'created_at')
    search_fields = ('user__username', 'listing__title', 'contact_phone')
    list_filter = ('created_at',)
    readonly_fields = ('message',)


@admin.register(ListingLike)
class ListingLikeAdmin(admin.ModelAdmin):
    list_display = ('listing', 'ip_address', 'created_at')
    search_fields = ('listing__title', 'ip_address')
    list_filter = ('created_at',)
    autocomplete_fields = ['listing']
