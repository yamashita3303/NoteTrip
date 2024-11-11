from django import forms
from .models import Plan
from.models import Checklist

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'destination', 'start_dt', 'end_dt', 'budget', 'total_cost']

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['name', 'category', 'situation']