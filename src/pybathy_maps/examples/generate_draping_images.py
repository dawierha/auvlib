#!/usr/bin/python

from pydata_tools import data_structures, gsf_data, xtf_data, csv_data
from pybathy_maps import mesh_map, patch_draper, map_draper
import matplotlib.pyplot as plt
import sys
import os
import numpy as np
import math

def parse_or_load_gsf(path):

    if os.path.exists("gsf_cache.cereal"):
        gsf_pings = gsf_data.gsf_mbes_ping.read_data("gsf_cache.cereal")
    else:
        gsf_pings = gsf_data.gsf_mbes_ping.parse_folder(path)
        gsf_data.write_data(gsf_pings, "gsf_cache.cereal")
    return gsf_pings

def parse_or_load_csv(path):

    if os.path.exists("csv_cache.cereal"):
        entries = csv_data.csv_nav_entry.read_data("csv_cache.cereal")
    else:
        entries = csv_data.csv_nav_entry.parse_file(path)
        csv_data.write_data(entries, "csv_cache.cereal")
    return entries

def parse_or_load_xtf(path):

    if os.path.exists("xtf_cache.cereal"):
        xtf_pings = xtf_data.xtf_sss_ping.read_data("xtf_cache.cereal")
    else:
        xtf_pings = xtf_data.xtf_sss_ping.parse_folder(path)
        #nav_entries = csv_data.csv_nav_entry.parse_file(csv_path)
        xtf_data.write_data(xtf_pings, "xtf_cache.cereal")
    return xtf_pings

def create_mesh(path):

    gsf_pings = parse_or_load_gsf(path)
    mbes_pings = gsf_data.convert_pings(gsf_pings)
    V, F, bounds = mesh_map.mesh_from_pings(mbes_pings, 0.5)

    return V, F, bounds

def match_or_load_xtf(xtf_path, csv_path):

    if os.path.exists("matched_cache.cereal"):
        xtf_pings = xtf_data.xtf_sss_ping.read_data("matched_cache.cereal")
    else:
        xtf_pings = parse_or_load_xtf(xtf_path)
        nav_entries = parse_or_load_csv(csv_path)
        xtf_pings = csv_data.convert_matched_entries(xtf_pings, nav_entries)
        xtf_data.write_data(xtf_pings, "matched_cache.cereal")
    return xtf_pings

class MapImageSaver(object):

    def __init__(self):

        self.map_images = []

    def save_callback(self, map_image):

        print "Got sss map image callback!"
        #plt.imshow(map_image.sss_map_image, cmap=plt.jet())
        #plt.show()
        self.map_images.append(map_image)
        map_draper.write_data(self.map_images, "map_images_cache.cereal")

V, F, bounds = create_mesh(sys.argv[1])

xtf_pings = match_or_load_xtf(sys.argv[2], sys.argv[3])
xtf_pings = xtf_data.correct_sensor_offset(xtf_pings, np.array([2., -1.5, 0.]))

sound_speeds = csv_data.csv_asvp_sound_speed.parse_file(sys.argv[4])

#patch_draper.generate_draping(V, F, bounds, xtf_pings, sound_speeds)
resolution = 30./8.
sensor_yaw = 5.*math.pi/180.

saver = MapImageSaver()
map_images = map_draper.drape_maps(V, F, bounds, xtf_pings, sound_speeds, sensor_yaw, resolution, saver.save_callback)
map_draper.write_data(map_images, "map_images.cereal")
