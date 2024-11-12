from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # 電話番号フィールドを追加
    phone = models.CharField(
        max_length=15,
        blank=False,
        validators=[RegexValidator(regex=r'^\d{10,11}$', message="電話番号の形式が正しくありません。")]
    )

    def __str__(self):
        return f"{self.sei} {self.mei}"


class Application(models.Model):
    sei = models.CharField(max_length=50)  # 姓
    sei_kana = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[ァ-ヶー]+$', message="フリガナはカタカナで入力してください。")])  # 姓（フリガナ）
    mei = models.CharField(max_length=50)  # 名
    mei_kana = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[ァ-ヶー]+$', message="フリガナはカタカナで入力してください。")])  # 名（フリガナ）
    organization = models.CharField(max_length=100)  # 所属団体名または会社名
    position = models.CharField(max_length=100)  # 役職
    relationship_proof = models.TextField()  # 観光協会との関係の証明
    created_at = models.DateTimeField(auto_now_add=True)  # 申請日時
    APPROVAL_STATUS = [
    ('pending', '承認待ち'),
    ('approved', '承認済み'),
    ('rejected', '拒否'),
    ]
    is_approved = models.CharField(max_length=10, choices=APPROVAL_STATUS, default='pending') # 承認フラグ
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')  # 申請者の外部キー

    def __str__(self):
        return f"{self.applicant.sei} {self.applicant.mei} - {self.organization}"
 
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
    rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], verbose_name="評価")    
    notes = models.TextField(blank=True, verbose_name="補足")
 
    def __str__(self):
        return self.name
