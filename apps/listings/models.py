from django.db import models
from django.conf import settings
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os


# ───── Локация ─────
class Location(models.Model):
    city = models.CharField("Город", max_length=100)
    district = models.CharField("Район", max_length=100)

    class Meta:
        unique_together = ('city', 'district')
        verbose_name = "Локация"
        verbose_name_plural = "Локации"

    def __str__(self):
        return f"{self.city}, {self.district}"


# ───── Объявление ─────
class Listing(models.Model):
    DEAL_TYPE_CHOICES = [
        ('sale', 'Продажа'),
        ('rent', 'Аренда'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        verbose_name="Владелец"
    )
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2)
    rooms = models.PositiveSmallIntegerField("Количество комнат")
    area = models.DecimalField("Площадь (м²)", max_digits=7, decimal_places=2)
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Локация (город/район)"
    )
    address = models.CharField("Адрес", max_length=255)
    deal_type = models.CharField("Тип сделки", max_length=10, choices=DEAL_TYPE_CHOICES)
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return f"{self.title} ({self.get_deal_type_display()})"


# ───── Фото ─────
class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Объявление"
    )
    image = models.ImageField("Изображение", upload_to='listing_images/')

    class Meta:
        verbose_name = "Фото квартиры"
        verbose_name_plural = "Фотографии квартиры"

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.lower().endswith('.webp'):
            img = Image.open(self.image)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            output = BytesIO()
            img.save(output, format='WEBP', quality=75)
            output.seek(0)
            webp_name = os.path.splitext(self.image.name)[0] + '.webp'
            self.image = ContentFile(output.read(), name=webp_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Фото → {self.listing.title}"


# ───── Заявка ─────
class Application(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applications",
        verbose_name="Пользователь"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name="Объявление"
    )
    message = models.TextField("Сообщение", blank=True)
    contact_phone = models.CharField("Телефон для связи", max_length=30)
    created_at = models.DateTimeField("Дата заявки", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "Аноним"
        return f"{username} → {self.listing.title}"


# ───── Лайки (без авторизации) ─────
class ListingLike(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name="Объявление"
    )
    ip_address = models.GenericIPAddressField("IP-адрес")
    created_at = models.DateTimeField("Дата лайка", auto_now_add=True)

    class Meta:
        unique_together = ('listing', 'ip_address')
        verbose_name = "Лайк"
        verbose_name_plural = "Лайки"

    def __str__(self):
        return f"{self.ip_address} ❤️ {self.listing.title}"
