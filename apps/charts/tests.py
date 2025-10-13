from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import CarbonUsage, CarbonGoal
from .forms import CarbonGoalForm
from apps.pages.models import UserProfile, InitialSurveyResult, WeeklyCheckupResult
import json


class CarbonUsageModelTest(TestCase):
    """Tests for CarbonUsage model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_create_carbon_usage(self):
        """Test creating a carbon usage record"""
        usage = CarbonUsage.objects.create(
            user=self.user,
            category="transport",
            amount=45.5,
            description="Daily commute",
        )
        self.assertEqual(usage.user, self.user)
        self.assertEqual(usage.category, "transport")
        self.assertEqual(usage.amount, 45.5)
        self.assertEqual(usage.description, "Daily commute")

    def test_carbon_usage_str(self):
        """Test string representation of CarbonUsage"""
        usage = CarbonUsage.objects.create(
            user=self.user,
            category="energy",
            amount=120.0,
        )
        self.assertEqual(str(usage), "energy - 120.0kg CO2")

    def test_carbon_usage_ordering(self):
        """Test that carbon usage is ordered by date descending"""
        usage1 = CarbonUsage.objects.create(
            user=self.user,
            category="transport",
            amount=50.0,
            date=timezone.now().date() - timedelta(days=1),
        )
        usage2 = CarbonUsage.objects.create(
            user=self.user,
            category="energy",
            amount=60.0,
            date=timezone.now().date(),
        )
        usages = CarbonUsage.objects.all()
        self.assertEqual(usages[0], usage2)  # Most recent first


class CarbonGoalModelTest(TestCase):
    """Tests for CarbonGoal model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
        )

    def test_create_carbon_goal(self):
        """Test creating a carbon goal"""
        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,
            current_amount=350.0,
            month=current_month,
            achieved=False,
        )
        self.assertEqual(goal.user, self.user)
        self.assertEqual(goal.target_amount, 300.0)
        self.assertEqual(goal.current_amount, 350.0)
        self.assertFalse(goal.achieved)

    def test_carbon_goal_str(self):
        """Test string representation of CarbonGoal"""
        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,
            month=current_month,
        )
        expected_str = f"Goal for {current_month.strftime('%B %Y')}: 300.0kg CO2"
        self.assertEqual(str(goal), expected_str)

    def test_progress_percentage_no_baseline(self):
        """Test progress percentage when no baseline exists"""
        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,
            current_amount=350.0,
            month=current_month,
        )
        # Should return 0 if no baseline survey
        self.assertEqual(goal.progress_percentage, 0)

    def test_progress_percentage_with_baseline(self):
        """Test progress percentage calculation with baseline"""
        # Create baseline survey
        InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="PETROL",
            device_time="4-8",
            renewable_pct=0,
            flights_per_year="NONE",
            public_transport="NEVER",
            compost_waste="NO",
            clothes_drying="DRYER",
            buy_secondhand="NEVER",
            monthly_raw_total=500.0,
            home_electric_subtotal=100.0,
            renewable_discount=0.0,
            monthly_total=500.0,  # Baseline is 500
            monthly_per_person=250.0,
        )

        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,  # Target is 300
            current_amount=400.0,  # Current is 400
            month=current_month,
        )

        # Progress = (500 - 400) / (500 - 300) * 100 = 100/200 * 100 = 50%
        self.assertEqual(goal.progress_percentage, 50.0)

    def test_progress_percentage_goal_achieved(self):
        """Test progress percentage when goal is achieved"""
        # Create baseline survey
        InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="PETROL",
            device_time="4-8",
            renewable_pct=0,
            flights_per_year="NONE",
            public_transport="NEVER",
            compost_waste="NO",
            clothes_drying="DRYER",
            buy_secondhand="NEVER",
            monthly_raw_total=500.0,
            home_electric_subtotal=100.0,
            renewable_discount=0.0,
            monthly_total=500.0,
            monthly_per_person=250.0,
        )

        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,
            current_amount=250.0,  # Below target
            month=current_month,
        )

        # Should return 100% when goal is exceeded
        self.assertEqual(goal.progress_percentage, 100)

    def test_progress_percentage_exceeds_baseline(self):
        """Test progress percentage when current exceeds baseline"""
        # Create baseline survey
        InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="PETROL",
            device_time="4-8",
            renewable_pct=0,
            flights_per_year="NONE",
            public_transport="NEVER",
            compost_waste="NO",
            clothes_drying="DRYER",
            buy_secondhand="NEVER",
            monthly_raw_total=500.0,
            home_electric_subtotal=100.0,
            renewable_discount=0.0,
            monthly_total=500.0,
            monthly_per_person=250.0,
        )

        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.create(
            user=self.user,
            target_amount=300.0,
            current_amount=600.0,  # Worse than baseline
            month=current_month,
        )

        # Should return 0 when current exceeds baseline
        self.assertEqual(goal.progress_percentage, 0)


class CarbonGoalFormTest(TestCase):
    """Tests for CarbonGoalForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {"target_amount": 300.0}
        form = CarbonGoalForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_zero_target(self):
        """Test form with zero target amount"""
        form_data = {"target_amount": 0}
        form = CarbonGoalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("target_amount", form.errors)

    def test_invalid_negative_target(self):
        """Test form with negative target amount"""
        form_data = {"target_amount": -100.0}
        form = CarbonGoalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("target_amount", form.errors)


class ChartsViewsTest(TestCase):
    """Tests for charts views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
            onboarding_completed=True,
        )

    def test_charts_index_requires_login(self):
        """Test that charts index requires authentication"""
        response = self.client.get(reverse("charts"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_charts_index_requires_onboarding(self):
        """Test that charts index requires completed onboarding"""
        self.profile.onboarding_completed = False
        self.profile.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("charts"))
        self.assertEqual(response.status_code, 302)

    def test_charts_index_get(self):
        """Test GET request to charts index view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("charts"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "charts/index.html")

    def test_charts_index_with_data(self):
        """Test charts index with user data"""
        self.client.login(username="testuser", password="testpass123")

        # Create initial survey
        InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="PETROL",
            device_time="4-8",
            renewable_pct=25,
            flights_per_year="1SHORT",
            public_transport="WEEKLY",
            compost_waste="YES",
            clothes_drying="LINE",
            buy_secondhand="SOME",
            monthly_raw_total=100.0,
            home_electric_subtotal=30.0,
            renewable_discount=7.5,
            monthly_total=92.5,
            monthly_per_person=46.25,
        )

        response = self.client.get(reverse("charts"))
        self.assertEqual(response.status_code, 200)

        # Check that data is passed to template
        self.assertIn("carbon_data", response.context)
        self.assertIn("carbon_by_category", response.context)
        self.assertIn("monthly_trend", response.context)

    def test_manage_carbon_goal_requires_login(self):
        """Test that manage carbon goal requires authentication"""
        response = self.client.get(reverse("manage_carbon_goal"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_manage_carbon_goal_get(self):
        """Test GET request to manage carbon goal view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("manage_carbon_goal"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "charts/manage_goal.html")

    def test_manage_carbon_goal_post_valid(self):
        """Test POST request with valid data to manage carbon goal"""
        self.client.login(username="testuser", password="testpass123")
        data = {"target_amount": 350.0}
        response = self.client.post(reverse("manage_carbon_goal"), data)
        self.assertEqual(response.status_code, 302)

        # Verify goal was updated
        current_month = timezone.now().replace(day=1)
        goal = CarbonGoal.objects.get(user=self.user, month=current_month)
        self.assertEqual(goal.target_amount, 350.0)


class GetCarbonUsageDataTest(TestCase):
    """Tests for get_carbon_usage_data helper function"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
        )

    def test_get_carbon_usage_data_no_survey(self):
        """Test get_carbon_usage_data with no initial survey"""
        from apps.charts.views import get_carbon_usage_data

        data = get_carbon_usage_data(self.user)
        # Should return sample data
        self.assertIn("categories", data)
        self.assertIn("values", data)
        self.assertIn("colors", data)

    def test_get_carbon_usage_data_with_survey(self):
        """Test get_carbon_usage_data with initial survey"""
        from apps.charts.views import get_carbon_usage_data

        InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="PETROL",
            device_time="4-8",
            renewable_pct=0,
            flights_per_year="NONE",
            public_transport="NEVER",
            compost_waste="NO",
            clothes_drying="DRYER",
            buy_secondhand="NEVER",
            monthly_raw_total=100.0,
            home_electric_subtotal=30.0,
            renewable_discount=0.0,
            monthly_total=100.0,
            monthly_per_person=50.0,
        )

        data = get_carbon_usage_data(self.user)
        self.assertIn("categories", data)
        self.assertIn("values", data)
        self.assertEqual(len(data["categories"]), len(data["values"]))


class GetCarbonByCategoryTest(TestCase):
    """Tests for get_carbon_by_category helper function"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
        )

    def test_get_carbon_by_category(self):
        """Test get_carbon_by_category returns correct format"""
        from apps.charts.views import get_carbon_by_category

        data = get_carbon_by_category(self.user)
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("category", data[0])
            self.assertIn("amount", data[0])
            self.assertIn("percentage", data[0])


class GetMonthlyTrendTest(TestCase):
    """Tests for get_monthly_trend helper function"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
        )

    def test_get_monthly_trend_no_data(self):
        """Test get_monthly_trend with no weekly checkups"""
        from apps.charts.views import get_monthly_trend

        data = get_monthly_trend(self.user)
        # Should return sample data
        self.assertIn("months", data)
        self.assertIn("your_usage", data)
        self.assertIn("average_usage", data)

    def test_get_monthly_trend_with_data(self):
        """Test get_monthly_trend with weekly checkups"""
        from apps.charts.views import get_monthly_trend

        # Create weekly checkups
        for i in range(3):
            WeeklyCheckupResult.objects.create(
                user=self.user,
                date_submitted=timezone.now() - timedelta(weeks=i),
                heating_usage="SOME",
                appliance_usage="REG",
                daily_transport="MIXED",
                weekly_travel="LOCAL",
                vehicle_type="STANDARD",
                energy_source="STANDARD",
                water_usage="MODERATE",
                waste_generation="MEDIUM",
                weekly_consumption="MODERATE",
                weekly_raw_total=100.0,
                home_electric_subtotal=30.0,
                renewable_discount=0.0,
                weekly_total=100.0,
                pct_change_from_last=None,
                monthly_estimate=400.0,
                monthly_estimate_per_person=200.0,
            )

        data = get_monthly_trend(self.user)
        self.assertIn("months", data)
        self.assertIn("your_usage", data)
        self.assertIn("average_usage", data)
