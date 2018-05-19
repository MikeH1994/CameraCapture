#!/usr/bin/env python

# Based on code by Jim Easterbrook  jim@jim-easterbrook.me.uk
# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2

from __future__ import print_function

import io
import logging
import os
import subprocess
import sys
import matplotlib.pyplot as plt
import numpy as np
import cv2
import six
import gphoto2 as gp

from PIL import Image

def displayCameras():
    camera_list = []
    for name, addr in gp.check_result(gp.gp_camera_autodetect()):
        camera_list.append((name, addr))
    camera_list.sort(key=lambda x: x[0])

    print ("=============================================")
    print("Cameras:")
    for index, (name, addr) in enumerate(camera_list):
        print('{:d}:  {:s}  {:s}'.format(index, addr, name))
    print ("=============================================")
    
def getCamera(cameraNumber = 0):
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    # make a list of all available cameras
    camera_list = []
    for name, addr in gp.check_result(gp.gp_camera_autodetect()):
        camera_list.append((name, addr))
    camera_list.sort(key=lambda x: x[0])

    if cameraNumber < 0 or cameraNumber >= len(camera_list):
        print('Camera out of range')
        return None
    # initialise chosen camera
    name, addr = camera_list[cameraNumber]
    camera = gp.Camera()
    # search ports for camera port name
    port_info_list = gp.PortInfoList()
    port_info_list.load()
    idx = port_info_list.lookup_path(addr)
    camera.set_port_info(port_info_list[idx])
    camera.init()

    config = gp.check_result(gp.gp_camera_get_config(camera))
    # find the image format config item
    OK, image_format = gp.gp_widget_get_child_by_name(config, 'imageformat')
    if OK >= gp.GP_OK:
        # get current setting
        value = gp.check_result(gp.gp_widget_get_value(image_format))

    OK, capture_size_class = gp.gp_widget_get_child_by_name(
        config, 'capturesizeclass')
    if OK >= gp.GP_OK:
        # set value
        value = gp.check_result(gp.gp_widget_get_choice(capture_size_class, 2))
        gp.check_result(gp.gp_widget_set_value(capture_size_class, value))
        # set config
        gp.check_result(gp.gp_camera_set_config(camera, config))
    return camera

def captureImage(camera):
    if camera==None:
        print("Invalid camera instance")
        return None
    camera_file = gp.check_result(gp.gp_camera_capture_preview(camera))
    file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
    data = memoryview(file_data)
    image = Image.open(io.BytesIO(file_data))
    image = np.array(image)
    return image
    
if __name__ == "__main__":
    displayCameras()
    camera = getCamera(0)
    image = captureImage(camera)
    plt.imshow(image)
    plt.show()
    camera.exit()
