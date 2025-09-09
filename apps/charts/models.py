from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class CarbonUsage(models.Model):
    """Model to track carbon usage data for users"""
    CATEGORY_CHOICES = [
        ('transport', 'Transportation'),
        ('energy', 'Energy'),
        ('food', 'Food'),
        ('waste', 'Waste'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.FloatField(help_text="Carbon footprint in kg CO2")
    date = models.DateField(default=datetime.now)
    description = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.category} - {self.amount}kg CO2"
    
    class Meta:
        ordering = ['-date']

class CarbonGoal(models.Model):
    """Model to track user carbon reduction goals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    target_amount = models.FloatField(help_text="Target carbon footprint in kg CO2 per month")
    current_amount = models.FloatField(default=0, help_text="Current carbon footprint in kg CO2 this month")
    month = models.DateField()
    achieved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Goal for {self.month.strftime('%B %Y')}: {self.target_amount}kg CO2"
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            # Enhanced calculation to handle edge cases better
            progress = (self.current_amount / self.target_amount) * 100
            return min(100, max(0, progress))  # Ensure it's between 0 and 100
        return 0