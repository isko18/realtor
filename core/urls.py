from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.listings.views import index


# drf-yasg: схема и контактная информация
schema_view = get_schema_view(
    openapi.Info(
        title="Real Estate API",
        default_version='v1',
        description="API для платформы недвижимости",
        terms_of_service="https://yourdomain.com/terms/",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# Приложения
apps_includes = [
    path('listings/', include('apps.listings.urls')),
    path('users/', include('apps.users.urls')),
]

# API-группировка
api_urlpatterns = [
    path('v1/', include(apps_includes)),
]

# Общие URL'ы
urlpatterns = [
    path('', index, name='index'),
    path('favorites/', index, name='index'),
    path('login/', index, name='index'),
    path('dashboard/profile/', index, name='index'),
    path('dashboard/announcements/', index, name='index'),
    path('dashboard/create-listing/', index, name='index'),
    path('dashboard/single/', index, name='index'),
    path('dashboard/bit/', index, name='index'),
    path('dashboard/agent/', index, name='index'),
    path('dashboard/locations/', index, name='index'),
    path('dashboard/texteditor/', index, name='index'),
    path('dashboard/register/', index, name='index'),
    path('dashboard/image-admin/', index, name='index'),
    path('dashboard/listing-manager/', index, name='index'),
    path('dashboard/employee/', index, name='index'),
    






    path('admin/', admin.site.urls),

    # API
    path('api/', include(api_urlpatterns)),

    # Документация Swagger и Redoc от drf-yasg
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Медиа-файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
