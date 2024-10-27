import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import imageio
from shapely.geometry import Point
import os

# Paths to files
location_file = '/Users/quanshuen/PycharmProjects/tflActivity/Data/Busy Locations/1 Monitoring locations.csv'
activity_file = '/Users/quanshuen/PycharmProjects/tflActivity/Data/Busy Locations/2018 Q3 (Jul-Sep)-Central.csv'
shapefile_path = '/Users/quanshuen/PycharmProjects/tflActivity/Data/Shapefile for Map of London/London-wards-2018/London-wards-2018_ESRI/London_Ward_CityMerged.shp'

# Directory to save images and GIF
output_folder = '/Users/quanshuen/PycharmProjects/tflActivity/tflActivity/heatmap_frames'
gif_path = '/Users/quanshuen/PycharmProjects/tflActivity/tflActivity/bike_activity_heatmap_average.gif'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load location data and activity data
locations_df = pd.read_csv(location_file)
activity_df = pd.read_csv(activity_file)

# Convert 'Date' to datetime
activity_df['Date'] = pd.to_datetime(activity_df['Date'], format='%d/%m/%Y')

# Merge location and activity data on dock IDs
merged_df = pd.merge(
    activity_df,
    locations_df,
    left_on='UnqID',
    right_on='Site ID',
    how='inner'
)

# Convert 'Time' to datetime to enable grouping by hour
merged_df['Time'] = pd.to_datetime(merged_df['Time'], format='%H:%M:%S').dt.time

# Extract hour from the Time column
merged_df['Hour'] = merged_df['Time'].apply(lambda x: pd.to_datetime(str(x)).hour)

# Convert location data to GeoDataFrame with WGS 84 CRS (lat/lon)
geometry = [Point(xy) for xy in zip(merged_df['Longitude'], merged_df['Latitude'])]
location_gdf = gpd.GeoDataFrame(merged_df, crs="EPSG:4326", geometry=geometry)

# Reproject location data to match the shapefile CRS (British National Grid, EPSG:27700)
location_gdf = location_gdf.to_crs(epsg=27700)

# Load the London map shapefile
london_map = gpd.read_file(shapefile_path)

# Group by hour and Site ID, calculating the average Count
average_counts = (
    location_gdf.groupby(['Hour', 'UnqID'])
    ['Count'].mean().reset_index()
)

# Merge with location data to get latitude and longitude
average_location_gdf = pd.merge(
    average_counts,
    locations_df,
    left_on='UnqID',
    right_on='Site ID',
    how='inner'
)

# Convert location data to GeoDataFrame
geometry_avg = [Point(xy) for xy in zip(average_location_gdf['Longitude'], average_location_gdf['Latitude'])]
average_location_gdf = gpd.GeoDataFrame(average_location_gdf, crs="EPSG:4326", geometry=geometry_avg)

# Reproject average location data
average_location_gdf = average_location_gdf.to_crs(epsg=27700)

# Determine global min and max for 'Count' to use consistent color scale
vmin = average_location_gdf['Count'].min()
vmax = average_location_gdf['Count'].max()


# Function to plot a heatmap for each hour and save as an image with a 4x zoom
def plot_heatmap(hour_data, hour, output_path):
    plt.figure(figsize=(10, 10))

    # Plot the London map
    london_map.plot(edgecolor='black', color='lightgrey', linewidth=0.5)

    # Create a scatter plot for bike counts at each location, with fixed vmin and vmax
    plt.scatter(
        hour_data.geometry.x,
        hour_data.geometry.y,
        c=hour_data['Count'],
        cmap='hot',  # or any other color map suitable for heatmaps
        s=hour_data['Count'] * 2,  # Scale marker size by count for emphasis
        alpha=0.6,
        vmin=vmin,  # Fixed color scale minimum
        vmax=vmax  # Fixed color scale maximum
    )

    # Title and labels
    plt.title(f"Average Bike Dock Activity Heatmap (All Days) - Hour: {hour:02d}:00")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.colorbar(label="Average Bike Count")

    # Calculate bounding box of bike locations and apply a 4x zoom
    minx, miny, maxx, maxy = london_map.total_bounds
    center_x = (maxx + minx) / 2
    center_y = (maxy + miny) / 2
    zoom_factor = 8  # 4x zoom

    plt.xlim(center_x - (maxx - minx) / zoom_factor, center_x + (maxx - minx) / zoom_factor)
    plt.ylim(center_y - (maxy - miny) / zoom_factor, center_y + (maxy - miny) / zoom_factor)

    # Save each plot as a separate image with consistent dimensions
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()


# Generate heatmaps for each hour and store image paths
image_files = []
for hour in range(24):
    # Filter average data for each hour
    hour_data = average_location_gdf[average_location_gdf['Hour'] == hour]

    # Output path for the heatmap with zero-padded hour formatting
    output_path = os.path.join(output_folder, f'average_heatmap_{hour:02d}.png')

    # Plot and save the heatmap for the current hour
    plot_heatmap(hour_data, hour, output_path)

    # Append the file path to the list in order
    image_files.append(output_path)

# Ensure images are loaded in the correct sorted order
images = [imageio.imread(img) for img in sorted(image_files)]

# Ensure all images are the same shape
base_shape = images[0].shape
consistent_images = [img for img in images if img.shape == base_shape]

# Create a GIF from the images in the correct order
imageio.mimsave(gif_path, consistent_images, duration=0.5)

print(f"Average heatmap GIF saved as {gif_path}")
