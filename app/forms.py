from django import forms
from .models import Schedule

class Scheduleform(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['start_dt', 'end_dt', 'start_at', 'end_at', 'title', 'destination', 'cost', 'memo','address','phone']
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
