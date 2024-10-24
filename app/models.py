from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # 電話番号フィールドを追加
    phone = models.CharField(max_length=15, blank=False)  # ハイフンを含む電話番号用のフィールド

    def __str__(self):
        return self.username
