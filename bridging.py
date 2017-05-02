# coding=utf-8
from __future__ import absolute_import

import argparse
import os

from bridges import wp


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Options of starting bridging.')

    parser.add_argument(dest='path',
                        action='store',
                        help='Path of data source.')

    parser.add_argument('--wp',
                        dest='wp',
                        action='store_const',
                        const=True,
                        help='Use Wordpress data source.')

    args, unknown = parser.parse_known_args()
    if not os.path.isfile(args.path):
        raise Exception('')
    if args.wp:
        wp.load_json_data(args.path)
