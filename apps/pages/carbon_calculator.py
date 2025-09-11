class CarbonCalculator:
    MONTHLY_WEIGHTS = {
        "home_type": {"APT": 4, "SMALL": 6, "LARGE": 8},
        "primary_heating": {"ELEC": 6, "GAS": 10, "OIL": 14, "NONE": 0},
        "appliance_use": {"DAILY": 2, "WEEKLY": 0.8, "OCCAS": 0.4, "NEVER": 0},
        "lighting_type": {"LED": 0.2, "CFL": 0.6, "INC": 1.6, "MIX": 1},
        "air_conditioning": {"YES": 3.2, "NO": 0},
        "car_type": {
            "NONE": 0,
            "PETROL": 12,
            "DIESEL": 13,
            "HYBRID": 6,
            "ELEC": 2.4,
        },
        "device_time": {"LT2": 0.4, "2-4": 0.8, "4-8": 1.6, "GT8": 2.4},
        "flights_per_year": {
            "NONE": 0,
            "1SHORT": 4,
            "2-4SHORT": 8,
            "1LONG": 24,
            "MULTLONG": 48,
        },
        "public_transport": {"NEVER": 0, "OCCAS": -0.8, "WEEKLY": -2, "DAILY": -3.2},
        "compost_waste": {"YES": -0.4, "NO": 0},
        "clothes_drying": {"LINE": -0.6, "MIXED": -0.2, "DRYER": 0},
        "buy_secondhand": {"OFTEN": -0.8, "SOME": -0.4, "RARELY": -0.2, "NEVER": 0},
    }

    WEEKLY_WEIGHTS = {
        "heating_usage": {
            "OFF": 0,
            "ECO": 0.6,
            "SOME": 1.2,
            "MOST": 2.4,
        },
        "appliance_usage": {
            "OPT": 0.4,
            "REG": 0.8,
            "FREQ": 1.4,
            "HEAVY": 2.0,
        },
        "daily_transport": {
            "ACTIVE": 0,
            "PUBLIC": 0.6,
            "MIXED": 1.2,
            "CAR": 2.0,
        },
        "weekly_travel": {
            "LOCAL": 0.4,
            "REGION": 1.2,
            "LONG": 3.2,
            "FLIGHT": 8.0,
        },
        "vehicle_type": {
            "NONE": 0,
            "ELECTRIC": 0.2,
            "HYBRID": 0.6,
            "STANDARD": 1.2,
            "LARGE": 1.8,
        },
        "energy_source": {
            "FULL_GREEN": 0.2,
            "PARTIAL": 0.6,
            "GREEN_OPT": 1.0,
            "STANDARD": 1.6,
        },
        "water_usage": {
            "MINIMAL": 0.4,
            "MODERATE": 0.8,
            "TYPICAL": 1.4,
            "HIGH": 2.0,
        },
        "waste_generation": {
            "MINIMAL": 0.2,
            "LOW": 0.6,
            "MEDIUM": 1.2,
            "HIGH": 2.0,
        },
        "weekly_consumption": {
            "NONE": 0,
            "ESSENTIAL": 0.4,
            "MODERATE": 1.0,
            "HIGH": 1.8,
        },
    }

    @staticmethod
    def calculate_initial_survey(data):
        """Calculate CO2 emissions from initial survey data."""
        monthly_raw_total = 0
        home_electric_subtotal = 0

        # Calculate home-electric subtotal first
        if data["primary_heating"] == "ELEC":
            home_electric_subtotal += CarbonCalculator.MONTHLY_WEIGHTS[
                "primary_heating"
            ]["ELEC"]

        # Add other electric components
        home_electric_subtotal += (
            CarbonCalculator.MONTHLY_WEIGHTS["appliance_use"][data["appliance_use"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["lighting_type"][data["lighting_type"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["air_conditioning"][
                data["air_conditioning"]
            ]
            + CarbonCalculator.MONTHLY_WEIGHTS["device_time"][data["device_time"]]
        )

        # Calculate raw total from all sources
        monthly_raw_total = (
            CarbonCalculator.MONTHLY_WEIGHTS["home_type"][data["home_type"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["primary_heating"][
                data["primary_heating"]
            ]
            + CarbonCalculator.MONTHLY_WEIGHTS["appliance_use"][data["appliance_use"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["lighting_type"][data["lighting_type"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["air_conditioning"][
                data["air_conditioning"]
            ]
            + CarbonCalculator.MONTHLY_WEIGHTS["car_type"][data["car_type"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["device_time"][data["device_time"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["flights_per_year"][
                data["flights_per_year"]
            ]
            + CarbonCalculator.MONTHLY_WEIGHTS["public_transport"][
                data["public_transport"]
            ]
            + CarbonCalculator.MONTHLY_WEIGHTS["compost_waste"][data["compost_waste"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["clothes_drying"][data["clothes_drying"]]
            + CarbonCalculator.MONTHLY_WEIGHTS["buy_secondhand"][data["buy_secondhand"]]
        )

        # Calculate renewable discount
        renewable_discount = home_electric_subtotal * (data["renewable_pct"] / 100)

        # Calculate final totals
        monthly_total = monthly_raw_total - renewable_discount
        monthly_per_person = monthly_total / data["household_size"]

        return {
            "monthly_raw_total": monthly_raw_total,
            "home_electric_subtotal": home_electric_subtotal,
            "renewable_discount": renewable_discount,
            "monthly_total": monthly_total,
            "monthly_per_person": monthly_per_person,
        }

    @staticmethod
    def calculate_weekly_checkup(data, last_week_total=None, household_size=1):
        """Calculate carbon emissions (in kg CO2e) from weekly checkup data."""
        # Calculate base emissions from each category
        weekly_raw_total = (
            CarbonCalculator.WEEKLY_WEIGHTS["heating_usage"][data["heating_usage"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["appliance_usage"][
                data["appliance_usage"]
            ]
            + CarbonCalculator.WEEKLY_WEIGHTS["daily_transport"][
                data["daily_transport"]
            ]
            + CarbonCalculator.WEEKLY_WEIGHTS["weekly_travel"][data["weekly_travel"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["vehicle_type"][data["vehicle_type"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["energy_source"][data["energy_source"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["water_usage"][data["water_usage"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["waste_generation"][
                data["waste_generation"]
            ]
            + CarbonCalculator.WEEKLY_WEIGHTS["weekly_consumption"][
                data["weekly_consumption"]
            ]
        )

        # Apply efficiency bonuses
        weekly_total = weekly_raw_total

        # Renewable energy bonus (20% reduction if using full green energy)
        if data["energy_source"] == "FULL_GREEN":
            weekly_total *= 0.8
        elif data["energy_source"] == "PARTIAL":
            weekly_total *= 0.9

        # Electric vehicle bonus (15% reduction on transport emissions)
        if data["vehicle_type"] == "ELECTRIC":
            transport_component = (
                CarbonCalculator.WEEKLY_WEIGHTS["daily_transport"][
                    data["daily_transport"]
                ]
                + CarbonCalculator.WEEKLY_WEIGHTS["weekly_travel"][
                    data["weekly_travel"]
                ]
            )
            weekly_total -= transport_component * 0.15

        # Calculate percentage change if we have last week's total
        pct_change = None
        if last_week_total is not None and last_week_total != 0:
            pct_change = ((weekly_total - last_week_total) / last_week_total) * 100

        monthly_estimate = weekly_total * 4

        home_electric_subtotal = (
            CarbonCalculator.WEEKLY_WEIGHTS["heating_usage"][data["heating_usage"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["appliance_usage"][
                data["appliance_usage"]
            ]
            + CarbonCalculator.WEEKLY_WEIGHTS["energy_source"][data["energy_source"]]
            + CarbonCalculator.WEEKLY_WEIGHTS["water_usage"][data["water_usage"]]
        )

        renewable_discount = 0
        if data["energy_source"] == "FULL_GREEN":
            renewable_discount = home_electric_subtotal * 0.8  # 80% discount
        elif data["energy_source"] == "PARTIAL":
            renewable_discount = home_electric_subtotal * 0.4  # 40% discount
        elif data["energy_source"] == "GREEN_OPT":
            renewable_discount = home_electric_subtotal * 0.2  # 20% discount

        monthly_estimate_per_person = monthly_estimate / household_size

        return {
            "weekly_raw_total": weekly_raw_total,
            "home_electric_subtotal": home_electric_subtotal,
            "renewable_discount": renewable_discount,
            "weekly_total": weekly_total,
            "pct_change_from_last": pct_change,
            "monthly_estimate": monthly_estimate,
            "monthly_estimate_per_person": monthly_estimate_per_person,
        }
