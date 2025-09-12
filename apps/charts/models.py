from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.


class CarbonUsage(models.Model):
    """Model to track carbon usage data for users"""

    CATEGORY_CHOICES = [
        ("transport", "Transportation"),
        ("energy", "Energy"),
        ("food", "Food"),
        ("waste", "Waste"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.FloatField(help_text="Carbon footprint in kg CO2")
    date = models.DateField(default=datetime.now)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount}kg CO2"

    class Meta:
        ordering = ["-date"]


class CarbonGoal(models.Model):
    """Model to track user carbon reduction goals"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    target_amount = models.FloatField(
        help_text="Target carbon footprint in kg CO2 per month"
    )
    current_amount = models.FloatField(
        default=0, help_text="Current carbon footprint in kg CO2 this month"
    )
    month = models.DateField()
    achieved = models.BooleanField(default=False)

    def __str__(self):
        return f"Goal for {self.month.strftime('%B %Y')}: {self.target_amount}kg CO2"

    @property
    def progress_percentage(self):
        # Get the user's initial survey for baseline
        from apps.pages.models import InitialSurveyResult
        baseline_survey = InitialSurveyResult.objects.filter(user=self.user).first()
        
        if baseline_survey and self.target_amount > 0 and self.current_amount >= 0:
            baseline = float(baseline_survey.monthly_total)
            
            # Validate the goal
            if self.target_amount >= baseline:
                # Invalid goal (target should be less than baseline)
                return 0
            
            # Case 1: Current usage exceeds baseline
            if self.current_amount >= baseline:
                return 0
            # Case 2: Current usage is below target (exceeded goal)
            elif self.current_amount <= self.target_amount:
                return 100
            # Case 3: Current usage is between baseline and target
            else:
                total_reduction_needed = baseline - self.target_amount
                reduction_achieved = baseline - self.current_amount
                progress = min(100, (reduction_achieved / total_reduction_needed) * 100)
                return max(0, progress)
        return 0
