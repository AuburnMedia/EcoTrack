# Account Management

This document outlines the account management features of EcoTrack.

## User Registration

Users can register for a new account through the registration page. The registration process involves:

1. Creating a username and password
2. Agreeing to the terms of service
3. Completing an initial onboarding process

### Onboarding Process

After registration, users complete an onboarding form that collects:

- Their name
- Amount of people in their household
- House type (Large house, Small house, or Apartment)
- Monthly carbon goal (in kilograms of CO2), with tips provided

## Sample Data Generation

EcoTrack includes a command-line tool to generate sample data for testing and demonstration purposes.

### Fill Sample Data Command

```bash
python manage.py fill_sample_data <username>
```

This command:
- Creates or updates the user profile with demo settings
- Generates an initial carbon survey
- Creates weekly checkup data with realistic carbon usage patterns
- Establishes monthly carbon goals


## User Deletion

Users and their associated data can be removed using the delete_user command.

### Delete User Command

```bash
python manage.py delete_user <username> [--force]
```

This command:
- Removes the specified user account
- Deletes all associated data including:
  - User profile
  - Initial survey results
  - Weekly checkup data
  - Carbon usage entries
  - Carbon goals

Use the `--force` flag to skip the confirmation prompt.
