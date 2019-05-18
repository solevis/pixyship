# https://pixelstarships.s3.amazonaws.com/1241.png
import os
from urllib import request

from ps_client import PixelStarshipsApi

IMAGE_DIR = 'images'
PS_ASSET_URL = 'https://pixelstarships.s3.amazonaws.com/{}.png'


def find_last_image_id():
    entries = os.listdir(IMAGE_DIR)
    ids = [int(e.replace('.png', '')) for e in entries if '.png' in e]
    return max(ids)


def old_get_assets(start_id=None, quit_after=10):
    start_id = start_id or find_last_image_id()
    if start_id == 0:
        quit_after = 100    # When starting from the beginning there can be large gaps

    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    id_list = range(start_id, start_id + 10000)
    misses = 0

    for num in id_list:
        filename = IMAGE_DIR + '/{}.png'.format(num)
        if not os.path.isfile(filename):
            print('getting', filename)
            url = PS_ASSET_URL.format(num)
            try:
                request.urlretrieve(url, filename)
                misses = 0
            except Exception as e:
                misses += 1
                print(misses, type(e))
                if misses >= quit_after:
                    break


def get_assets():
    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    psa = PixelStarshipsApi()
    sprites = psa.sprite_map

    for k, v in sprites.items():
        num = v['image_file']
        print(k, num)
        filename = IMAGE_DIR + '/{}.png'.format(num)

        if not os.path.isfile(filename):
            print('getting', filename)
            url = PS_ASSET_URL.format(num)
            try:
                request.urlretrieve(url, filename)
            except Exception as e:
                print('ERROR', e)


if __name__ == '__main__':
    get_assets()
