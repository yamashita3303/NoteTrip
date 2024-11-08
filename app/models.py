from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # 電話番号フィールドを追加
    phone = models.CharField(max_length=15, blank=False)  # ハイフンを含む電話番号用のフィールド

    def __str__(self):
        return self.username

class Application(models.Model):
    sei = models.CharField(max_length=50)  # 姓
    sei_kana = models.CharField(max_length=50)  # 姓（フリガナ）
    mei = models.CharField(max_length=50)  # 名
    mei_kana = models.CharField(max_length=50)  # 名（フリガナ）
    organization = models.CharField(max_length=100)  # 所属団体名または会社名
    position = models.CharField(max_length=100)  # 役職
    relationship_proof = models.TextField()  # 観光協会との関係の証明
    created_at = models.DateTimeField(auto_now_add=True)  # 申請日時
    is_approved = models.BooleanField(default=False)  # 承認フラグ
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # 申請者の外部キー

    def __str__(self):
        return f"{self.sei} {self.mei} - {self.organization}"
 
class Spot(models.Model):
    CATEGORY_CHOICES = [
        ('観光地', '観光地'),
        ('レストラン', 'レストラン'),
        ('カフェ', 'カフェ'),
        ('自然スポット', '自然スポット'),
    ]
 
    name = models.CharField(max_length=100, verbose_name="スポット名")
    address = models.CharField(max_length=200, verbose_name="住所")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="カテゴリー")
    opening_hours = models.CharField(max_length=100, blank=True, verbose_name="営業時間")
    price = models.CharField(max_length=50, blank=True, verbose_name="料金")
    rating = models.FloatField(verbose_name="評価")    
    notes = models.TextField(blank=True, verbose_name="補足")
 
    def __str__(self):
        return self.name
