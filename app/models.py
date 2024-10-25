from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # 電話番号フィールドを追加
    phone = models.CharField(max_length=15, blank=False)  # ハイフンを含む電話番号用のフィールド

    def __str__(self):
        return self.username

class Cost(models.Model):
    cost_name = models.CharField(max_length=50, verbose_name="購入物")
    class Genre(models.TextChoices):
        FOOD = 'food', '食費'
        TRAFFIC = 'traffic', '交通費'
        ENTERTAINMENT = 'entertainment', 'エンタメ'
        SOUVENIR = 'souvenir', 'お土産'
        OTHER = 'other', 'その他'
    cost_genre = models.CharField(max_length=30, choices=Genre.choices, verbose_name="ジャンル", default="食費")
    class WalletType(models.TextChoices):
        SHARED = 'shared', '共有の財布'
        PERSONAL = 'personal', '個人の財布'
    cost_wallet = models.CharField(max_length=10, choices=WalletType. choices,verbose_name="財布の種類", default="共有の財布")

class Payment(models.Model):
    cost = models.ForeignKey(Cost, related_name='payment', on_delete=models.CASCADE)
    payment_payers = models.CharField(max_length=30, verbose_name="支払者", null=True, blank=True)
    payment_money = models.IntegerField(verbose_name="費用")
    
class Budget(models.Model):
    budget = models.IntegerField(verbose_name="予算", null=True, blank=True)
