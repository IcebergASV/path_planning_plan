#! /usr/bin/env python

import os
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from datetime import datetime

def plot_lat_long(file_path, landmarks_file_path=None, title="Geographical Plot"):
    """Plot latitude and longitude data from one or two datasets on a scatter plot."""
    df_main = pd.read_csv(file_path)
    df_second = pd.read_csv(landmarks_file_path)
    gpd.options.display_precision = 7
    gdf_main = gpd.GeoDataFrame(df_main, geometry=gpd.points_from_xy(df_main.longitude, df_main.latitude), crs="EPSG:4326")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot first dataset in red
    scatter_main = ax.scatter(df_main['longitude'], df_main['latitude'], c='red', alpha=0.7, s=20, label="Dataset 1")

    # Plot second dataset in blue if provided
    scatter_second = None
    if df_second is not None:
        gdf_second = gpd.GeoDataFrame(df_second, geometry=gpd.points_from_xy(df_second.longitude, df_second.latitude), crs="EPSG:4326")
        scatter_second = ax.scatter(df_second['longitude'], df_second['latitude'], c='blue', alpha=0.7, s=20, label="Dataset 2")

    # Draw arrows between consecutive points in Dataset 1
    for i in range(1, len(df_main)):
        x_start, y_start = df_main.iloc[i-1]['longitude'], df_main.iloc[i-1]['latitude']
        x_end, y_end = df_main.iloc[i]['longitude'], df_main.iloc[i]['latitude']
        ax.annotate("", xy=(x_end, y_end), xytext=(x_start, y_start),
                    arrowprops=dict(facecolor='green', edgecolor='green', arrowstyle='->', alpha=0.6))
    
    selected_points = []

    def on_click(event):
        """Select a point by clicking."""
        if event.xdata is None or event.ydata is None:
            return
        datasets = [df_main]
        if df_second is not None:
            datasets.append(df_second)
        
        # Find the closest point from either dataset
        closest_point = None
        min_distance = float('inf')
        for df in datasets:
            distances = ((df['longitude'] - event.xdata)**2 + (df['latitude'] - event.ydata)**2)
            min_index = distances.idxmin()
            distance = distances.iloc[min_index]
            if distance < min_distance:
                min_distance = distance
                closest_point = [df.iloc[min_index]['latitude'], df.iloc[min_index]['longitude']]
        
        if closest_point:
            selected_points.append(closest_point)
            print(f"Selected point: {closest_point}")

    fig.canvas.mpl_connect('button_press_event', on_click)
    
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.legend()
    plt.show()
    
    return selected_points

def write_mission_file(selected_points, base_directory, file_name):
    """Save selected points as a mission waypoint file."""
    today_date = datetime.now().strftime("%Y-%m-%d")
    directory_path = os.path.join(base_directory, today_date)
    os.makedirs(directory_path, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(file_name))[0]
    mission_file_path = os.path.join(directory_path, f"{base_name}.waypoints")
    
    with open(mission_file_path, 'w') as f:
        f.write("QGC WPL 110\n")
        for idx, (lat, lon) in enumerate(selected_points):
            f.write(f"{idx} 0 3 16 0 0 0 0 {round(lat, 6)} {round(lon, 6)} 0 1\n")
    
    print(f"Mission file written to {mission_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot latitude and longitude from one or two CSV files.")
    parser.add_argument("csv_file", type=str, help="Path to the primary CSV file")
    parser.add_argument("--csv_file_second", type=str, help="Optional path to a second CSV file (plotted in blue)")
    parser.add_argument("--output_dir", type=str, default=".", help="Directory to save the mission file")
    
    args = parser.parse_args()

    selected_points = plot_lat_long(args.csv_file, args.csv_file_second)

    write_mission_file(selected_points, args.output_dir, args.csv_file)
