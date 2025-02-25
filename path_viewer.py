#! /usr/bin/env python

import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import geodatasets
import numpy as np
from shapely.geometry import Point

def plot_lat_long(file_path):

    df = pd.read_csv(file_path)

    print(df.head())
    gpd.options.display_precision = 7

    gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )
    print(gdf.head())

    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(df['longitude'], df['latitude'], c='red', alpha=0.7, s=20)

    # Draw arrows from the previous point to the most recent one
    for i in range(1, len(df)):
        x_start, y_start = df.iloc[i-1]['longitude'], df.iloc[i-1]['latitude']
        x_end, y_end = df.iloc[i]['longitude'], df.iloc[i]['latitude']
        
        # Draw an arrow from (x_start, y_start) to (x_end, y_end)
        ax.annotate(
            "", 
            xy=(x_end, y_end), 
            xytext=(x_start, y_start),
            arrowprops=dict(facecolor='green', edgecolor='green', arrowstyle='->', alpha=0.6)
        )
    
    selected_points = []
    
    def on_pick(event):
        ind = event.ind[0]
        point = (df.iloc[ind]['latitude'], df.iloc[ind]['longitude'])
        # Format to 6 decimal places
        formatted_point = [point[0], point[1]]
        selected_points.append(formatted_point)
        print(f"Selected point: {formatted_point}")

    fig.canvas.mpl_connect('pick_event', on_pick)  # Trigger when a point is clicked
    scatter.set_picker(True)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographical Plot with Hover Highlighting and Arrows")
    plt.show()

    return selected_points


def write_mission_file_from_plot(selected_points, directory_path):
    # Ensure the directory exists, if not, create it
    if not os.path.exists(directory_path):
        print(" write_mission_file_from_plot: Directory not found")
        return
    
    # Define the path for the mission file inside the specified directory
    mission_file_path = os.path.join(directory_path, "output.waypoints")
    
    # Open the .mission file in write mode
    with open(mission_file_path, 'w') as f:
        # Write the header for the mission file
        f.write("QGC WPL 110\n")  # Assuming version 110 as an example

        # Iterate through the selected points and write each in the desired format
        for idx, (lat, lon) in enumerate(selected_points):
            # <INDEX> <CURRENT WP> <COORD FRAME> <COMMAND> <PARAM1> <PARAM2> <PARAM3> <PARAM4> <PARAM5/X/LATITUDE> <PARAM6/Y/LONGITUDE> <PARAM7/Z/ALTITUDE> <AUTOCONTINUE>
            line = f"{idx} 0 3 16 0 0 0 0 {round(lat, 6)} {round(lon, 6)} 0 1\n"
            f.write(line)

    print(f"Mission file written to {mission_file_path}")


if __name__ == "__main__":
    file_path = input("Enter the path to the CSV file: ")
    selected = plot_lat_long(file_path)
    write_mission_file_from_plot(selected, "/home/parallels/repos/path_planning_tool/mp_wp_missions")