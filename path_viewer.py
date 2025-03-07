import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point

# Define mode colors
MODE_COLORS = {
    "UNKNOWN": "gray",
    "MANUAL": "blue",
    "GUIDED": "orange",
    "AUTO": "green"
}

def plot_lat_long(file_path):
    # Read CSV and ensure correct columns
    df = pd.read_csv(file_path, names=["latitude", "longitude", "mode"], skiprows=1)

    # Convert latitude and longitude to numeric values
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # Drop invalid rows
    df = df.dropna(subset=["latitude", "longitude"])

    # Standardize mode column
    df["mode"] = df["mode"].str.upper().fillna("UNKNOWN")

    gpd.options.display_precision = 7
    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    # Scatter plot waypoints based on mode
    scatter_plots = []
    for mode, color in MODE_COLORS.items():
        mode_data = df[df["mode"] == mode]
        if not mode_data.empty:
            scatter = ax.scatter(
                mode_data["longitude"], mode_data["latitude"],
                c=color, label=mode, alpha=0.7, s=30, picker=True
            )
            scatter_plots.append((scatter, mode_data))  # Store scatter and corresponding data

    # Draw arrows to show path
    for i in range(1, len(df)):
        x_start, y_start = df.iloc[i-1]["longitude"], df.iloc[i-1]["latitude"]
        x_end, y_end = df.iloc[i]["longitude"], df.iloc[i]["latitude"]
        mode = df.iloc[i]["mode"]
        color = MODE_COLORS.get(mode, "gray")

        ax.annotate(
            "", 
            xy=(x_end, y_end), 
            xytext=(x_start, y_start),
            arrowprops=dict(facecolor=color, edgecolor=color, arrowstyle="->", alpha=0.6)
        )

    selected_points = []

    def on_pick(event):
        for scatter, mode_data in scatter_plots:
            if event.artist == scatter:
                index = event.ind[0]  # Get the first selected point index
                lat = mode_data.iloc[index]["latitude"]
                lon = mode_data.iloc[index]["longitude"]
                formatted_point = [round(lat, 6), round(lon, 6)]

                # Append only if the point is not already selected
                if formatted_point not in selected_points:  
                    selected_points.append(formatted_point)
                    print(f"Selected point: {formatted_point}")

    fig.canvas.mpl_connect("pick_event", on_pick)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographical Plot with Mode-Based Colors")
    plt.legend()
    plt.show()

    return selected_points


def write_mission_file(selected_points, directory_path, file_name):
    if not os.path.exists(directory_path):
        print("Directory not found")
        return
    
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    mission_file_path = os.path.join(directory_path, f"{base_name}.waypoints")
    
    with open(mission_file_path, 'w') as f:
        f.write("QGC WPL 110\n")
        for idx, (lat, lon) in enumerate(selected_points):
            f.write(f"{idx} 0 3 16 0 0 0 0 {lat} {lon} 0 1\n")
    
    print(f"Mission file written to {mission_file_path}")


if __name__ == "__main__":
    file_path = input("Enter the path to the CSV file: ")
    selected_points = plot_lat_long(file_path)
    write_mission_file(selected_points, "/home/jordyn/Documents/Iceberg", file_path)
