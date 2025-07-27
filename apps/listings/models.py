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

class SingleField(models.Model):
    value  = models.CharField("Текст",max_length=255)  

    class Meta:
        verbose_name = "Одно поле"
        verbose_name_plural = "Одно поле"

    def __str__(self):
        return self.value
    

class Listing(models.Model):
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
    single_field = models.ForeignKey(
        SingleField,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="complex"
    )
    address = models.CharField("Адрес", max_length=255)
    deal_type = models.CharField("Тип сделки", max_length=50)
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    likes_count = models.PositiveIntegerField("Количество лайков", default=0)

    property_type = models.CharField("Тип недвижимости", max_length=100, blank=True, null=True)

    floor = models.PositiveSmallIntegerField("Этаж", blank=True, null=True)
    land_area = models.DecimalField("Площадь участка (сотки)", max_digits=7, decimal_places=2, blank=True, null=True)
    commercial_type = models.CharField("Тип коммерции", max_length=100, blank=True, null=True)
    condition = models.CharField("Состояние", max_length=100, blank=True, null=True)
    utilities = models.TextField("Коммуникации", blank=True, null=True)
    purpose = models.CharField("Назначение", max_length=100, blank=True, null=True)
    parking = models.BooleanField("Парковка", default=False)
    document = models.CharField("Документ",max_length=255, blank=True, null=True)


    class Meta:
        ordering = ['-created_at']
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"

    def __str__(self):
        return f"{self.title} ({self.deal_type})"

    


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
        try:
            if self.image:
                print(f"Сохранение изображения: {self.image.name}")
                super().save(*args, **kwargs)
        except Exception as e:
            print(f"Ошибка при сохранении изображения: {str(e)}")
            raise

    def __str__(self):
        return f"Фото → {self.listing.title}"

# ───── Одиночное изображение ─────
class SingleImage(models.Model):
    image = models.ImageField("Изображение", upload_to='single_images/')

    class Meta:
        verbose_name = "Одиночное изображение"
        verbose_name_plural = "Одиночные изображения"

    def __str__(self):
        return f"Изображение ID: {self.id}"

# ───── Заявка ─────
class Application(models.Model):
    name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=100)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='applications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Заявка с объявлением"
        verbose_name_plural = "Заявки с объявлениями"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка: {self.name} ({self.contact_phone})"


class Bit(models.Model):
    name = models.CharField("Имя", max_length=100)
    contact_phone = models.CharField("Телефон", max_length=30)
    message = models.TextField("Сообщение", blank=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Простая заявка"
        verbose_name_plural = "Простые заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Простая заявка: {self.name} ({self.contact_phone})"

class TextMessage(models.Model):
    text = models.TextField("Текст", max_length=500)

    class Meta:
        verbose_name = "Текстовое сообщение"
        verbose_name_plural = "Текстовые сообщения"

    def __str__(self):
        return self.text