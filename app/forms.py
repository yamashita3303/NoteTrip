from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import CustomUser  # カスタムユーザーモデルをインポート
from .models import Application
from .models import Spot
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
    
class AssociationApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('sei', 'sei_kana', 'mei', 'mei_kana', 'organization', 'position', 'relationship_proof')

class SpotForm(forms.ModelForm):
    class Meta:
        model = Spot
        fields = ["name", "address", "category", "opening_hours", "price", "rating", "notes"]
        