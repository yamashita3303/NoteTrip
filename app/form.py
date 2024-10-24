from django import forms
from .models import Plan

class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['title', 'destination', 'start_dt', 'end_dt', 'budget', 'total_cost']
