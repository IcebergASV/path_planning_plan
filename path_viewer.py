#! /usr/bin/env python

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
        point = (df.iloc[ind]['longitude'], df.iloc[ind]['latitude'])
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


# Example usage:
selected = plot_lat_long("latlong_data.csv")
print("Final selected points:", selected)
