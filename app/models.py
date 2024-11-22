from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

class CustomUser(AbstractUser):
    phone = models.CharField(
        max_length=15,
        blank=False,
        validators=[RegexValidator(regex=r'^\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$', message="電話番号の形式が正しくありません。")]
    )
    email = models.EmailField(unique=True)

    @property
    def application(self):
        return self.applications.first()

    def total_applications(self):
        return self.applications.count()

    def approved_applications(self):
        return self.applications.filter(status='approved')

    def rejected_applications(self):
        return self.applications.filter(status='rejected')

    def __str__(self):
        return f"{self.sei} {self.mei}"

class Application(models.Model):
    sei = models.CharField(max_length=50)
    sei_kana = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[ァ-ヶー]+$', message="フリガナはカタカナで入力してください。")])
    mei = models.CharField(max_length=50)
    mei_kana = models.CharField(max_length=50, validators=[RegexValidator(regex=r'^[ァ-ヶー]+$', message="フリガナはカタカナで入力してください。")])
    organization = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    relationship_proof = models.TextField()
    @property
    def content(self):
        # ここで申請内容を計算して返す
        return f"申請者: {self.sei} {self.mei}, 団体名: {self.organization}, 証明: {self.relationship_proof}"
    
    created_at = models.DateTimeField(auto_now_add=True)
    # 申請の状態
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, '未処理'),
        (APPROVED, '承認'),
        (REJECTED, '却下'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='applications')
    list_display = ('applicant', 'organization', 'status', 'created_at')

    def approve(self):
        self.status = 'approved'
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def send_notification(self):
        subject = f"申請結果: {self.get_status_display()}"
        message = f"申請内容:\n\n名前: {self.sei} {self.mei}\n団体名: {self.organization}\n役職: {self.position}\n\n結果: {self.get_status_display()}"
        recipient_email = self.applicant.email

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [recipient_email],
        )

    def save(self, *args, **kwargs):
        if self.pk:
            previous = Application.objects.get(pk=self.pk)
            if previous.status != self.status:
                self.send_notification()
        super().save(*args, **kwargs)

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

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, '不明')

    def get_rating_display(self):
        return f"{self.rating} / 5"

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
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
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
    day = models.IntegerField(null=True, blank=True)  # 日数
    
    def save(self, *args, **kwargs):
    # 開始日からの経過日数を計算
        if self.plan and self.start_dt:
            # start_dtがplan.start_dtよりも前の場合は0に設定
            self.day = max((self.start_dt - self.plan.start_dt).days + 1, 1)  # 1日目から始まるように+1、負の値を防ぐ
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - Day {self.day}"

class Checklist(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
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
