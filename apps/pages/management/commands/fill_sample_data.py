from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.pages.models import WeeklyCheckupResult, UserProfile, InitialSurveyResult
from apps.pages.carbon_calculator import CarbonCalculator
import random


class Command(BaseCommand):
    help = "Fills the database with sample weekly checkup data for a specified user"

    def add_arguments(self, parser):
        parser.add_argument(
            "username", type=str, help="Username to create sample data for"
        )

    def handle(self, *args, **options):
        username = options["username"]
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User {username} does not exist"))
            return

        # Create or update user profile with onboarding data
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "display_name": username,
                "house_type": "SMALL",
                "carbon_goal": 2000,
                "household_size": 1,
                "onboarding_completed": True,
            },
        )

        if not created:
            # Update existing profile
            profile.display_name = username
            profile.house_type = "SMALL"
            profile.carbon_goal = 2000
            profile.onboarding_completed = True
            profile.save()

        from apps.charts.models import CarbonGoal

        current_month = timezone.now().replace(day=1)
        carbon_goal, goal_created = CarbonGoal.objects.get_or_create(
            user=user,
            month=current_month,
            defaults={
                "target_amount": profile.carbon_goal,
                "current_amount": 0,
                "achieved": False,
            },
        )
        if not goal_created:
            carbon_goal.target_amount = profile.carbon_goal
            carbon_goal.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated onboarding data and carbon goal for user {username}"
            )
        )

        survey_data = {
            "home_type": profile.house_type,
            "household_size": profile.household_size,
            "primary_heating": random.choices(
                ["ELEC", "GAS", "OIL", "NONE"], weights=[40, 30, 20, 10]
            )[0],
            "appliance_use": random.choices(
                ["DAILY", "WEEKLY", "OCCAS", "NEVER"], weights=[40, 30, 20, 10]
            )[0],
            "lighting_type": random.choices(
                ["LED", "CFL", "INC", "MIX"], weights=[40, 30, 10, 20]
            )[0],  # Favor LED
            "air_conditioning": random.choices(["YES", "NO"], weights=[30, 70])[
                0
            ],  # Favor no AC
            "car_type": random.choices(
                ["NONE", "PETROL", "DIESEL", "HYBRID", "ELEC"],
                weights=[15, 25, 20, 25, 15],
            )[0],
            "device_time": random.choices(
                ["LT2", "2-4", "4-8", "GT8"], weights=[20, 40, 30, 10]
            )[0],
            "flights_per_year": random.choices(
                ["NONE", "1SHORT", "2-4SHORT", "1LONG", "MULTLONG"],
                weights=[30, 35, 20, 10, 5],
            )[0],
            "public_transport": random.choices(
                ["NEVER", "OCCAS", "WEEKLY", "DAILY"], weights=[20, 30, 30, 20]
            )[0],
            "compost_waste": random.choices(["YES", "NO"], weights=[60, 40])[
                0
            ],  # Favor composting
            "clothes_drying": random.choices(
                ["LINE", "MIXED", "DRYER"], weights=[40, 40, 20]
            )[0],
            "buy_secondhand": random.choices(
                ["OFTEN", "SOME", "RARELY", "NEVER"], weights=[25, 35, 25, 15]
            )[0],
            "renewable_pct": random.choices(
                [0, 25, 50, 75, 100], weights=[15, 25, 30, 20, 10]
            )[0],
        }

        results = CarbonCalculator.calculate_initial_survey(survey_data)

        db_survey_data = survey_data.copy()
        db_survey_data.pop("home_type")
        db_survey_data.pop("household_size")

        survey, created = InitialSurveyResult.objects.get_or_create(
            user=user,
            defaults={
                **db_survey_data,
                "date_submitted": timezone.now(),
                "monthly_raw_total": results["monthly_raw_total"],
                "home_electric_subtotal": results["home_electric_subtotal"],
                "renewable_discount": results["renewable_discount"],
                "monthly_total": results["monthly_total"],
                "monthly_per_person": results["monthly_per_person"],
            },
        )

        if not created:
            # Update existing survey (excluding calculation-only fields)
            for key, value in db_survey_data.items():
                setattr(survey, key, value)
            survey.monthly_raw_total = results["monthly_raw_total"]
            survey.home_electric_subtotal = results["home_electric_subtotal"]
            survey.renewable_discount = results["renewable_discount"]
            survey.monthly_total = results["monthly_total"]
            survey.monthly_per_person = results["monthly_per_person"]
            survey.save()

        self.stdout.write(
            self.style.SUCCESS(f"Created/updated initial survey for user {username}")
        )

        # Choices for each field based on the model's choices
        CHOICES = {
            "heating_usage": ["OFF", "ECO", "SOME", "MOST"],
            "appliance_usage": ["OPT", "REG", "FREQ", "HEAVY"],
            "daily_transport": ["ACTIVE", "PUBLIC", "MIXED", "CAR"],
            "weekly_travel": ["LOCAL", "REGION", "LONG", "FLIGHT"],
            "vehicle_type": ["NONE", "ELECTRIC", "HYBRID", "STANDARD", "LARGE"],
            "energy_source": ["FULL_GREEN", "PARTIAL", "GREEN_OPT", "STANDARD"],
            "water_usage": ["MINIMAL", "MODERATE", "TYPICAL", "HIGH"],
            "waste_generation": ["MINIMAL", "LOW", "MEDIUM", "HIGH"],
            "weekly_consumption": ["NONE", "ESSENTIAL", "MODERATE", "HIGH"],
        }

        from tqdm import tqdm

        # Generate 30 weeks of data
        current_date = timezone.now()
        current_date = current_date - timezone.timedelta(
            days=current_date.weekday() + 1
        )
        # Set to end of day (23:59:59)
        current_date = current_date.replace(hour=23, minute=59, second=59)

        weeks_created = 0
        last_week_total = None

        # Create progress bar
        progress = tqdm(
            range(30),
            desc="Generating weekly data",
            unit="week",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} weeks [{elapsed}<{remaining}]",
        )

        for week in progress:
            date = current_date - timezone.timedelta(weeks=week)

            # Create checkup data with a tendency towards moderate choices
            # but occasional variation to show improvements and setbacks
            data = {
                "heating_usage": random.choices(
                    CHOICES["heating_usage"],
                    weights=[15, 40, 30, 15],  # Favor ECO and SOME
                )[0],
                "appliance_usage": random.choices(
                    CHOICES["appliance_usage"],
                    weights=[30, 40, 20, 10],  # Favor OPT and REG
                )[0],
                "daily_transport": random.choices(
                    CHOICES["daily_transport"],
                    weights=[20, 30, 30, 20],  # Balanced mix
                )[0],
                "weekly_travel": random.choices(
                    CHOICES["weekly_travel"],
                    weights=[40, 30, 20, 10],  # Favor local travel
                )[0],
                "vehicle_type": random.choices(
                    CHOICES["vehicle_type"],
                    weights=[20, 20, 30, 20, 10],  # Favor hybrid/electric
                )[0],
                "energy_source": random.choices(
                    CHOICES["energy_source"],
                    weights=[25, 30, 25, 20],  # Favor green energy
                )[0],
                "water_usage": random.choices(
                    CHOICES["water_usage"],
                    weights=[25, 35, 25, 15],  # Favor moderate usage
                )[0],
                "waste_generation": random.choices(
                    CHOICES["waste_generation"],
                    weights=[20, 35, 30, 15],  # Favor low waste
                )[0],
                "weekly_consumption": random.choices(
                    CHOICES["weekly_consumption"],
                    weights=[15, 40, 35, 10],  # Favor essential/moderate
                )[0],
            }

            # Calculate carbon impact using the CarbonCalculator
            results = CarbonCalculator.calculate_weekly_checkup(
                data, last_week_total, profile.household_size
            )

            # Force auto_now_add to use our date by temporarily disabling it
            WeeklyCheckupResult._meta.get_field("date_submitted").auto_now_add = False

            # Create the weekly checkup with the specific date
            WeeklyCheckupResult.objects.create(
                user=user,
                date_submitted=date,
                heating_usage=data["heating_usage"],
                appliance_usage=data["appliance_usage"],
                daily_transport=data["daily_transport"],
                weekly_travel=data["weekly_travel"],
                vehicle_type=data["vehicle_type"],
                energy_source=data["energy_source"],
                water_usage=data["water_usage"],
                waste_generation=data["waste_generation"],
                weekly_consumption=data["weekly_consumption"],
                weekly_raw_total=results["weekly_raw_total"],
                home_electric_subtotal=results["home_electric_subtotal"],
                renewable_discount=results["renewable_discount"],
                weekly_total=results["weekly_total"],
                pct_change_from_last=results["pct_change_from_last"],
                monthly_estimate=results["monthly_estimate"],
                monthly_estimate_per_person=results["monthly_estimate_per_person"],
            )

            # Re-enable auto_now_add for normal operation
            WeeklyCheckupResult._meta.get_field("date_submitted").auto_now_add = True

            last_week_total = results["weekly_total"]
            weeks_created += 1

            # Update progress bar description with current stats
            progress.set_description(
                f"Week {weeks_created}: CO2 {results['weekly_total']:.1f}kg"
            )

        # Clear progress bar and show final message
        progress.close()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {weeks_created} weeks of checkup data for user {username}"
            )
        )
