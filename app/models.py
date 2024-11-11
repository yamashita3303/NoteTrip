from django.db import models

class Schedule(models.Model):
    id = models.AutoField(primary_key=True)  # 自動インクリメントの整数フィールド
    start_dt = models.DateField()  # 開始日
    end_dt = models.DateField()  # 終了日
    start_at = models.TimeField()  # 開始時間
    end_at = models.TimeField()  # 終了時間
    title = models.CharField(max_length=30)  # タイトル (最大30文字)
    destination = models.CharField(max_length=30)  # 目的地 (最大30文字)
    cost = models.FloatField()  # 費用
    memo = models.TextField(max_length=200, blank=True)  # メモ (最大200文字、空白も許可)
    day = models.IntegerField()#日数
    address = models.CharField(max_length=255, blank=True, null=True)  # 住所フィールド
    phone = models.CharField(max_length=20, blank=True, null=True)  # 電話番号フィールド
    def __str__(self):
        return f"{self.day}日目 - {self.title}"