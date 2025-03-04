#! /usr/bin/env python

import os
import argparse
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from datetime import datetime

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

    for i in range(1, len(df)):
        x_start, y_start = df.iloc[i-1]['longitude'], df.iloc[i-1]['latitude']
        x_end, y_end = df.iloc[i]['longitude'], df.iloc[i]['latitude']
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
        formatted_point = [point[0], point[1]]
        selected_points.append(formatted_point)
        print(f"Selected point: {formatted_point}")

    fig.canvas.mpl_connect('pick_event', on_pick)
    scatter.set_picker(True)

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title("Geographical Plot with Hover Highlighting and Arrows")
    plt.show()

    return selected_points

def write_mission_file_from_plot(selected_points, base_directory, file_name):
    today_date = datetime.now().strftime("%Y-%m-%d")
    directory_path = os.path.join(base_directory, today_date)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    base_name = os.path.splitext(os.path.basename(file_name))[0]
    mission_file_path = os.path.join(directory_path, f"{base_name}.waypoints")
    
    with open(mission_file_path, 'w') as f:
        f.write("QGC WPL 110\n")
        for idx, (lat, lon) in enumerate(selected_points):
            line = f"{idx} 0 3 16 0 0 0 0 {round(lat, 6)} {round(lon, 6)} 0 1\n"
            f.write(line)
    
    print(f"Mission file written to {mission_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot latitude and longitude from a specified CSV file.")
    parser.add_argument("csv_file", type=str, help="Path to the CSV file")
    args = parser.parse_args()
    
    selected = plot_lat_long(args.csv_file)
    write_mission_file_from_plot(selected, "/home/parallels/repos/path_planning_tool/mp_wp_missions", args.csv_file)
