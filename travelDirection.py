import pandas as pd
import matplotlib.pyplot as plt
import imageio.v2 as imageio  # Updated import to handle deprecation warning
import os

# Path to the activity data file
activity_file = '/Users/quanshuen/PycharmProjects/tflActivity/Data/Busy Locations/2018 Q3 (Jul-Sep)-Central.csv'

# Directory to save images and GIF
output_folder = '/Users/quanshuen/PycharmProjects/tflActivity/tflActivity/Direction of travel'
gif_path = os.path.join(output_folder, 'direction_counts_by_hour.gif')

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load activity data
activity_df = pd.read_csv(activity_file)

# Convert 'Date' and 'Time' to datetime
activity_df['Datetime'] = pd.to_datetime(activity_df['Date'] + ' ' + activity_df['Time'], format='%d/%m/%Y %H:%M:%S')

# Extract hour from Datetime
activity_df['Hour'] = activity_df['Datetime'].dt.hour

# Group by hour and direction, then sum the counts
hourly_direction_counts = activity_df.groupby(['Hour', 'Dir'])['Count'].sum().unstack(fill_value=0)

# Define the list of directions
directions = ['Eastbound', 'Westbound', 'Northbound', 'Southbound']

# Initialize a list to hold file paths for GIF creation
image_files = []

# Generate bar charts for each hour
for hour in range(24):
    # Debug: Print which hour we're processing
    print(f"\nProcessing hour: {hour}")

    # Get counts for the current hour
    if hour in hourly_direction_counts.index:
        direction_counts = hourly_direction_counts.loc[hour]
        print(f"Counts for hour {hour}: {direction_counts.to_dict()}")
    else:
        direction_counts = pd.Series(0, index=directions)
        print(f"No data for hour {hour}, using zero counts: {direction_counts.to_dict()}")

    # Reindex to ensure all directions are included
    direction_counts = direction_counts.reindex(directions, fill_value=0)

    # Check the shape of the data to be plotted
    print(f"Shape of direction counts for hour {hour}: {direction_counts.shape}")

    # Create a bar chart
    plt.figure(figsize=(10, 6))

    # Try plotting
    try:
        direction_counts.plot(kind='bar', color=['blue', 'orange', 'green', 'red'], alpha=0.7, width=0.6)
    except Exception as e:
        print(f"Error plotting hour {hour}: {e}")
        continue

    # Title and labels
    plt.title(f"Total Cycle Hire Riders by Direction - Hour: {hour:02d}:00")
    plt.xlabel("Direction of Travel")
    plt.ylabel("Total Number of Riders")
    plt.xticks(rotation=45)

    # Set fixed limits for the axes
    plt.ylim(0, direction_counts.max() + 10)  # Leave some space above the bars

    # Adjust layout to minimize differences in figure size
    plt.tight_layout()

    # Save the plot with a fixed size and resolution
    output_path = os.path.join(output_folder, f'direction_counts_hour_{hour:02d}.png')
    plt.savefig(output_path, bbox_inches='tight', dpi=150)
    plt.close()

    # Append to image files
    image_files.append(output_path)

# Ensure images are loaded in the correct sorted order
images = []
for img_path in sorted(image_files):
    try:
        img = imageio.imread(img_path)
        images.append(img)
        print(f"Image shape for {img_path}: {img.shape}")  # Log the shape of each image
    except Exception as e:
        print(f"Error reading image {img_path}: {e}")

# Create a GIF from the images
if images:
    # Verify shapes of images
    image_shapes = [img.shape for img in images]
    print(f"Shapes of images for GIF: {image_shapes}")

    # Check for consistent shapes before creating the GIF
    if all(shape == image_shapes[0] for shape in image_shapes):
        imageio.mimsave(gif_path, images, duration=0.5)
        print(f"Direction counts GIF saved as {gif_path}")
    else:
        print("Image shapes are not consistent. GIF not created.")
else:
    print("No images were created, GIF not saved.")
