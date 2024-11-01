from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

class CustomUser(AbstractUser):
    # 電話番号フィールドを追加
    phone = models.CharField(max_length=15, blank=False)  # ハイフンを含む電話番号用のフィールド

    def __str__(self):
        return self.username

class Plan(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)  # タイトル
    destination = models.CharField(max_length=30)  # 旅行先
    start_dt = models.DateField()  # 開始日
    end_dt = models.DateField()  # 終了日
    budget = models.FloatField(null=True, blank=True)  # 予算
    total_cost = models.FloatField(null=True, blank=True)  # 費用合計
    image = models.ImageField(upload_to='trip_images/', null=True, blank=True)  # 画像フィールド
    # members = models.ManyToManyField(User, related_name='trips', blank=True)  # メンバー

    def __str__(self):
        return self.title
