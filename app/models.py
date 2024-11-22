from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
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
