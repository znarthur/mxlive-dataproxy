from django.conf import settings
from django.shortcuts import get_object_or_404

from downloads.models import SecurePath

import os
import cv2
import numpy
import shutil


MIN_MAX_PERCENTILES = (1, 99.85)


DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
CACHE_DIR = getattr(settings, 'DOWNLOAD_CACHE_DIR', '/tmp')

COLOR_MAP = numpy.array([[[i, i, i]] for i in reversed(range(256))], dtype=numpy.uint8)


def get_download_path(key):
    """Convenience method to return a path for a key"""
    obj = get_object_or_404(SecurePath, key=key)
    return obj.path


def load_image(filename, brightness=0.0, resolution=(1024, 1024)):
    from mxio import read_image
    """
    Read file and return an PIL image of desired resolution histogram
    :param filename: Image File (e.g. filename.img, filename.cbf)
    :param resolution: output size
    :return: resized PIL image
    """
    obj = read_image(filename)

    w, h = obj.frame.data.shape
    sub_data = obj.frame.data[:h//2, :w//2]
    selected = (sub_data >= 0) & (sub_data < obj.frame.cutoff_value)
    stats_data = sub_data if not selected.sum() else sub_data[selected]

    minimum, maximum = numpy.percentile(stats_data, MIN_MAX_PERCENTILES)
    img0 = cv2.convertScaleAbs(obj.frame.data - minimum, None, brightness * 255 / max(maximum, 1), 0)
    img1 = cv2.applyColorMap(img0, COLOR_MAP)
    image = cv2.cvtColor(img1, cv2.COLOR_BGR2BGRA)
    image = cv2.resize(image, resolution, interpolation=cv2.INTER_AREA)
    return image


def create_png(filename, output, brightness, resolution=(1024, 1024)):
    """
    Generate png in output using filename as input with specified brightness
    and resolution. default resolution is 1024x1024
    creates a directory for output if none exists
    :param filename: Image File (e.g. filename.img, filename.cbf)
    :param output: PNG Image Filename
    :param brightness: float (1.5=dark; -0.5=light)
    :param resolution: output size
    :return: PNG Image
    """
    img_info = load_image(filename, brightness, resolution)
    dir_name = os.path.dirname(output)
    if not os.path.exists(dir_name) and dir_name != '':
        os.makedirs(dir_name)
    cv2.imwrite(output, img_info)


def get_missing_image(src='frame-missing.png'):
    """Return full path to missing file placeholder"""
    missing_file = os.path.join(CACHE_DIR, src)
    src_file = os.path.join(DATA_DIR, src)
    if not os.path.exists(missing_file):
        shutil.copy(src_file, missing_file)
    return missing_file


def get_missing_frame():
    return get_missing_image(src='frame-missing.png')


def get_missing_snapshot():
    return get_missing_image(src='snapshot-missing.gif')