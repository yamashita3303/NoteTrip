from django import forms
from django.forms import ModelForm
from .models import Cost

class CostForm(ModelForm):
    class Meta:
        model = Cost
        fields = [
            "cost_name",
            "cost_genre",
            "cost_wallet",
            "cost_payers",
            "cost_money",
        ]
        widgets = {
            'cost_wallet': forms.RadioSelect,  # ラジオボタンにする
        }
    def __init__(self, *args, **kwargs):
        super(CostForm, self).__init__(*args, **kwargs)
        self.fields['cost_wallet'].empty_label = None  # 空白選択肢を無効化