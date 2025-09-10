from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    HOUSE_TYPE_CHOICES = [
        ('LARGE', 'Large house'),
        ('SMALL', 'Small house'),
        ('APT', 'Apartment')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    household_size = models.PositiveIntegerField(default=1)  # Default to 1 person
    house_type = models.CharField(max_length=10, choices=HOUSE_TYPE_CHOICES, default='APT')  # Default to Apartment
    carbon_goal = models.PositiveIntegerField(help_text="Monthly carbon goal in kilograms of CO2", null=True, blank=True)
    onboarding_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Survey Models
class InitialSurveyResult(models.Model):
    HEATING_CHOICES = [
        ('ELEC', 'Electric'),
        ('GAS', 'Gas'),
        ('OIL', 'Oil'),
        ('NONE', 'None')
    ]
    USAGE_FREQ_CHOICES = [
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('OCCAS', 'Occasionally'),
        ('NEVER', 'Never')
    ]
    LIGHT_TYPE_CHOICES = [
        ('LED', 'LED'),
        ('CFL', 'CFL'),
        ('INC', 'Incandescent'),
        ('MIX', 'Mixed')
    ]
    YES_NO_CHOICES = [
        ('YES', 'Yes'),
        ('NO', 'No')
    ]
    CAR_TYPE_CHOICES = [
        ('NONE', 'None'),
        ('PETROL', 'Petrol'),
        ('DIESEL', 'Diesel'),
        ('HYBRID', 'Hybrid'),
        ('ELEC', 'Electric')
    ]
    DEVICE_TIME_CHOICES = [
        ('LT2', '<2h'),
        ('2-4', '2-4h'),
        ('4-8', '4-8h'),
        ('GT8', '8+h')
    ]
    RENEWABLE_PCT_CHOICES = [
        (0, '0%'),
        (25, '25%'),
        (50, '50%'),
        (75, '75%'),
        (100, '100%')
    ]
    FLIGHT_CHOICES = [
        ('NONE', 'None'),
        ('1SHORT', '1 short'),
        ('2-4SHORT', '2-4 short'),
        ('1LONG', '1 long'),
        ('MULTLONG', 'Multiple long')
    ]
    TRANSPORT_FREQ_CHOICES = [
        ('NEVER', 'Never'),
        ('OCCAS', 'Occasionally'),
        ('WEEKLY', 'Weekly'),
        ('DAILY', 'Daily')
    ]
    CLOTHES_DRY_CHOICES = [
        ('LINE', 'Always line'),
        ('MIXED', 'Sometimes'),
        ('DRYER', 'Always dryer')
    ]
    SECONDHAND_CHOICES = [
        ('OFTEN', 'Often'),
        ('SOME', 'Sometimes'),
        ('RARELY', 'Rarely'),
        ('NEVER', 'Never')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    # Survey Questions
    primary_heating = models.CharField(max_length=4, choices=HEATING_CHOICES)
    appliance_use = models.CharField(max_length=6, choices=USAGE_FREQ_CHOICES)
    lighting_type = models.CharField(max_length=3, choices=LIGHT_TYPE_CHOICES)
    air_conditioning = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    car_type = models.CharField(max_length=6, choices=CAR_TYPE_CHOICES)
    device_time = models.CharField(max_length=3, choices=DEVICE_TIME_CHOICES)
    renewable_pct = models.IntegerField(choices=RENEWABLE_PCT_CHOICES)
    flights_per_year = models.CharField(max_length=8, choices=FLIGHT_CHOICES)
    public_transport = models.CharField(max_length=6, choices=TRANSPORT_FREQ_CHOICES)
    compost_waste = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    clothes_drying = models.CharField(max_length=5, choices=CLOTHES_DRY_CHOICES)
    buy_secondhand = models.CharField(max_length=6, choices=SECONDHAND_CHOICES)

    # Calculated Fields
    monthly_raw_total = models.FloatField()
    home_electric_subtotal = models.FloatField()
    renewable_discount = models.FloatField()
    monthly_total = models.FloatField()
    monthly_per_person = models.FloatField()

    def __str__(self):
        return f"{self.user.username}'s Initial Survey - {self.date_submitted.strftime('%Y-%m-%d')}"

class WeeklyCheckupResult(models.Model):
    HEATING_CHOICES = [
        ('OFF', 'Didn\'t need it this week'),
        ('ECO', 'Used eco settings/timer'),
        ('SOME', 'A few hours when needed'),
        ('MOST', 'Most of the day')
    ]
    
    APPLIANCE_USAGE_CHOICES = [
        ('OPT', 'Full loads, eco settings'),
        ('REG', 'Regular loads'),
        ('FREQ', 'Frequent small loads'),
        ('HEAVY', 'Multiple loads daily')
    ]
    
    TRANSPORT_CHOICES = [
        ('ACTIVE', 'Mostly walk/cycle'),
        ('PUBLIC', 'Mainly public transport'),
        ('MIXED', 'Mix of car and alternatives'),
        ('CAR', 'Primarily car')
    ]
    
    DISTANCE_CHOICES = [
        ('LOCAL', 'Stayed local (<20km)'),
        ('REGION', 'Regional trips (20-100km)'),
        ('LONG', 'Long distance (>100km)'),
        ('FLIGHT', 'Took a flight')
    ]
    
    CAR_TYPE_CHOICES = [
        ('NONE', 'No car used'),
        ('ELECTRIC', 'Electric vehicle'),
        ('HYBRID', 'Hybrid/Small efficient car'),
        ('STANDARD', 'Standard car'),
        ('LARGE', 'Large vehicle/SUV')
    ]
    
    ENERGY_SOURCE_CHOICES = [
        ('FULL_GREEN', '100% renewable/solar'),
        ('PARTIAL', 'Partial renewable mix'),
        ('GREEN_OPT', 'Green energy plan'),
        ('STANDARD', 'Standard grid power')
    ]
    
    WATER_USAGE_CHOICES = [
        ('MINIMAL', 'Quick showers, minimal usage'),
        ('MODERATE', 'Moderate usage, some conservation'),
        ('TYPICAL', 'Typical household usage'),
        ('HIGH', 'Extended usage, multiple daily')
    ]
    
    WASTE_CHOICES = [
        ('MINIMAL', 'Minimal waste, mostly reusable'),
        ('LOW', 'Small bag, mostly recycled'),
        ('MEDIUM', 'Regular bin amount'),
        ('HIGH', 'Multiple bags/overflow')
    ]
    
    CONSUMPTION_CHOICES = [
        ('NONE', 'No new purchases'),
        ('ESSENTIAL', 'Only essentials'),
        ('MODERATE', 'Some non-essential items'),
        ('HIGH', 'Multiple large purchases')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    # Survey Questions
    heating_usage = models.CharField(max_length=6, choices=HEATING_CHOICES)
    appliance_usage = models.CharField(max_length=6, choices=APPLIANCE_USAGE_CHOICES)
    daily_transport = models.CharField(max_length=6, choices=TRANSPORT_CHOICES)
    weekly_travel = models.CharField(max_length=6, choices=DISTANCE_CHOICES)
    vehicle_type = models.CharField(max_length=8, choices=CAR_TYPE_CHOICES)
    energy_source = models.CharField(max_length=10, choices=ENERGY_SOURCE_CHOICES)
    water_usage = models.CharField(max_length=8, choices=WATER_USAGE_CHOICES)
    waste_generation = models.CharField(max_length=8, choices=WASTE_CHOICES)
    weekly_consumption = models.CharField(max_length=9, choices=CONSUMPTION_CHOICES)

    # Calculated Fields
    weekly_raw_total = models.FloatField()
    weekly_total = models.FloatField()
    pct_change_from_last = models.FloatField(null=True, blank=True)
    monthly_estimate = models.FloatField()

    def __str__(self):
        return f"{self.user.username}'s Weekly Checkup - {self.date_submitted.strftime('%Y-%m-%d')}"


class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 100) 
    info  = models.CharField(max_length = 100, default = '')
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
