import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

# Load the Excel file, specify the second sheet, and set header row
file_path = '/Users/quanshuen/PycharmProjects/tflActivity/Data/tfl-daily-cycle-hires.xlsx'  # Update with your actual file path
df = pd.read_excel(file_path, sheet_name=1, header=5)  # Reads data from the second sheet with headers on row 6

# Convert 'Day' column to datetime
df['Day'] = pd.to_datetime(df['Day'], dayfirst=True)

# Extract month and year from 'Day' column
df['Year'] = df['Day'].dt.year
df['Month'] = df['Day'].dt.month

# Calculate monthly average of 'Number of Bicycle Hires' for each year
monthly_avg = df.groupby(['Year', 'Month'])['Number of Bicycle Hires'].mean().unstack(level=0)

# Set up a color map for the gradient
years = monthly_avg.columns
norm = mcolors.Normalize(vmin=years.min(), vmax=years.max())
cmap = plt.cm.viridis  # Choose a color map like 'viridis' or 'plasma'
colors = cmap(norm(years))

# Plotting
plt.figure(figsize=(12, 6))

# Plot each year with a color from the gradient
for year, color in zip(years, colors):
    plt.plot(monthly_avg.index, monthly_avg[year], label=str(year), color=color)

# Set the month names as X-axis labels
plt.xticks(ticks=range(1, 13), labels=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

# Labels and title
plt.xlabel('Month')
plt.ylabel('Average Number of Bicycle Hires')
plt.title('Monthly Variation of Bicycle Hires Over the Years')
plt.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)

plt.tight_layout()
plt.show()
