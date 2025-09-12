# EcoTrack - Track Your Environmental Impact


![Image of the website in action](./static/img/EcoTrack_demo_1.png)

## Overview

EcoTrack helps you understand and reduce your impact on the environment. It shows you how your daily life affects your carbon footprint and helps you make better choices for the planet.

## Features

When you start using EcoTrack, you'll create an account and tell us a little bit about your lifestyle. The application will then:

Track Your Impact: Answer a quick survey when you begin and short weekly check-ins to see how you're doing. We look at your home energy use, how you travel, what appliances you use, and how you handle waste.

Show Your Progress: See your environmental impact through easy-to-read charts. Watch how your choices affect your carbon footprint over time and work toward your personal goals.

Help You Improve: Get tips and suggestions based on your habits. As you make changes, EcoTrack learns what works for you and suggests new ways to reduce your impact.

## Technical Details

Ecotrack is built using modern web tools to make it fast and reliable. The website works well on all devices and uses clear charts to show your data.

## Setting Up EcoTrack

To run EcoTrack on your computer, follow these steps:

```
python -m pip install -r requirements.txt

py manage.py collectstatic # Required 

py manage.py makemigrations
py manage.py migrate

py manage.py createsuperuser --username admin

py manage.py fill_sample_data admin # Optional: adds test data

py manage.py runserver
```

## Safety and Speed

The user's data is kept safe with secure logins and encrypted storage. CSRF tokens are enabled to prevent loss of user data and secure data storage.

## License

See LICENSE.md
