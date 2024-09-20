from analyze_lib import dataset

file_path = './activities.csv'

data = dataset(file_path)

# annual analysis from 2022 to 2023:
for y in [2022,2023]:

    # general analysis of all activities
    data.annual_analysis(year=y)

    # analysis of running activities with a distance > 1200.0 meters
    data.annual_analysis(year=y, sport='Run', threshold=1200.0)

# 2023 monthly analysis
data.monthly_analysis(year=2023)

# 2023 monthly analysis (running activities with a distance > 2500.0 meters) without figures
data.monthly_analysis(year=2023, sport='Run', threshold=2500.0, with_figure=False)
