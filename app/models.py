from django.db import models

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
    cost_payers = models.CharField(max_length=30, verbose_name="支払者", null=True, blank=True)
    cost_money = models.IntegerField(verbose_name="費用")
    
    
    # cost_budget = models.IntegerField(verbose_name="予算", null=True, blank=True)
