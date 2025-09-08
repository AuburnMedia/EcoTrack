from django import forms
from .models import CarbonGoal

class CarbonGoalForm(forms.ModelForm):
    target_amount = forms.FloatField(
        label='Monthly Carbon Goal (kg CO₂)',
        help_text='Set your target monthly carbon footprint in kilograms of CO₂',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarbonGoal
        fields = ['target_amount']

    def clean_target_amount(self):
        target = self.cleaned_data['target_amount']
        if target <= 0:
            raise forms.ValidationError("Goal must be greater than 0 kg CO₂")
        return target
