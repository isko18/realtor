from django.contrib import admin
from .models import Listing, ListingImage, Location, Application, SingleField, Bit, TextMessage, SingleImage, ListingImage
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from apps.listings.translation import *


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'district')
    search_fields = ('city', 'district')


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'owner', 'deal_type', 'property_type', 'price',
        'likes_count', 'is_active', 'created_at', 'floor', 'land_area', 'parking'
    )
    list_filter = (
        'deal_type', 'property_type', 'is_active', 'location__city',
        'commercial_type', 'condition', 'parking'
    )
    search_fields = (
        'title', 'description', 'address',
        'commercial_type', 'condition', 'purpose', 'property_type'
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

@admin.register(SingleField)
class SingleFieldAdmin(admin.ModelAdmin):
    list_display = ('value',)
    search_fields = ('value',)


@admin.register(Bit)
class BitAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_phone', 'created_at')
    search_fields = ('name', 'contact_phone')
    list_filter = ('created_at',)

@admin.register(TextMessage)
class TextMessageAdmin(TranslationAdmin):
    fieldsets = (
        ('Основное', {
            'fields': ('text',),
        }),
        ('Русская версия', {
            'fields': ('text_ru',),
        }),
        ('Кыргызская версия', {
            'fields': ('text_ky',),
        }),
    )
    list_display = ('text',)
    search_fields = ('text', 'text_ru', 'text_ky')

@admin.register(SingleImage)
class SingleImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')
    readonly_fields = ('image',)

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'image')
    search_fields = ('listing__title',)
