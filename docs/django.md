# Django Implementation

This document outlines the Django implementation of EcoTrack, including models, forms, views, and their relationships.

## Models

### User Models

#### UserProfile
Extends the default Django User model with additional fields:
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    household_size = models.PositiveIntegerField(default=1)
    house_type = models.CharField(max_length=10, choices=[
        ("LARGE", "Large house"),
        ("SMALL", "Small house"),
        ("APT", "Apartment")
    ])
    carbon_goal = models.PositiveIntegerField(help_text="Monthly carbon goal in kilograms of CO2")
    onboarding_completed = models.BooleanField(default=False)
```

### Survey Models

#### InitialSurveyResult
Stores the results of the initial carbon footprint survey:
```python
class InitialSurveyResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)
    monthly_raw_total = models.DecimalField(max_digits=10, decimal_places=2)
    home_electric_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    renewable_discount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_total = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    # Survey-specific fields as defined in forms.py
```

#### WeeklyCheckupResult
Records weekly carbon usage updates:
```python
class WeeklyCheckupResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)
    weekly_raw_total = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_total = models.DecimalField(max_digits=10, decimal_places=2)
    pct_change_from_last = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    monthly_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    home_electric_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    renewable_discount = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_estimate_per_person = models.DecimalField(max_digits=10, decimal_places=2)
```

### Chart Models

#### CarbonGoal
Tracks user's monthly carbon reduction goals:
```python
class CarbonGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    target_amount = models.FloatField()
    current_amount = models.FloatField(default=0)
    achieved = models.BooleanField(default=False)
```

## Forms

### User Forms

#### UserOnboardingForm
```python
class UserOnboardingForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["display_name", "household_size", "house_type", "carbon_goal"]
```

### Survey Forms

#### InitialSurveyForm
```python
class InitialSurveyForm(forms.ModelForm):
    class Meta:
        model = InitialSurveyResult
        exclude = [
            "user",
            "monthly_raw_total",
            "home_electric_subtotal",
            "renewable_discount",
            "monthly_total",
            "monthly_per_person",
            "household_size",
            "home_type",
        ]
```

#### WeeklyCheckupForm
```python
class WeeklyCheckupForm(forms.ModelForm):
    class Meta:
        model = WeeklyCheckupResult
        exclude = [
            "user",
            "weekly_raw_total",
            "weekly_total",
            "pct_change_from_last",
            "monthly_estimate",
            "home_electric_subtotal",
            "renewable_discount",
            "monthly_estimate_per_person",
        ]
```

### Chart Forms

#### CarbonGoalForm
```python
class CarbonGoalForm(forms.ModelForm):
    class Meta:
        model = CarbonGoal
        fields = ["target_amount"]
```

## Views

### Authentication Views

#### register
- Handles user registration
- Creates UserProfile upon registration
- Redirects to onboarding

#### onboarding
- Processes initial user setup
- Sets household information and carbon goals
- Marks onboarding as complete

### Dashboard Views

#### index
- Main dashboard view
- Displays carbon usage overview
- Shows weekly checkup status
- Manages carbon goal progress

### Survey Views

#### initial_survey
- Handles initial carbon footprint survey
- Calculates baseline carbon usage
- Creates InitialSurveyResult obj

#### weekly_checkup
- Processes weekly carbon usage updates
- Calculates trends and changes
- Updates WeeklyCheckupResult onj

#### survey_dashboard
- Displays survey history
- Shows carbon usage trends
- Presents analytics

### Chart Views

#### manage_carbon_goal
- Handles carbon goal creation/updates
- Tracks goal progress
- Manages achievement status

#### charts_index
- Displays detailed carbon analytics
- Shows usage breakdowns by category
- Presents monthly trends

## URL Configuration

### Main URLs
- `/` - Dashboard (index)
- `/accounts/register/` - User registration
- `/onboarding/` - User onboarding
- `/survey/initial/` - Initial survey
- `/survey/weekly/` - Weekly checkup
- `/survey/dashboard/` - Survey overview
- `/charts/` - Detailed analytics
- `/charts/manage-goal/` - Goal management

## Admin Configuration

### CarbonUsageAdmin
```python
@admin.register(CarbonUsage)
class CarbonUsageAdmin(admin.ModelAdmin):
    list_display = ["category", "amount", "date", "user", "description"]
    list_filter = ["category", "date", "user"]
    search_fields = ["description", "category"]
    date_hierarchy = "date"
    ordering = ["-date"]
```

### CarbonGoalAdmin
```python
@admin.register(CarbonGoal)
class CarbonGoalAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "month",
        "target_amount",
        "current_amount",
        "progress_percentage",
        "achieved",
    ]
    list_filter = ["achieved", "month", "user"]
    ordering = ["-month"]
    readonly_fields = ["progress_percentage"]
```

## Custom Decorators

### onboarding_required
Ensures users have completed the onboarding process before accessing protected views:
```python
def onboarding_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if not profile.onboarding_completed:
                return redirect("onboarding")
        except UserProfile.DoesNotExist:
            return redirect("onboarding")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
```

This decorator:
- Checks if the user has a UserProfile
- Verifies onboarding_completed status
- Redirects to onboarding if not completed
- Applied to views requiring completed onboarding:
  - index
  - survey_dashboard
  - weekly_checkup
  - charts_index
  - manage_carbon_goal
