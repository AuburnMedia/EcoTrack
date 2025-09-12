from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from apps.charts.models import CarbonGoal
from apps.pages.models import InitialSurveyResult, WeeklyCheckupResult, UserProfile
from .forms import CarbonGoalForm
import json
from django.contrib.auth.decorators import login_required
from apps.pages.decorators import onboarding_required

# Create your views here.


@login_required
@onboarding_required
def manage_carbon_goal(request):
    # Get or create current month's goal
    current_month = timezone.now().replace(day=1)
    goal, created = CarbonGoal.objects.get_or_create(
        user=request.user,
        month=current_month,
        defaults={"target_amount": 0, "current_amount": 0},
    )

    if request.method == "POST":
        form = CarbonGoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "Carbon goal updated successfully!")
            return redirect("index")
    else:
        form = CarbonGoalForm(instance=goal)

    context = {
        "form": form,
        "current_goal": goal,
        "parent": "apps",
        "segment": "carbon_goal",
    }
    return render(request, "charts/manage_goal.html", context)


@login_required
@onboarding_required
def index(request):
    # Get carbon usage data for the current user
    current_user = request.user if request.user.is_authenticated else None

    # Get real user data instead of sample data
    carbon_data = get_carbon_usage_data(current_user)
    carbon_by_category = get_carbon_by_category(current_user)
    monthly_trend = get_monthly_trend(current_user)

    # Get current goal
    current_month = timezone.now().replace(day=1)
    current_goal = CarbonGoal.objects.filter(
        user=current_user, month=current_month
    ).first()

    context = {
        "parent": "apps",
        "segment": "charts",
        "carbon_data": json.dumps(carbon_data),
        "carbon_by_category": json.dumps(carbon_by_category),
        "monthly_trend": json.dumps(monthly_trend),
        "current_goal": current_goal,
    }
    return render(request, "charts/index.html", context)


def get_carbon_usage_data(user=None):
    """Get carbon usage data for charts based on user's initial survey"""
    if user and user.is_authenticated:
        try:
            # Get the user's most recent initial survey
            initial_survey = InitialSurveyResult.objects.filter(user=user).latest(
                "date_submitted"
            )

            # Calculate category breakdowns based on survey data
            # These are estimated breakdowns based on the total monthly footprint
            total_monthly = initial_survey.monthly_total

            # Estimate category breakdown (simplified calculation)
            categories = ["Transportation", "Energy", "Food", "Waste", "Other"]

            # Transportation: car type and flights influence
            transport_factor = 0.3  # Default 30%
            if initial_survey.car_type == "NONE":
                transport_factor = 0.15
            elif initial_survey.car_type in ["HYBRID", "ELEC"]:
                transport_factor = 0.25
            elif initial_survey.flights_per_year in ["1LONG", "MULTLONG"]:
                transport_factor = 0.4

            # Energy: home type and heating influence
            energy_factor = 0.35  # Default 35%
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.house_type == "APT":
                    energy_factor = 0.25
                elif profile.house_type == "LARGE":
                    energy_factor = 0.4
            except UserProfile.DoesNotExist:
                # Use default energy factor if profile doesn't exist
                pass

            if initial_survey.renewable_pct >= 50:
                energy_factor *= 0.7  # Reduce if using renewables

            # Adjust other categories proportionally
            remaining = 1.0 - transport_factor - energy_factor
            food_factor = remaining * 0.4
            waste_factor = remaining * 0.3
            other_factor = remaining * 0.3

            values = [
                round(total_monthly * transport_factor, 1),
                round(total_monthly * energy_factor, 1),
                round(total_monthly * food_factor, 1),
                round(total_monthly * waste_factor, 1),
                round(total_monthly * other_factor, 1),
            ]

            return {
                "categories": categories,
                "values": values,
                "colors": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
            }
        except InitialSurveyResult.DoesNotExist:
            pass

    # Fallback to sample data if no user data available
    sample_data = {
        "categories": ["Transportation", "Energy", "Food", "Waste", "Other"],
        "values": [450.5, 320.8, 180.2, 95.3, 75.6],
        "colors": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
    }
    return sample_data


def get_carbon_by_category(user=None):
    """Get carbon usage breakdown by category for pie chart"""
    carbon_data = get_carbon_usage_data(user)

    total = sum(carbon_data["values"])
    sample_data = []

    for i, category in enumerate(carbon_data["categories"]):
        amount = carbon_data["values"][i]
        percentage = round((amount / total) * 100, 1) if total > 0 else 0
        sample_data.append(
            {"category": category, "amount": amount, "percentage": percentage}
        )

    return sample_data


def get_monthly_trend(user=None):
    """Get monthly carbon usage trend from weekly checkups"""
    if user and user.is_authenticated:
        try:
            # Get user's weekly checkups from last 6 months
            six_months_ago = timezone.now() - timedelta(days=180)
            weekly_checkups = WeeklyCheckupResult.objects.filter(
                user=user, date_submitted__gte=six_months_ago
            ).order_by("date_submitted")

            if weekly_checkups.exists():
                # Group by month and calculate averages
                monthly_data = {}
                for checkup in weekly_checkups:
                    month_key = checkup.date_submitted.strftime("%b")
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    monthly_data[month_key].append(checkup.monthly_estimate)

                months = list(monthly_data.keys())[-6:]  # Last 6 months
                your_usage = []

                for month in months:
                    if month in monthly_data:
                        avg_usage = sum(monthly_data[month]) / len(monthly_data[month])
                        your_usage.append(round(avg_usage, 1))
                    else:
                        your_usage.append(0)

                
                average_usage = [850.0] * len(months)

                return {
                    "months": months,
                    "your_usage": your_usage,
                    "average_usage": average_usage,
                }
        except Exception:
            pass

    # Fallback to sample data
    months = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    your_usage = [1150, 1230, 980, 1420, 1100, 1050]
    average_usage = [1000.0] * len(months)  # Flat 1000kg line

    return {"months": months, "your_usage": your_usage, "average_usage": average_usage}
