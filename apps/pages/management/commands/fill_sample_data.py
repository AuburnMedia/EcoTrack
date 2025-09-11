from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.pages.models import WeeklyCheckupResult, UserProfile
from apps.pages.carbon_calculator import CarbonCalculator
import random

class Command(BaseCommand):
    help = 'Fills the database with sample weekly checkup data for a specified user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to create sample data for')

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} does not exist'))
            return

        # Create or update user profile with onboarding data
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'display_name': username,
                'house_type': 'SMALL',  
                'carbon_goal': 2000,    
                'household_size': 1,     
                'onboarding_completed': True
            }
        )
        
        if not created:
            # Update existing profile
            profile.name = username
            profile.house_type = 'SMALL'
            profile.carbon_goal = 2000
            profile.onboarding_completed = True
            profile.save()

        self.stdout.write(self.style.SUCCESS(f'Updated onboarding data for user {username}'))

        # Choices for each field based on the model's choices
        CHOICES = {
            'heating_usage': ['OFF', 'ECO', 'SOME', 'MOST'],
            'appliance_usage': ['OPT', 'REG', 'FREQ', 'HEAVY'],
            'daily_transport': ['ACTIVE', 'PUBLIC', 'MIXED', 'CAR'],
            'weekly_travel': ['LOCAL', 'REGION', 'LONG', 'FLIGHT'],
            'vehicle_type': ['NONE', 'ELECTRIC', 'HYBRID', 'STANDARD', 'LARGE'],
            'energy_source': ['FULL_GREEN', 'PARTIAL', 'GREEN_OPT', 'STANDARD'],
            'water_usage': ['MINIMAL', 'MODERATE', 'TYPICAL', 'HIGH'],
            'waste_generation': ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH'],
            'weekly_consumption': ['NONE', 'ESSENTIAL', 'MODERATE', 'HIGH']
        }

        # Generate 30 weeks of data
        current_date = timezone.now()
        current_date = current_date - timezone.timedelta(days=current_date.weekday() + 1)
        # Set to end of day (23:59:59)
        current_date = current_date.replace(hour=23, minute=59, second=59)
        
        weeks_created = 0
        last_week_total = None

        for week in range(30):
            date = current_date - timezone.timedelta(weeks=week)
            
            # Create checkup data with a tendency towards moderate choices
            # but occasional variation to show improvements and setbacks
            data = {
                'heating_usage': random.choices(
                    CHOICES['heating_usage'],
                    weights=[15, 40, 30, 15]  # Favor ECO and SOME
                )[0],
                'appliance_usage': random.choices(
                    CHOICES['appliance_usage'],
                    weights=[30, 40, 20, 10]  # Favor OPT and REG
                )[0],
                'daily_transport': random.choices(
                    CHOICES['daily_transport'],
                    weights=[20, 30, 30, 20]  # Balanced mix
                )[0],
                'weekly_travel': random.choices(
                    CHOICES['weekly_travel'],
                    weights=[40, 30, 20, 10]  # Favor local travel
                )[0],
                'vehicle_type': random.choices(
                    CHOICES['vehicle_type'],
                    weights=[20, 20, 30, 20, 10]  # Favor hybrid/electric
                )[0],
                'energy_source': random.choices(
                    CHOICES['energy_source'],
                    weights=[25, 30, 25, 20]  # Favor green energy
                )[0],
                'water_usage': random.choices(
                    CHOICES['water_usage'],
                    weights=[25, 35, 25, 15]  # Favor moderate usage
                )[0],
                'waste_generation': random.choices(
                    CHOICES['waste_generation'],
                    weights=[20, 35, 30, 15]  # Favor low waste
                )[0],
                'weekly_consumption': random.choices(
                    CHOICES['weekly_consumption'],
                    weights=[15, 40, 35, 10]  # Favor essential/moderate
                )[0]
            }

            # Calculate carbon impact using the CarbonCalculator
            results = CarbonCalculator.calculate_weekly_checkup(data, last_week_total)
            
            # Force auto_now_add to use our date by temporarily disabling it
            WeeklyCheckupResult._meta.get_field('date_submitted').auto_now_add = False
            
            # Create the weekly checkup with the specific date
            checkup = WeeklyCheckupResult.objects.create(
                user=user,
                date_submitted=date,
                heating_usage=data['heating_usage'],
                appliance_usage=data['appliance_usage'],
                daily_transport=data['daily_transport'],
                weekly_travel=data['weekly_travel'],
                vehicle_type=data['vehicle_type'],
                energy_source=data['energy_source'],
                water_usage=data['water_usage'],
                waste_generation=data['waste_generation'],
                weekly_consumption=data['weekly_consumption'],
                weekly_raw_total=results['weekly_raw_total'],
                weekly_total=results['weekly_total'],
                pct_change_from_last=results['pct_change_from_last'],
                monthly_estimate=results['monthly_estimate']
            )
            
            # Re-enable auto_now_add for normal operation
            WeeklyCheckupResult._meta.get_field('date_submitted').auto_now_add = True

            last_week_total = results['weekly_total']
            weeks_created += 1

            if week % 4 == 0:  # Progress indicator every 4 weeks
                self.stdout.write(f'Created data for week {weeks_created}...')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {weeks_created} weeks of checkup data for user {username}'
            )
        )
