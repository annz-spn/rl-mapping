import rosbag
import rospy
from roslib import message
import sensor_msgs.point_cloud2 as pcl
import numpy as np


def read_map_pointcloud(fname, topic='/lidar/octomap_binary'):
    maps = []
    ts = []
    with rosbag.Bag(fname) as bag:
        for topic, msg, t in bag.read_messages(topics=[topic]):
            #print(msg)
            point_gen = pcl.read_points(
                msg,
                skip_nans=True,
                field_names=('x','y','z')
            )
            x, y, z = [], [], []
            for point in point_gen:
                x.append(point[0])
                y.append(point[1])
                z.append(point[2])
            x, y, z = np.array(x), np.array(y), np.array(z)
            grid = build_map(x, y, z)
            maps.append(grid)
            # msg_points = np.array([point for point in point_gen])
            # maps.append(msg_points)
            ts.append(t.to_sec())
    return np.array(maps), np.array(ts)


def build_grid(x, y):
    map_height, map_width = 80, 80
    grid_scale = 0.1
    voxel_size = 0.2
    r = voxel_size / 2

    grid = np.zeros((int(map_width / grid_scale), int(map_height / grid_scale)), dtype=int)
    x_from = (np.round(x + int(map_width / 2) - r, decimals=5) / grid_scale).astype(int).flatten()
    x_to = (np.round(x + int(map_width / 2) + r, decimals=5) / grid_scale).astype(int).flatten()
    y_from = (np.round(y + int(map_height / 2) - r, decimals=5) / grid_scale).astype(int).flatten()
    y_to = (np.round(y + int(map_height / 2) + r, decimals=5) / grid_scale).astype(int).flatten()

    for x1, x2, y1, y2 in zip(x_from, x_to, y_from, y_to):
        for i in (x1, x2 + 1):
            for j in (y1 , y2 + 1):
                grid[i, j] = 1
                
    return grid


def build_map(x, y, z, z_threshold_upper=1, z_threshold_lower=0):
    arg_ok = np.argwhere((z >= z_threshold_lower) & (z <= z_threshold_upper))
    x_new = x[arg_ok]
    y_new = y[arg_ok]
    grid = build_grid(x_new, y_new)
    return grid
