from django.shortcuts import render
from django.core import serializers
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from apps.charts.models import CarbonUsage, CarbonGoal
import json

# Create your views here.

def index(request):
    # Get carbon usage data for the current user (or sample data if no user)
    current_user = request.user if request.user.is_authenticated else None
    
    # Generate sample carbon usage data if no real data exists
    carbon_data = get_carbon_usage_data(current_user)
    carbon_by_category = get_carbon_by_category(current_user)
    monthly_trend = get_monthly_trend(current_user)
    
    context = {
        'parent': 'apps',
        'segment': 'charts',
        'carbon_data': json.dumps(carbon_data),
        'carbon_by_category': json.dumps(carbon_by_category),
        'monthly_trend': json.dumps(monthly_trend)
    }
    return render(request, 'charts/index.html', context)

def get_carbon_usage_data(user=None):
    """Get carbon usage data for charts"""
    # For now, return sample data - in future this will come from the database
    sample_data = {
        'categories': ['Transportation', 'Energy', 'Food', 'Waste', 'Other'],
        'values': [450.5, 320.8, 180.2, 95.3, 75.6],
        'colors': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
    }
    return sample_data

def get_carbon_by_category(user=None):
    """Get carbon usage breakdown by category"""
    # Sample data for pie chart
    sample_data = [
        {'category': 'Transportation', 'amount': 450.5, 'percentage': 40.2},
        {'category': 'Energy', 'amount': 320.8, 'percentage': 28.6},
        {'category': 'Food', 'amount': 180.2, 'percentage': 16.1},
        {'category': 'Waste', 'amount': 95.3, 'percentage': 8.5},
        {'category': 'Other', 'amount': 75.6, 'percentage': 6.6}
    ]
    return sample_data

def get_monthly_trend(user=None):
    """Get monthly carbon usage trend"""
    # Sample data for line chart showing last 6 months
    months = ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    your_usage = [1150, 1230, 980, 1420, 1100, 1050]
    average_usage = [1200, 1180, 1220, 1350, 1280, 1150]
    
    return {
        'months': months,
        'your_usage': your_usage,
        'average_usage': average_usage
    }
