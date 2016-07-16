#!/usr/bin/env python
# -*- coding:utf8 -*-

import os
import PIL
from PIL import Image

SIZE = (75,75)
SAVE_DIRECTORY = 'thumbs'

def get_image_paths(folder):
    return (os.path.join(folder, f)
            for f in os.listdir(folder)
            if 'jpeg' in f)

def create_thumbnail(filename):
    im = Image.open(filename)
    im.thumbnail(SIZE, Image.ANTIALIAS)
    base, fname = os.path.split(filename)
    save_path = os.path.join(base, SAVE_DIRECTORY, fname)
    im.save(save_path)

folder = os.path.abspath(
    '11_18_2013_R000_IQM_Big_Sur_Mon__e10d1958e7b766c3e840')
os.mkdir(os.path.join(folder, SAVE_DIRECTORY))

images = get_image_paths(folder)

#高cpu同步用进程池
from multiprocessing import Pool
pool = Pool()
pool.map(create_thumbnail, images)
pool.close()
pool.join()


#高cpu同步用进程池
from multiprocessing import Pool
import multiprocessing
pool = Pool(multiprocessing.cpu_count())
results = pool.map_async(create_thumbnail, images)
pool.close()
pool.join()

print results.wait(timeout=10)
print results.successful()
print results.ready()
for item in results.get(timeout=10):
    print item
