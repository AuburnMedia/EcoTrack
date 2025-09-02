from django.contrib import admin
from .models import CarbonUsage, CarbonGoal

# Register your models here.

@admin.register(CarbonUsage)
class CarbonUsageAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'date', 'user', 'description']
    list_filter = ['category', 'date', 'user']
    search_fields = ['description', 'category']
    date_hierarchy = 'date'
    ordering = ['-date']

@admin.register(CarbonGoal)
class CarbonGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'target_amount', 'current_amount', 'progress_percentage', 'achieved']
    list_filter = ['achieved', 'month', 'user']
    ordering = ['-month']
    readonly_fields = ['progress_percentage']
