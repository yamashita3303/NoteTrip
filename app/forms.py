from django import forms
from django.forms import ModelForm
from .models import CustomUser, Cost, Payment, Budget
from django.contrib.auth.forms import UserCreationForm
import re  # 正規表現のためにインポート

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        label="電話番号",
        max_length=15,
        required=True,
        help_text="例: 090-1234-5678"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser  # カスタムユーザーモデルを指定
        fields = ('username', 'email', 'phone', 'password1', 'password2')  # 必要なフィールドを指定

    # 電話番号のバリデーション (ハイフン付き)
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^\d{2,4}-\d{2,4}-\d{4}$'  # 電話番号のフォーマット（例: 090-1234-5678）
        if not re.match(pattern, phone):
            raise forms.ValidationError('電話番号の形式が正しくありません（例: 090-1234-5678）。')
        return phone

class CostForm(ModelForm):
    class Meta:
        model = Cost
        fields = [
            "cost_name",
            "cost_genre",
            "cost_wallet",
        ]
        widgets = {
            'cost_wallet': forms.RadioSelect,  # ラジオボタンにする
        }
    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)
        self.fields['cost_wallet'].empty_label = None  # 空白選択肢を無効化

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = [
            "payment_payers",
            "payment_money",
        ]

class BudgetForm(ModelForm):
    class Meta:
        model = Budget
        fields = [
            "budget",
        ]