from django.db import models
from django.contrib.auth.models import User

class Plan(models.Model):
    title = models.CharField(max_length=30)  # タイトル
    destination = models.CharField(max_length=30)  # 旅行先
    start_dt = models.DateField()  # 開始日
    end_dt = models.DateField()  # 終了日
    budget = models.FloatField(null=True, blank=True)  # 予算
    total_cost = models.FloatField(null=True, blank=True)  # 費用合計
    image = models.ImageField(upload_to='trip_images/', null=True, blank=True)  # 画像フィールド
    # members = models.ManyToManyField(User, related_name='trips', blank=True)  # メンバー
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_trips')  # 作成者

    def __str__(self):
        return self.title
