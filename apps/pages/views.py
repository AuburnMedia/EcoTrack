import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from .forms import (
    InitialSurveyForm,
    WeeklyCheckupForm,
    UserOnboardingForm,
    UserProfileForm,
)
from .models import InitialSurveyResult, WeeklyCheckupResult, UserProfile
from apps.charts.models import CarbonGoal
from .decorators import onboarding_required
from .carbon_calculator import CarbonCalculator


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            # Create an empty profile (onboarding_completed = False)
            UserProfile.objects.create(user=user)
            # Redirect to onboarding
            return redirect("onboarding")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register.html", {"form": form})


@login_required
def onboarding(request):
    # Check if user has already completed onboarding
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.onboarding_completed:
            return redirect("index")
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == "POST":
        form = UserOnboardingForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.onboarding_completed = True
            profile.save()

            # Create initial carbon goal
            current_month = timezone.now().replace(day=1)
            CarbonGoal.objects.create(
                user=request.user,
                month=current_month,
                target_amount=profile.carbon_goal,
            )

            #messages.success(
            #    request,
            #    "Welcome to EcoTrack! Now, let's gather some information about your carbon footprint.",
            #)
            return redirect("initial_survey")
    else:
        form = UserOnboardingForm(instance=profile)

    return render(request, "pages/onboarding.html", {"form": form})


@login_required
@onboarding_required
def index(request):
    # Check if user needs to complete onboarding
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.onboarding_completed:
            return redirect("onboarding")
    except UserProfile.DoesNotExist:
        return redirect("onboarding")

    # Check if user needs to complete initial survey
    if not InitialSurveyResult.objects.filter(user=request.user).exists():
        #messages.info(
        #    request,
        #    "Please complete the initial survey to start tracking your carbon footprint.",
        #)
        return redirect("initial_survey")

    context = {}

    if request.user.is_authenticated:
        # Get initial survey and weekly checkups
        initial_survey = (
            InitialSurveyResult.objects.filter(user=request.user)
            .order_by("-date_submitted")
            .first()
        )
        weekly_checkups = WeeklyCheckupResult.objects.filter(
            user=request.user
        ).order_by("-date_submitted")[:12]

        # Get current carbon goal
        current_month = timezone.now().replace(day=1)
        current_goal = CarbonGoal.objects.filter(
            user=request.user, month=current_month
        ).first()

        # Area chart data - last 7 weekly checkups reversed for chronological order
        last_7_checkups = list(reversed(weekly_checkups[:7])) if weekly_checkups else []
        if last_7_checkups:
            area_chart_data = {
                "labels": [
                    checkup.date_submitted.strftime("%b %d")
                    for checkup in last_7_checkups
                ],
                "weekly_totals": [
                    float(checkup.weekly_total) for checkup in last_7_checkups
                ],
                "monthly_estimates": [
                    float(checkup.monthly_estimate) for checkup in last_7_checkups
                ],
            }
        else:
            area_chart_data = None

        # Previous results for table
        previous_results = []
        # Iterate through checkups to calculate percentage change from the previous one
        for i, checkup in enumerate(weekly_checkups):
            pct_change = None
            # Find the previous checkup (the next one in the list, since it's sorted descending)
            if i + 1 < len(weekly_checkups):
                prev_checkup = weekly_checkups[i + 1]
                if prev_checkup.weekly_total > 0:
                    pct_change = (
                        (checkup.weekly_total - prev_checkup.weekly_total)
                        / prev_checkup.weekly_total
                    ) * 100

            previous_results.append(
                {
                    "date": checkup.date_submitted,
                    "carbon": checkup.weekly_total,
                    "pct_change": pct_change,
                    "monthly_est": checkup.monthly_estimate,
                }
            )

        # Current usage stats
        latest_checkup = weekly_checkups.first() if weekly_checkups else None
        current_usage = {
            "weekly_total": latest_checkup.weekly_total if latest_checkup else 0,
            "monthly_estimate": latest_checkup.monthly_estimate
            if latest_checkup
            else 0,
            "pct_change": previous_results[0]["pct_change"]
            if previous_results and "pct_change" in previous_results[0]
            else None,
        }

        # Time since last checkup
        time_since_last = None
        if latest_checkup:
            time_since_last = (timezone.now() - latest_checkup.date_submitted).days

        # Carbon usage chart data - improved logic to always show meaningful trend data
        monthly_data = []
        if weekly_checkups:
            # Always show individual weekly data for better visualization
            # Take the most recent 6 weeks to show a good trend
            recent_checkups = list(reversed(weekly_checkups[:6]))
            for i, checkup in enumerate(recent_checkups):
                # Use relative week labels for better readability
                weeks_ago = len(recent_checkups) - i - 1
                if weeks_ago == 0:
                    label = "This Week"
                elif weeks_ago == 1:
                    label = "Last Week"
                else:
                    label = f"{weeks_ago} Weeks Ago"

                monthly_data.append(
                    {"month": label, "average": float(checkup.weekly_total)}
                )

        # Calculate goal progress based on current goal and baseline
        current = float(latest_checkup.monthly_estimate) if latest_checkup else 0
        goal_progress = 0

        if (
            current_goal
            and current_goal.target_amount > 0
            and current >= 0
            and initial_survey
        ):
            baseline = float(initial_survey.monthly_total)
            target = float(current_goal.target_amount)

            # Check if current usage is at or below target (achieved goal)
            if current <= target:
                goal_progress = 100
            # Check if current usage exceeds baseline (no progress)
            elif current >= baseline:
                goal_progress = 0
            # Calculate progress for values between baseline and target
            else:
                total_reduction_needed = baseline - target
                reduction_achieved = baseline - current
                goal_progress = (reduction_achieved / total_reduction_needed) * 100
                goal_progress = max(0, min(100, goal_progress))
        elif initial_survey and current > 0:
            # Fall back to simple baseline comparison if no goal is set
            baseline = float(initial_survey.monthly_total)
            if current >= baseline:
                goal_progress = 0
            else:
                reduction = baseline - current
                goal_progress = min(100, (reduction / baseline) * 100)

        # Ensure time calculations are valid
        time_since_last = (
            (timezone.now() - latest_checkup.date_submitted).days
            if latest_checkup
            else None
        )
        days_until_next = max(0, 7 - (time_since_last or 0))  # Ensure non-negative

        # Update current goal's current_amount if we have a latest checkup
        if current_goal and latest_checkup:
            current_goal.current_amount = latest_checkup.monthly_estimate
            current_goal.save()

        context.update(
            {
                "initial_survey": initial_survey,
                "area_chart_data": json.dumps(area_chart_data)
                if area_chart_data
                else None,
                "previous_results": previous_results,
                "current_usage": current_usage,
                "time_since_last": time_since_last
                or 0,  # Ensure we don't send None to template
                "days_until_next": days_until_next,
                "monthly_data": json.dumps(monthly_data) if monthly_data else None,
                "goal_progress": round(goal_progress, 1),
                "show_estimator": not initial_survey or not latest_checkup,
                "current_goal": current_goal,
            }
        )

    return render(request, "pages/index.html", context)


@login_required
@onboarding_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    current_month = timezone.now().replace(day=1)
    current_goal = CarbonGoal.objects.filter(
        user=request.user, month=current_month
    ).first()

    initial_survey = (
        InitialSurveyResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )
    last_checkup = (
        WeeklyCheckupResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()

            goal_value = profile.carbon_goal or 0
            carbon_goal, created_goal = CarbonGoal.objects.get_or_create(
                user=request.user,
                month=current_month,
                defaults={"target_amount": goal_value, "current_amount": 0},
            )
            if not created_goal and carbon_goal.target_amount != goal_value:
                carbon_goal.target_amount = goal_value
                carbon_goal.save(update_fields=["target_amount"])
            current_goal = carbon_goal

            #messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)

    time_since_last_checkup = (
        (timezone.now() - last_checkup.date_submitted).days if last_checkup else None
    )

    goal_progress = None
    if current_goal and last_checkup:
        current_estimate = float(last_checkup.monthly_estimate or 0)
        target_amount = float(current_goal.target_amount or 0)
        if target_amount > 0:
            if current_estimate <= target_amount:
                goal_progress = 100.0
            elif initial_survey:
                baseline = float(initial_survey.monthly_total or 0)
                if baseline > target_amount:
                    if current_estimate >= baseline:
                        goal_progress = 0.0
                    else:
                        total_reduction_needed = baseline - target_amount
                        reduction_achieved = baseline - current_estimate
                        if total_reduction_needed > 0:
                            goal_progress = max(
                                0.0,
                                min(
                                    100.0,
                                    (reduction_achieved / total_reduction_needed) * 100,
                                ),
                            )
            else:
                # Without baseline data, show relative progress towards target
                if current_estimate > 0:
                    ratio = target_amount / current_estimate
                    goal_progress = max(0.0, min(100.0, ratio * 100))

    context = {
        "form": form,
        "profile": profile,
        "current_goal": current_goal,
        "initial_survey": initial_survey,
        "last_checkup": last_checkup,
        "time_since_last_checkup": time_since_last_checkup,
        "goal_progress": goal_progress,
        "segment": "profile",
    }

    return render(request, "pages/profile.html", context)


@login_required
@onboarding_required
def survey_dashboard(request):
    initial_survey = (
        InitialSurveyResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )
    weekly_checkups = WeeklyCheckupResult.objects.filter(user=request.user).order_by(
        "-date_submitted"
    )[:12]

    initial_survey = (
        InitialSurveyResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )
    weekly_checkups = WeeklyCheckupResult.objects.filter(user=request.user).order_by(
        "-date_submitted"
    )[:12]

    # Prepare chart data with better error handling
    chart_data = {
        "labels": [
            checkup.date_submitted.strftime("%Y-%m-%d")
            for checkup in reversed(weekly_checkups)
        ],
        "weekly_totals": [
            float(checkup.weekly_total or 0) for checkup in reversed(weekly_checkups)
        ],
        "monthly_estimates": [
            float(checkup.monthly_estimate or 0)
            for checkup in reversed(weekly_checkups)
        ],
    }

    # JSON serialize the chart data
    chart_data = {
        "labels": json.dumps(chart_data["labels"]),
        "weekly_totals": json.dumps(chart_data["weekly_totals"]),
        "monthly_estimates": json.dumps(chart_data["monthly_estimates"]),
    }

    context = {
        "initial_survey": initial_survey,
        "weekly_checkups": weekly_checkups,
        "chart_data": chart_data,
    }
    return render(request, "pages/survey_dashboard.html", context)


@login_required
def initial_survey(request):
    # Check if user has completed onboarding
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.onboarding_completed:
            #messages.error(request, "Please complete the onboarding process first.")
            return redirect("onboarding")
    except UserProfile.DoesNotExist:
        return redirect("onboarding")

    # Check if user already has an initial survey
    if InitialSurveyResult.objects.filter(user=request.user).exists():
        #messages.info(request, "You have already completed the initial survey.")
        return redirect("survey_dashboard")

    if request.method == "POST":
        form = InitialSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.user = request.user

            # Calculate carbon footprint
            data = form.cleaned_data
            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return redirect("onboarding")

            # Create data dict with profile and form data
            survey_data = {
                **data,  # Form data
                "household_size": profile.household_size,
                "home_type": profile.house_type,
            }

            results = CarbonCalculator.calculate_initial_survey(survey_data)

            # Update survey with calculated fields
            for key, value in results.items():
                setattr(survey, key, value)

            survey.save()
            #messages.success(request, "Initial survey completed successfully!")
            return redirect("survey_dashboard")
    else:
        form = InitialSurveyForm()

    return render(request, "pages/initial_survey.html", {"form": form})


@login_required
@onboarding_required
def weekly_checkup(request):
    last_checkup = (
        WeeklyCheckupResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )
    last_checkup = (
        WeeklyCheckupResult.objects.filter(user=request.user)
        .order_by("-date_submitted")
        .first()
    )

    if request.method == "POST":
        form = WeeklyCheckupForm(request.POST)
        if form.is_valid():
            checkup = form.save(commit=False)
            checkup.user = request.user

            # Get last week's total for comparison
            last_week_total = last_checkup.weekly_total if last_checkup else None

            # Calculate carbon footprint
            data = form.cleaned_data
            results = CarbonCalculator.calculate_weekly_checkup(data, last_week_total)

            # Update checkup with calculated fields
            for key, value in results.items():
                setattr(checkup, key, value)

            checkup.save()
            #messages.success(request, "Weekly checkup completed successfully!")
            return redirect("survey_dashboard")
    else:
        form = WeeklyCheckupForm()

    return render(request, "pages/weekly_checkup.html", {"form": form})
