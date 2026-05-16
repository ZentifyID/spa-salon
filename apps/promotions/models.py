from django.db import models
from django.utils import timezone


class PromoCode(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "PERCENT", "Процент (%)"
        FIXED = "FIXED", "Фиксированная сумма"

    code = models.CharField("Промокод", max_length=50, unique=True)
    discount_type = models.CharField(
        "Тип скидки",
        max_length=10,
        choices=DiscountType.choices,
        default=DiscountType.PERCENT,
    )
    discount_value = models.DecimalField("Значение скидки", max_digits=10, decimal_places=2)
    is_active = models.BooleanField("Активен", default=True)
    valid_from = models.DateTimeField("Действует с", default=timezone.now)
    valid_until = models.DateTimeField("Действует до", null=True, blank=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return f"{self.code} ({self.get_discount_display()})"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now:
            return False
        if self.valid_until and self.valid_until < now:
            return False
        return True

    def get_discount_display(self):
        if self.discount_type == self.DiscountType.PERCENT:
            return f"{self.discount_value}%"
        return f"{self.discount_value} руб."


class SpecialOffer(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to="promotions/", null=True, blank=True)
    button_text = models.CharField("Текст кнопки", max_length=50, default="Узнать больше")
    button_link = models.CharField("Ссылка кнопки", max_length=255, default="/booking/")
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Спецпредложение"
        verbose_name_plural = "Спецпредложения"

    def __str__(self):
        return self.title
