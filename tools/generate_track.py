#! /usr/bin/env python3

"""
This script is based on the following code:
https://qiita.com/toki-1441/items/615d781e3a20edf22cda
"""

import os
import numpy as np
import pandas as pd
import argparse
import matplotlib.pyplot as plt

def search_nearest_index(x, y, bound_map_x, bound_map_y, index=0, window_len=10):
    min_dist = 1000000
    min_index = index
    bound_map_x = bound_map_x + bound_map_x
    bound_map_y = bound_map_y + bound_map_y
    for i in range(index, index + window_len):
        dist = np.sqrt((x - bound_map_x[i])**2 + (y - bound_map_y[i])**2)
        if dist < min_dist:
            min_dist = dist
            min_index = i
    return min_index

def calc_width(x, y, bound_x, bound_y):
    return np.sqrt((x - bound_x)**2 + (y - bound_y)**2)

def calculate_center_line(outer_track_df, inner_track_df, limit=10, skip=5):
    # Calculate the center line
    outer_track_x = list(outer_track_df["x"])
    outer_track_y = list(outer_track_df["y"])
    inner_track_x = list(inner_track_df["x"])
    inner_track_y = list(inner_track_df["y"])
    center_x = []
    center_y = []
    w_tr_right_m = []
    w_tr_left_m = []
    nearest_index = 0
    for i in range(0, len(outer_track_x), skip):
        nearest_index = search_nearest_index(outer_track_x[i], outer_track_y[i], inner_track_x, inner_track_y, nearest_index, limit)

        # Calculate the center line
        if nearest_index > len(inner_track_x) - 1:
            nearest_index -= len(inner_track_x)

        cx = (outer_track_x[i] + inner_track_x[nearest_index]) / 2.
        cy = (outer_track_y[i] + inner_track_y[nearest_index]) / 2.

        if len(center_x) > 0 and calc_dist(center_x[-1], center_y[-1], cx, cy) < min_dist_between_points:
            continue

        center_x.append(cx)
        center_y.append(cy)

    return pd.DataFrame({
        "x_m": center_x,
        "y_m": center_y,
        "w_tr_right_m": w_tr_right_m,  # Assuming the width is evenly divided
        "w_tr_left_m": w_tr_left_m
    })

def read_bounds_csv(bounds_dir: str):
    outer_track_path = bounds_dir + "/left_lane_bound.csv"
    inner_track_path = bounds_dir + "/right_lane_bound.csv"

    # Defining column names
    column_names = ["x", "y","z"]

    # Re-load the CSV files with column names
    outer_track_df = pd.read_csv(outer_track_path, names=column_names, header=0)
    inner_track_df = pd.read_csv(inner_track_path, names=column_names, header=0)
    return outer_track_df, inner_track_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bounds_dir", help="bounds csv directory in resources/bounds")
    args = parser.parse_args()

    # Load the provided CSV files
    this_dir = os.path.dirname(os.path.abspath(__file__))
    bounds_dir = this_dir + "/../resources/bounds/" + args.bounds_dir
    outer_track_df, inner_track_df = read_bounds_csv(bounds_dir)

    center_track_df = calculate_center_line(outer_track_df, inner_track_df,limit=40, skip=3)

    output_path = this_dir + "/../inputs/tracks/" + args.bounds_dir + ".csv"
    custom_header = "# x_m, y_m, w_tr_right_m, w_tr_left_m\n"
    with open(output_path, "w") as f:
        f.write(custom_header)
        center_track_df.to_csv(f, index=False, header=False)

    # plot

    # plot the track
    fig = plt.figure()
    plt.plot(outer_track_df["x"], outer_track_df["y"], "r")
    plt.plot(inner_track_df["x"], inner_track_df["y"], "b")
    plt.plot(center_track_df["x_m"], center_track_df["y_m"], "g")
    # plt.plot(outer_track_df["x"], outer_track_df["y"], "ro")
    # plt.plot(inner_track_df["x"], inner_track_df["y"], "bo")
    # plt.plot(center_track_df["x"], center_track_df["y"], "go")
    plt.show()

