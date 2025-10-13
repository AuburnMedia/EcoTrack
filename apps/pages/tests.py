from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from .models import UserProfile, InitialSurveyResult, WeeklyCheckupResult, Product
from .forms import UserOnboardingForm, InitialSurveyForm, WeeklyCheckupForm
from .carbon_calculator import CarbonCalculator
from .decorators import onboarding_required
from apps.charts.models import CarbonGoal


class UserProfileModelTest(TestCase):
    """Tests for UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_create_user_profile(self):
        """Test creating a user profile"""
        profile = UserProfile.objects.create(
            user=self.user,
            display_name="Test User",
            household_size=3,
            house_type="SMALL",
            carbon_goal=500,
            onboarding_completed=True,
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.display_name, "Test User")
        self.assertEqual(profile.household_size, 3)
        self.assertEqual(profile.house_type, "SMALL")
        self.assertEqual(profile.carbon_goal, 500)
        self.assertTrue(profile.onboarding_completed)

    def test_user_profile_str(self):
        """Test string representation of UserProfile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), "testuser's Profile")

    def test_user_profile_defaults(self):
        """Test default values for UserProfile"""
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.household_size, 1)
        self.assertEqual(profile.house_type, "APT")
        self.assertFalse(profile.onboarding_completed)


class InitialSurveyResultModelTest(TestCase):
    """Tests for InitialSurveyResult model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_create_initial_survey(self):
        """Test creating an initial survey result"""
        survey = InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="YES",
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
            monthly_per_person=30.83,
        )
        self.assertEqual(survey.user, self.user)
        self.assertEqual(survey.primary_heating, "GAS")
        self.assertEqual(survey.monthly_total, 92.5)

    def test_initial_survey_str(self):
        """Test string representation of InitialSurveyResult"""
        survey = InitialSurveyResult.objects.create(
            user=self.user,
            primary_heating="GAS",
            appliance_use="DAILY",
            lighting_type="LED",
            air_conditioning="NO",
            car_type="NONE",
            device_time="LT2",
            renewable_pct=0,
            flights_per_year="NONE",
            public_transport="NEVER",
            compost_waste="NO",
            clothes_drying="DRYER",
            buy_secondhand="NEVER",
            monthly_raw_total=50.0,
            home_electric_subtotal=20.0,
            renewable_discount=0.0,
            monthly_total=50.0,
            monthly_per_person=50.0,
        )
        self.assertIn("testuser", str(survey))
        self.assertIn("Initial Survey", str(survey))


class WeeklyCheckupResultModelTest(TestCase):
    """Tests for WeeklyCheckupResult model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_create_weekly_checkup(self):
        """Test creating a weekly checkup result"""
        checkup = WeeklyCheckupResult.objects.create(
            user=self.user,
            heating_usage="SOME",
            appliance_usage="REG",
            daily_transport="MIXED",
            weekly_travel="REGION",
            vehicle_type="STANDARD",
            energy_source="STANDARD",
            water_usage="MODERATE",
            waste_generation="MEDIUM",
            weekly_consumption="MODERATE",
            weekly_raw_total=100.0,
            home_electric_subtotal=30.0,
            renewable_discount=0.0,
            weekly_total=100.0,
            pct_change_from_last=5.0,
            monthly_estimate=400.0,
            monthly_estimate_per_person=200.0,
        )
        self.assertEqual(checkup.user, self.user)
        self.assertEqual(checkup.heating_usage, "SOME")
        self.assertEqual(checkup.weekly_total, 100.0)

    def test_weekly_checkup_str(self):
        """Test string representation of WeeklyCheckupResult"""
        checkup = WeeklyCheckupResult.objects.create(
            user=self.user,
            heating_usage="OFF",
            appliance_usage="OPT",
            daily_transport="ACTIVE",
            weekly_travel="LOCAL",
            vehicle_type="NONE",
            energy_source="FULL_GREEN",
            water_usage="MINIMAL",
            waste_generation="MINIMAL",
            weekly_consumption="NONE",
            weekly_raw_total=20.0,
            home_electric_subtotal=10.0,
            renewable_discount=8.0,
            weekly_total=12.0,
            pct_change_from_last=-10.0,
            monthly_estimate=48.0,
            monthly_estimate_per_person=48.0,
        )
        self.assertIn("testuser", str(checkup))
        self.assertIn("Weekly Checkup", str(checkup))


class ProductModelTest(TestCase):
    """Tests for Product model"""

    def test_create_product(self):
        """Test creating a product"""
        product = Product.objects.create(
            name="Eco-Friendly Water Bottle",
            info="Reusable water bottle",
            price=15,
        )
        self.assertEqual(product.name, "Eco-Friendly Water Bottle")
        self.assertEqual(product.info, "Reusable water bottle")
        self.assertEqual(product.price, 15)

    def test_product_str(self):
        """Test string representation of Product"""
        product = Product.objects.create(name="Test Product")
        self.assertEqual(str(product), "Test Product")


class UserOnboardingFormTest(TestCase):
    """Tests for UserOnboardingForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            "display_name": "John Doe",
            "household_size": 3,
            "house_type": "SMALL",
            "carbon_goal": 500,
        }
        form = UserOnboardingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_household_size(self):
        """Test form with invalid household size"""
        form_data = {
            "display_name": "John Doe",
            "household_size": 0,
            "house_type": "SMALL",
            "carbon_goal": 500,
        }
        form = UserOnboardingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("household_size", form.errors)

    def test_negative_household_size(self):
        """Test form with negative household size"""
        form_data = {
            "display_name": "John Doe",
            "household_size": -1,
            "house_type": "SMALL",
            "carbon_goal": 500,
        }
        form = UserOnboardingForm(data=form_data)
        self.assertFalse(form.is_valid())


class InitialSurveyFormTest(TestCase):
    """Tests for InitialSurveyForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            "primary_heating": "GAS",
            "appliance_use": "DAILY",
            "lighting_type": "LED",
            "air_conditioning": "YES",
            "car_type": "PETROL",
            "device_time": "4-8",
            "renewable_pct": 25,
            "flights_per_year": "1SHORT",
            "public_transport": "WEEKLY",
            "compost_waste": "YES",
            "clothes_drying": "LINE",
            "buy_secondhand": "SOME",
        }
        form = InitialSurveyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_required_field(self):
        """Test form with missing required field"""
        form_data = {
            "primary_heating": "GAS",
            # Missing other required fields
        }
        form = InitialSurveyForm(data=form_data)
        self.assertFalse(form.is_valid())


class WeeklyCheckupFormTest(TestCase):
    """Tests for WeeklyCheckupForm"""

    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            "heating_usage": "SOME",
            "appliance_usage": "REG",
            "daily_transport": "MIXED",
            "weekly_travel": "REGION",
            "vehicle_type": "STANDARD",
            "energy_source": "STANDARD",
            "water_usage": "MODERATE",
            "waste_generation": "MEDIUM",
            "weekly_consumption": "MODERATE",
        }
        form = WeeklyCheckupForm(data=form_data)
        self.assertTrue(form.is_valid())


class CarbonCalculatorTest(TestCase):
    """Tests for CarbonCalculator utility"""

    def test_calculate_initial_survey(self):
        """Test initial survey calculation"""
        data = {
            "home_type": "SMALL",
            "primary_heating": "GAS",
            "appliance_use": "DAILY",
            "lighting_type": "LED",
            "air_conditioning": "NO",
            "car_type": "PETROL",
            "device_time": "4-8",
            "renewable_pct": 0,
            "flights_per_year": "NONE",
            "public_transport": "NEVER",
            "compost_waste": "NO",
            "clothes_drying": "DRYER",
            "buy_secondhand": "NEVER",
            "household_size": 2,
        }
        result = CarbonCalculator.calculate_initial_survey(data)

        self.assertIn("monthly_raw_total", result)
        self.assertIn("home_electric_subtotal", result)
        self.assertIn("renewable_discount", result)
        self.assertIn("monthly_total", result)
        self.assertIn("monthly_per_person", result)

        # Verify calculations are correct
        self.assertGreater(result["monthly_raw_total"], 0)
        self.assertEqual(result["renewable_discount"], 0)  # No renewable energy
        self.assertEqual(result["monthly_total"], result["monthly_raw_total"])
        self.assertEqual(
            result["monthly_per_person"], result["monthly_total"] / 2
        )

    def test_calculate_initial_survey_with_renewables(self):
        """Test initial survey calculation with renewable energy"""
        data = {
            "home_type": "APT",
            "primary_heating": "ELEC",
            "appliance_use": "WEEKLY",
            "lighting_type": "LED",
            "air_conditioning": "NO",
            "car_type": "ELEC",
            "device_time": "LT2",
            "renewable_pct": 100,
            "flights_per_year": "NONE",
            "public_transport": "DAILY",
            "compost_waste": "YES",
            "clothes_drying": "LINE",
            "buy_secondhand": "OFTEN",
            "household_size": 1,
        }
        result = CarbonCalculator.calculate_initial_survey(data)

        # Verify renewable discount is applied
        self.assertGreater(result["renewable_discount"], 0)
        self.assertEqual(
            result["renewable_discount"], result["home_electric_subtotal"]
        )

    def test_calculate_weekly_checkup(self):
        """Test weekly checkup calculation"""
        data = {
            "heating_usage": "SOME",
            "appliance_usage": "REG",
            "daily_transport": "MIXED",
            "weekly_travel": "LOCAL",
            "vehicle_type": "STANDARD",
            "energy_source": "STANDARD",
            "water_usage": "MODERATE",
            "waste_generation": "MEDIUM",
            "weekly_consumption": "MODERATE",
        }
        result = CarbonCalculator.calculate_weekly_checkup(data, household_size=2)

        self.assertIn("weekly_raw_total", result)
        self.assertIn("home_electric_subtotal", result)
        self.assertIn("renewable_discount", result)
        self.assertIn("weekly_total", result)
        self.assertIn("pct_change_from_last", result)
        self.assertIn("monthly_estimate", result)
        self.assertIn("monthly_estimate_per_person", result)

        self.assertGreater(result["weekly_total"], 0)
        self.assertIsNone(result["pct_change_from_last"])  # No last week total
        self.assertEqual(result["monthly_estimate"], result["weekly_total"] * 4)

    def test_calculate_weekly_checkup_with_last_week(self):
        """Test weekly checkup calculation with last week's data"""
        data = {
            "heating_usage": "SOME",
            "appliance_usage": "REG",
            "daily_transport": "MIXED",
            "weekly_travel": "LOCAL",
            "vehicle_type": "STANDARD",
            "energy_source": "STANDARD",
            "water_usage": "MODERATE",
            "waste_generation": "MEDIUM",
            "weekly_consumption": "MODERATE",
        }
        result = CarbonCalculator.calculate_weekly_checkup(
            data, last_week_total=100.0, household_size=2
        )

        # Verify percentage change is calculated
        self.assertIsNotNone(result["pct_change_from_last"])
        self.assertIsInstance(result["pct_change_from_last"], (int, float))

    def test_calculate_weekly_checkup_green_energy(self):
        """Test weekly checkup calculation with green energy"""
        data = {
            "heating_usage": "OFF",
            "appliance_usage": "OPT",
            "daily_transport": "ACTIVE",
            "weekly_travel": "LOCAL",
            "vehicle_type": "ELECTRIC",
            "energy_source": "FULL_GREEN",
            "water_usage": "MINIMAL",
            "waste_generation": "MINIMAL",
            "weekly_consumption": "NONE",
        }
        result = CarbonCalculator.calculate_weekly_checkup(data, household_size=1)

        # Should have lower total due to green energy bonus
        self.assertGreater(result["renewable_discount"], 0)


class OnboardingRequiredDecoratorTest(TestCase):
    """Tests for onboarding_required decorator"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_redirect_when_not_onboarded(self):
        """Test that users without onboarding are redirected"""
        UserProfile.objects.create(user=self.user, onboarding_completed=False)
        self.client.login(username="testuser", password="testpass123")

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/onboarding"))

    def test_access_when_onboarded(self):
        """Test that onboarded users can access protected views"""
        UserProfile.objects.create(user=self.user, onboarding_completed=True)
        self.client.login(username="testuser", password="testpass123")

        # This might redirect to initial_survey if not completed
        response = self.client.get(reverse("index"))
        # Should not redirect to onboarding
        if response.status_code == 302:
            self.assertNotIn("/onboarding", response.url)


class RegisterViewTest(TestCase):
    """Tests for register view"""

    def setUp(self):
        self.client = Client()

    def test_register_get(self):
        """Test GET request to register view"""
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_post_valid(self):
        """Test POST request with valid data"""
        data = {
            "username": "newuser",
            "password1": "complex_pass_123",
            "password2": "complex_pass_123",
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)
        # Should create user and redirect to onboarding
        self.assertTrue(User.objects.filter(username="newuser").exists())
        user = User.objects.get(username="newuser")
        self.assertTrue(UserProfile.objects.filter(user=user).exists())


class OnboardingViewTest(TestCase):
    """Tests for onboarding view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")

    def test_onboarding_requires_login(self):
        """Test that onboarding requires authentication"""
        response = self.client.get(reverse("onboarding"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_onboarding_get(self):
        """Test GET request to onboarding view"""
        self.client.login(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, onboarding_completed=False)
        response = self.client.get(reverse("onboarding"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/onboarding.html")

    def test_onboarding_already_completed(self):
        """Test that completed onboarding redirects to index"""
        self.client.login(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, onboarding_completed=True)
        response = self.client.get(reverse("onboarding"))
        self.assertEqual(response.status_code, 302)

    def test_onboarding_post_valid(self):
        """Test POST request with valid data"""
        self.client.login(username="testuser", password="testpass123")
        UserProfile.objects.create(user=self.user, onboarding_completed=False)
        data = {
            "display_name": "Test User",
            "household_size": 2,
            "house_type": "SMALL",
            "carbon_goal": 400,
        }
        response = self.client.post(reverse("onboarding"), data)
        self.assertEqual(response.status_code, 302)

        # Verify profile was updated
        profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(profile.onboarding_completed)
        self.assertEqual(profile.household_size, 2)

        # Verify carbon goal was created
        current_month = timezone.now().replace(day=1)
        self.assertTrue(
            CarbonGoal.objects.filter(user=self.user, month=current_month).exists()
        )


class InitialSurveyViewTest(TestCase):
    """Tests for initial_survey view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
            onboarding_completed=True,
        )

    def test_initial_survey_requires_login(self):
        """Test that initial survey requires authentication"""
        response = self.client.get(reverse("initial_survey"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_initial_survey_requires_onboarding(self):
        """Test that initial survey requires completed onboarding"""
        self.profile.onboarding_completed = False
        self.profile.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("initial_survey"))
        self.assertEqual(response.status_code, 302)

    def test_initial_survey_get(self):
        """Test GET request to initial survey view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("initial_survey"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/initial_survey.html")

    def test_initial_survey_already_completed(self):
        """Test that completing initial survey twice redirects"""
        self.client.login(username="testuser", password="testpass123")
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
            monthly_raw_total=50.0,
            home_electric_subtotal=20.0,
            renewable_discount=0.0,
            monthly_total=50.0,
            monthly_per_person=25.0,
        )
        response = self.client.get(reverse("initial_survey"))
        self.assertEqual(response.status_code, 302)


class WeeklyCheckupViewTest(TestCase):
    """Tests for weekly_checkup view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
            onboarding_completed=True,
        )

    def test_weekly_checkup_requires_login(self):
        """Test that weekly checkup requires authentication"""
        response = self.client.get(reverse("weekly_checkup"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_weekly_checkup_requires_onboarding(self):
        """Test that weekly checkup requires completed onboarding"""
        self.profile.onboarding_completed = False
        self.profile.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("weekly_checkup"))
        self.assertEqual(response.status_code, 302)

    def test_weekly_checkup_get(self):
        """Test GET request to weekly checkup view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("weekly_checkup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/weekly_checkup.html")


class SurveyDashboardViewTest(TestCase):
    """Tests for survey_dashboard view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = UserProfile.objects.create(
            user=self.user,
            household_size=2,
            house_type="SMALL",
            onboarding_completed=True,
        )

    def test_survey_dashboard_requires_login(self):
        """Test that survey dashboard requires authentication"""
        response = self.client.get(reverse("survey_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login", response.url)

    def test_survey_dashboard_requires_onboarding(self):
        """Test that survey dashboard requires completed onboarding"""
        self.profile.onboarding_completed = False
        self.profile.save()
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("survey_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_survey_dashboard_get(self):
        """Test GET request to survey dashboard view"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("survey_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/survey_dashboard.html")
