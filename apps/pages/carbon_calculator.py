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

    # Weekly weights for Weekly Checkup
    WEEKLY_WEIGHTS = {
        'appliance_usage': {
            'NONE': 0,
            '1-2': 5,
            '3-5': 15,
            'DAILY': 30
        },
        'lighting_used': {
            'LED': 1,
            'MIXED': 5,
            'CFL': 10,
            'INC': 20
        },
        'heating_ac_usage': {
            'NONE': 0,
            '1-2': 15,
            '3-5': 30,
            'DAILY': 50
        },
        'car_usage': {
            'NONE': 0,
            '1-2': 40,
            '3-5': 80,
            'DAILY': 150
        },
        'flights': {
            'NONE': 0,
            'SHORT': 200,
            'LONG': 400
        },
        'public_transport': {
            'NONE': 0,
            '1-2': -10,
            '3-5': -25,
            'DAILY': -40
        },
        'compost_recycle': {
            'NO': 0,
            'SOME': -5,
            'DAILY': -15
        },
        'secondhand_purchases': {
            'NO': 0,
            'ONE': -10,
            'MANY': -20
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
        """Calculate CO2 emissions from weekly checkup data."""
        weekly_raw_total = (
            CarbonCalculator.WEEKLY_WEIGHTS['appliance_usage'][data['appliance_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['lighting_used'][data['lighting_used']] +
            CarbonCalculator.WEEKLY_WEIGHTS['heating_ac_usage'][data['heating_ac_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['car_usage'][data['car_usage']] +
            CarbonCalculator.WEEKLY_WEIGHTS['flights'][data['flights']] +
            CarbonCalculator.WEEKLY_WEIGHTS['public_transport'][data['public_transport']] +
            CarbonCalculator.WEEKLY_WEIGHTS['compost_recycle'][data['compost_recycle']] +
            CarbonCalculator.WEEKLY_WEIGHTS['secondhand_purchases'][data['secondhand_purchases']]
        )

        weekly_total = weekly_raw_total  # In this version, no weekly renewable discount

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
