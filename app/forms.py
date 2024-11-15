from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Plan, Schedule, Checklist
import re  # 正規表現のため

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        label="電話番号",
        max_length=15,
        required=True,
        help_text="例: 090-1234-5678"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')

    # 電話番号(ハイフン付き)
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone')
        pattern = r'^\d{2,4}-\d{2,4}-\d{4}$'
        if not re.match(pattern, phone):
            raise forms.ValidationError('電話番号の形式が正しくありません（例: 090-1234-5678）。')
        return phone

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'destination', 'start_dt', 'end_dt', 'budget', 'total_cost']

class Scheduleform(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['start_dt', 'end_dt', 'start_at', 'end_at', 'title', 'destination', 'cost', 'memo', 'address', 'phone', 'day']
        labels = {
            'start_dt': '開始日',
            'end_dt': '終了日',
            'start_at': '開始時間',
            'end_at': '終了時間',
            'title': 'タイトル',
            'destination': '目的地',
            'cost': '費用',
            'memo': 'メモ',
            'address':'住所',
            'phone':'電話番号',
            'day':'日数',
        }
        widgets = {
            'start_dt': forms.DateInput(attrs={'type': 'date'}),  
            'end_dt': forms.DateInput(attrs={'type': 'date'}),    
            'start_at': forms.TimeInput(attrs={'type': 'time'}),  
            'end_at': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_dt = cleaned_data.get("start_dt")
        end_dt = cleaned_data.get("end_dt")
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")

        # 開始日が終了日より後であればエラーを出す
        if start_dt and end_dt and start_dt > end_dt:
            self.add_error('end_dt', '終了日は開始日よりも後でなければなりません。')

        # 開始時間が終了時間より後であればエラーを出す
        if start_at and end_at and start_at > end_at:
            self.add_error('end_at', '終了時間は開始時間よりも後でなければなりません。')

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['name', 'category', 'situation']