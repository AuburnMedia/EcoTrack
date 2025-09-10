class CarbonCalculator:
    # Monthly weights for Initial Survey
    MONTHLY_WEIGHTS = {
        'home_type': {
            'APT': 100,
            'SMALL': 150,
            'LARGE': 200
        },
        'primary_heating': {
            'ELEC': 150,
            'GAS': 250,
            'OIL': 350,
            'NONE': 0
        },
        'appliance_use': {
            'DAILY': 50,
            'WEEKLY': 20,
            'OCCAS': 10,
            'NEVER': 0
        },
        'lighting_type': {
            'LED': 5,
            'CFL': 15,
            'INC': 40,
            'MIX': 25
        },
        'air_conditioning': {
            'YES': 80,
            'NO': 0
        },
        'car_type': {
            'NONE': 0,
            'PETROL': 300,
            'DIESEL': 320,
            'HYBRID': 150,
            'ELEC': 60
        },
        'device_time': {
            'LT2': 10,
            '2-4': 20,
            '4-8': 40,
            'GT8': 60
        },
        'flights_per_year': {
            'NONE': 0,
            '1SHORT': 100,
            '2-4SHORT': 200,
            '1LONG': 600,
            'MULTLONG': 1200
        },
        'public_transport': {
            'NEVER': 0,
            'OCCAS': -20,
            'WEEKLY': -50,
            'DAILY': -80
        },
        'compost_waste': {
            'YES': -10,
            'NO': 0
        },
        'clothes_drying': {
            'LINE': -15,
            'MIXED': -5,
            'DRYER': 0
        },
        'buy_secondhand': {
            'OFTEN': -20,
            'SOME': -10,
            'RARELY': -5,
            'NEVER': 0
        }
    }

    # Weekly weights for Weekly Checkup (in kg CO2e)
    WEEKLY_WEIGHTS = {
        'heating_usage': {
            'OFF': 0,        # No heating/cooling needed
            'ECO': 15,       # Minimal usage with eco settings
            'SOME': 30,      # Moderate usage
            'MOST': 60       # Heavy usage
        },
        'appliance_usage': {
            'OPT': 10,       # Optimized usage
            'REG': 20,       # Regular usage
            'FREQ': 35,      # Frequent usage
            'HEAVY': 50      # Heavy usage
        },
        'daily_transport': {
            'ACTIVE': 0,     # Walking/cycling
            'PUBLIC': 15,    # Public transport
            'MIXED': 30,     # Mix of methods
            'CAR': 50        # Car-dependent
        },
        'weekly_travel': {
            'LOCAL': 10,     # Local only
            'REGION': 30,    # Regional trips
            'LONG': 80,      # Long distance
            'FLIGHT': 200    # Air travel
        },
        'vehicle_type': {
            'NONE': 0,       # No car used
            'ELECTRIC': 5,   # Electric vehicle
            'HYBRID': 15,    # Hybrid/efficient
            'STANDARD': 30,  # Standard car
            'LARGE': 45      # Large vehicle
        },
        'energy_source': {
            'FULL_GREEN': 5,   # 100% renewable
            'PARTIAL': 15,     # Partial renewable
            'GREEN_OPT': 25,   # Green energy plan
            'STANDARD': 40     # Standard grid
        },
        'water_usage': {
            'MINIMAL': 10,     # Very efficient
            'MODERATE': 20,    # Some conservation
            'TYPICAL': 35,     # Average usage
            'HIGH': 50         # High usage
        },
        'waste_generation': {
            'MINIMAL': 5,      # Minimal waste
            'LOW': 15,         # Low waste
            'MEDIUM': 30,      # Average waste
            'HIGH': 50         # High waste
        },
        'weekly_consumption': {
            'NONE': 0,         # No purchases
            'ESSENTIAL': 10,   # Essential only
            'MODERATE': 25,    # Some non-essential
            'HIGH': 45         # High consumption
        }
    }

    @staticmethod
    def calculate_initial_survey(data):
        """Calculate CO2 emissions from initial survey data."""
        monthly_raw_total = 0
        home_electric_subtotal = 0

        # Calculate home-electric subtotal first
        if data['primary_heating'] == 'ELEC':
            home_electric_subtotal += CarbonCalculator.MONTHLY_WEIGHTS['primary_heating']['ELEC']
        
        # Add other electric components
        home_electric_subtotal += (
            CarbonCalculator.MONTHLY_WEIGHTS['appliance_use'][data['appliance_use']] +
            CarbonCalculator.MONTHLY_WEIGHTS['lighting_type'][data['lighting_type']] +
            CarbonCalculator.MONTHLY_WEIGHTS['air_conditioning'][data['air_conditioning']] +
            CarbonCalculator.MONTHLY_WEIGHTS['device_time'][data['device_time']]
        )

        # Calculate raw total from all sources
        monthly_raw_total = (
            CarbonCalculator.MONTHLY_WEIGHTS['home_type'][data['home_type']] +
            CarbonCalculator.MONTHLY_WEIGHTS['primary_heating'][data['primary_heating']] +
            CarbonCalculator.MONTHLY_WEIGHTS['appliance_use'][data['appliance_use']] +
            CarbonCalculator.MONTHLY_WEIGHTS['lighting_type'][data['lighting_type']] +
            CarbonCalculator.MONTHLY_WEIGHTS['air_conditioning'][data['air_conditioning']] +
            CarbonCalculator.MONTHLY_WEIGHTS['car_type'][data['car_type']] +
            CarbonCalculator.MONTHLY_WEIGHTS['device_time'][data['device_time']] +
            CarbonCalculator.MONTHLY_WEIGHTS['flights_per_year'][data['flights_per_year']] +
            CarbonCalculator.MONTHLY_WEIGHTS['public_transport'][data['public_transport']] +
            CarbonCalculator.MONTHLY_WEIGHTS['compost_waste'][data['compost_waste']] +
            CarbonCalculator.MONTHLY_WEIGHTS['clothes_drying'][data['clothes_drying']] +
            CarbonCalculator.MONTHLY_WEIGHTS['buy_secondhand'][data['buy_secondhand']]
        )

        # Calculate renewable discount
        renewable_discount = home_electric_subtotal * (data['renewable_pct'] / 100)

        # Calculate final totals
        monthly_total = monthly_raw_total - renewable_discount
        monthly_per_person = monthly_total / data['household_size']

        return {
            'monthly_raw_total': monthly_raw_total,
            'home_electric_subtotal': home_electric_subtotal,
            'renewable_discount': renewable_discount,
            'monthly_total': monthly_total,
            'monthly_per_person': monthly_per_person
        }

    @staticmethod
    def calculate_weekly_checkup(data, last_week_total=None):
        """Calculate carbon emissions (in kg CO2e) from weekly checkup data."""
        # Calculate base emissions from each category
        weekly_raw_total = (
            CarbonCalculator.WEEKLY_WEIGHTS['heating_usage'][data['heating_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['appliance_usage'][data['appliance_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['daily_transport'][data['daily_transport']] +
            CarbonCalculator.WEEKLY_WEIGHTS['weekly_travel'][data['weekly_travel']] +
            CarbonCalculator.WEEKLY_WEIGHTS['vehicle_type'][data['vehicle_type']] +
            CarbonCalculator.WEEKLY_WEIGHTS['energy_source'][data['energy_source']] +
            CarbonCalculator.WEEKLY_WEIGHTS['water_usage'][data['water_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['waste_generation'][data['waste_generation']] +
            CarbonCalculator.WEEKLY_WEIGHTS['weekly_consumption'][data['weekly_consumption']]
        )

        # Apply efficiency bonuses
        weekly_total = weekly_raw_total
        
        # Renewable energy bonus (20% reduction if using full green energy)
        if data['energy_source'] == 'FULL_GREEN':
            weekly_total *= 0.8
        elif data['energy_source'] == 'PARTIAL':
            weekly_total *= 0.9
            
        # Electric vehicle bonus (15% reduction on transport emissions)
        if data['vehicle_type'] == 'ELECTRIC':
            transport_component = (
                CarbonCalculator.WEEKLY_WEIGHTS['daily_transport'][data['daily_transport']] +
                CarbonCalculator.WEEKLY_WEIGHTS['weekly_travel'][data['weekly_travel']]
            )
            weekly_total -= (transport_component * 0.15)

        # Calculate percentage change if we have last week's total
        pct_change = None
        if last_week_total is not None and last_week_total != 0:
            pct_change = ((weekly_total - last_week_total) / last_week_total) * 100

        monthly_estimate = weekly_total * 4

        return {
            'weekly_raw_total': weekly_raw_total,
            'weekly_total': weekly_total,
            'pct_change_from_last': pct_change,
            'monthly_estimate': monthly_estimate
        }
