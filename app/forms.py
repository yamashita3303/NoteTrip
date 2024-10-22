from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # カスタムユーザーモデルをインポート

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser  # カスタムユーザーモデルを指定
        fields = ('username', 'email', 'password1', 'password2')  # 必要なフィールドを指定
