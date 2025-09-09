from django import forms
from .models import InitialSurveyResult, WeeklyCheckupResult, UserProfile

class UserOnboardingForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'household_size', 'house_type', 'carbon_goal']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'household_size': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Amount of people in your household', 'min': '1', 'required': 'required'}),
            'house_type': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'carbon_goal': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Your carbon goal in kilograms of CO2/month'})
        }

    def clean_household_size(self):
        household_size = self.cleaned_data.get('household_size')
        if household_size is None or household_size < 1:
            raise forms.ValidationError("Household size must be at least 1")
        return household_size

class InitialSurveyForm(forms.ModelForm):
    class Meta:
        model = InitialSurveyResult
        exclude = [
            'user', 'monthly_raw_total', 'home_electric_subtotal',
            'renewable_discount', 'monthly_total', 'monthly_per_person',
            'household_size', 'home_type'
        ]
        widgets = {
            'primary_heating': forms.Select(attrs={'class': 'form-control'}),
            'appliance_use': forms.Select(attrs={'class': 'form-control'}),
            'lighting_type': forms.Select(attrs={'class': 'form-control'}),
            'air_conditioning': forms.Select(attrs={'class': 'form-control'}),
            'car_type': forms.Select(attrs={'class': 'form-control'}),
            'device_time': forms.Select(attrs={'class': 'form-control'}),
            'renewable_pct': forms.Select(attrs={'class': 'form-control'}),
            'flights_per_year': forms.Select(attrs={'class': 'form-control'}),
            'public_transport': forms.Select(attrs={'class': 'form-control'}),
            'compost_waste': forms.Select(attrs={'class': 'form-control'}),
            'clothes_drying': forms.Select(attrs={'class': 'form-control'}),
            'buy_secondhand': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'primary_heating': 'What is your primary heating source?',
            'appliance_use': 'How often do you use high-energy appliances?',
            'lighting_type': 'What type of lighting do you primarily use?',
            'air_conditioning': 'Do you use air conditioning?',
            'car_type': 'What type of car do you primarily use?',
            'device_time': 'How many hours per day do you use electronic devices?',
            'renewable_pct': 'What percentage of your electricity comes from renewable sources?',
            'flights_per_year': 'How many flights do you take per year?',
            'public_transport': 'How often do you use public transport?',
            'compost_waste': 'Do you compost food waste?',
            'clothes_drying': 'How do you typically dry clothes?',
            'buy_secondhand': 'How often do you buy second-hand items?',
        }

class WeeklyCheckupForm(forms.ModelForm):
    class Meta:
        model = WeeklyCheckupResult
        exclude = [
            'user', 'weekly_raw_total', 'weekly_total',
            'pct_change_from_last', 'monthly_estimate'
        ]
        widgets = {
            'appliance_usage': forms.Select(attrs={'class': 'form-control'}),
            'lighting_used': forms.Select(attrs={'class': 'form-control'}),
            'heating_ac_usage': forms.Select(attrs={'class': 'form-control'}),
            'car_usage': forms.Select(attrs={'class': 'form-control'}),
            'flights': forms.Select(attrs={'class': 'form-control'}),
            'public_transport': forms.Select(attrs={'class': 'form-control'}),
            'compost_recycle': forms.Select(attrs={'class': 'form-control'}),
            'secondhand_purchases': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'appliance_usage': 'How many times did you use washer/dryer/dishwasher this week?',
            'lighting_used': 'What type of lighting did you primarily use?',
            'heating_ac_usage': 'How many days did you use heating/AC?',
            'car_usage': 'How many days did you use a car?',
            'flights': 'Did you take any flights this week?',
            'public_transport': 'How many days did you use public transport?',
            'compost_recycle': 'Did you compost/recycle this week?',
            'secondhand_purchases': 'Did you make any second-hand purchases?',
        }
