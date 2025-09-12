# Dashboard

The EcoTrack dashboard provides users with a comprehensive view of their carbon footprint and environmental impact.

## Features

### Carbon Usage Overview

The dashboard displays:
- Weekly carbon emissions in kg CO2
- Percentage change from previous week
- Progress toward monthly carbon goals
- Graphs of usage patterns

### Chart Implementation

The dashboard uses Chart.js for data visualization. All charts are managed through the `EcoTrackCharts` class which handles:
- Chart creation
- Data updates
- Data handling

#### Area Chart (Weekly Trends)
Shows weekly CO2 trends with:
- User's actual usage
- Monthly estimates
- Comparison with average usage
- Tooltips showing exact values



#### Carbon Usage Chart
Displays:
- Daily/weekly carbon usage
- Comparison with baseline averages
- Progress indicators

#### Goal Progress Chart
A donut chart showing:
- Progress toward monthly carbon goal
- Remaining amount
- Color-coded indicators (green for progress, gray for remaining)

### Data Management

The dashboard integrates data from multiple sources:
1. Initial survey results
2. Weekly checkups
3. Carbon goals
4. Historical trends

### Technical Implementation

The dashboard is implemented using:
- Chart.js for visualization
- Django templates for structure
- CSS for styling
- JavaScript for interactivity

