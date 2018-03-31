__author__ = 'matt'

from os import listdir
from os.path import join, isdir, isfile

import json


EXT_FULL = '.f4kgt'
EXT_PARTIAL = EXT_FULL + '.partial'
EXTS = [EXT_FULL, EXT_PARTIAL]


def get_files_in_dir(directory='.', ignore_hidden=True, ext=None):
    files = [f for f in listdir(directory) if isfile(join(directory, f))]
    data = [f for f in files if not f.startswith(".")] if ignore_hidden else files

    if ext is not None and isinstance(ext, str):
        data = [f for f in files if f.endswith(ext)]

    return set([x.split('.')[0] for x in data])


full = get_files_in_dir(ext=EXT_FULL)
part = get_files_in_dir(ext=EXT_PARTIAL)


def load_and_compare(video_id):
    try:
        full_gt = json.load(open(video_id + EXT_FULL))
    except IOError:
        part_gt = json.load(open(video_id + EXT_PARTIAL))

        for k in part_gt.iterkeys():
            print("{},{},{},{}".format(video_id, int(k), 'NP', int(part_gt[k])))

    part_gt = json.load(open(video_id + EXT_PARTIAL))

    for k in part_gt.iterkeys():
        try:
            if full_gt[k] != part_gt[k]:
                print("{},{},{},{}".format(video_id, int(k), int(full_gt[k]), int(part_gt[k])))
        except KeyError:
            if k in full_gt:
                print("{},{},{},{}".format(video_id, int(k), int(full_gt[k]), 'NP'))
            elif k in part_gt:
                print("{},{},{},{}".format(video_id, int(k), 'NP', int(part_gt[k])))


def perform_fix():
    for filename in part:
        try:
            full_gt = json.load(open(filename + EXT_FULL))
            part_gt = json.load(open(filename + EXT_PARTIAL))
        except IOError:
            print('Can\'t find file {}'.format(filename))
            continue

        full_gt.update(part_gt)
        json.dump(full_gt, open(filename + EXT_FULL, 'w'))

        print('Updated video {}'.format(filename))


if __name__ == '__main__':
    for vid in part:
        load_and_compare(vid)

    x = raw_input('Would you like to perform the merge [y/n]? ').lower().strip()[0]

    if x == 'y':
        perform_fix()
    else:
        print('Exiting without having performed changes.')

