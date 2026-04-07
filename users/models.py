from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email