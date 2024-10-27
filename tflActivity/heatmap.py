import geopandas as gpd
import matplotlib.pyplot as plt

# Load a shapefile of London boroughs or another UK map (you may need to download a London-specific file)
# For example, you could download the boroughs shapefile from:
# https://data.london.gov.uk/dataset/statistical-gis-boundary-files-london

shapefile_path = 'path_to_your_shapefile/London_Borough_Excluding_MHW.shp'  # Update with actual file path
london_map = gpd.read_file(shapefile_path)

# Plotting the map
plt.figure(figsize=(10, 10))
london_map.plot(edgecolor='black', color='lightblue', linewidth=0.5)
plt.title("Map of London")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()