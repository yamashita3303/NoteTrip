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
    members = models.ManyToManyField(CustomUser, related_name='members', blank=True)  # メンバー

    def __str__(self):
        return self.title
    
class Schedule(models.Model):
    id = models.AutoField(primary_key=True)  # 自動インクリメントの整数フィールド
    start_dt = models.DateField()  # 開始日
    end_dt = models.DateField()  # 終了日
    start_at = models.TimeField()  # 開始時間
    end_at = models.TimeField()  # 終了時間
    title = models.CharField(max_length=30)  # タイトル (最大30文字)
    destination = models.CharField(max_length=30)  # 目的地 (最大30文字)
    address = models.CharField(max_length=255, blank=True, null=True)  # 住所フィールド
    phone = models.CharField(max_length=20, blank=True, null=True)  # 電話番号フィールド
    cost = models.FloatField()  # 費用
    memo = models.TextField(max_length=200, blank=True)  # メモ (最大200文字、空白も許可)
    day = models.IntegerField()#日数
    def __str__(self):
        return f"{self.day}日目 - {self.title}"

class Checklist(models.Model):
    CATEGORY_CHOICES = [
        ('valuables', '貴重品'),
        ('clothes', '衣類'),
        ('mobile', 'モバイル関連'),
        ('cosmetics', '化粧品＆衛生用品'),
        ('medicines', '医薬品'),
        ('other', 'その他'),
    ]

    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    situation = models.BooleanField(default=False)

    def __str__(self):
        return self.name
