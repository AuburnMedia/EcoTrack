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
    USAGE_COUNT_CHOICES = [
        ('NONE', '0'),
        ('1-2', '1-2'),
        ('3-5', '3-5'),
        ('DAILY', 'Daily')
    ]
    LIGHTING_CHOICES = [
        ('LED', 'All LED'),
        ('MIXED', 'Mixed'),
        ('CFL', 'Mostly CFL'),
        ('INC', 'Mostly incandescent')
    ]
    FLIGHT_CHOICES = [
        ('NONE', 'None'),
        ('SHORT', 'Short'),
        ('LONG', 'Long')
    ]
    COMPOST_CHOICES = [
        ('NO', 'No'),
        ('SOME', 'Some'),
        ('DAILY', 'Every day')
    ]
    SECONDHAND_CHOICES = [
        ('NO', 'No'),
        ('ONE', '1 item'),
        ('MANY', '2+ items')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    # Survey Questions
    appliance_usage = models.CharField(max_length=5, choices=USAGE_COUNT_CHOICES)
    lighting_used = models.CharField(max_length=5, choices=LIGHTING_CHOICES)
    heating_ac_usage = models.CharField(max_length=5, choices=USAGE_COUNT_CHOICES)
    car_usage = models.CharField(max_length=5, choices=USAGE_COUNT_CHOICES)
    flights = models.CharField(max_length=5, choices=FLIGHT_CHOICES)
    public_transport = models.CharField(max_length=5, choices=USAGE_COUNT_CHOICES)
    compost_recycle = models.CharField(max_length=5, choices=COMPOST_CHOICES)
    secondhand_purchases = models.CharField(max_length=4, choices=SECONDHAND_CHOICES)

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
