import numpy as np 
import os

from . import lidar_map, coloradar_utils as radar
from ..utils import find_nearest


def load_sample(heatmaps_dir, maps_dir, params):
    hm_bin_dir = os.path.join(heatmaps_dir, 'data')
    assert os.path.isdir(hm_bin_dir)

    hm_filenames = np.array(os.listdir(hm_bin_dir))
    hm_ts_filename = os.path.join(heatmaps_dir, 'timestamps.txt')
    with open(hm_ts_filename, mode='r') as file:
        hm_ts = np.array(list(map(float, file.readlines())))

    print('Reading maps...')
    if maps_dir.endswith('.bag'):
        maps, map_ts = lidar_map.read_map_pointcloud(maps_dir, topic='/lidar/octomap_point_cloud_centers')
    else:
        raise ValueError("Can't find maps")

    selected_heatmap_idx = find_nearest(smaller=map_ts, bigger=hm_ts)
    selected_hm_filenames = hm_filenames[selected_heatmap_idx]
    heatmaps = []
    print('Reading heatmaps...')
    for fname in selected_hm_filenames:
        path = os.path.join(hm_bin_dir, fname)
        heatmaps.append(radar.read_heatmap(path, params))
    heatmaps = np.array(heatmaps)

    print(heatmaps.shape, maps.shape)    
    return heatmaps, maps


def load_coloradar(heatmap_dirs, map_dirs, calib_dir):
    assert len(heatmap_dirs) == len(map_dirs)
    assert os.path.isdir(calib_dir)
    params = radar.get_single_chip_params(calib_dir)['heatmap']
    print('params')
    print(params)
    X, Y = [], []
    for hm_dir, map_dir in zip(heatmap_dirs, map_dirs):
        print(hm_dir)
        print(map_dir)
        assert os.path.isdir(hm_dir) 
        assert os.path.exists(map_dir)
        heatmaps, maps = load_sample(hm_dir, map_dir, params)
        X.append(heatmaps)
        Y.append(maps)

    X, Y = np.array(X), np.array(Y)
    return X, Y


if __name__ == '__main__':
    # bag_path = '/media/giantdrive/coloradar/bags'
    # bags = ['12_21_2020_arpg_lab_run0.bag', '12_21_2020_arpg_lab_run1.bag', '12_21_2020_ec_hallways_run0.bag', '12_21_2020_ec_hallways_run1.bag']
    load_coloradar(
        heatmap_dirs=['/home/ann/project/radar/hallways_run0/single_chip/heatmaps'], 
        map_dirs=['/home/ann/project/radar/octomap_testing_pcl.bag'], 
        calib_dir='/home/ann/project/radar/calib')
        # calib_dir='/media/giantdrive/coloradar/calib')