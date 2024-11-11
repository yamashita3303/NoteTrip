from django.db import models

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
