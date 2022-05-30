#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    HTMLディレクトリからページリストに存在するものだけを取得しなおす
"""

import csv
#import json
import os
import sys

from logzero import logger
from tqdm import tqdm

input_titles_path = sys.argv[1]
input_errors_path = sys.argv[2]
input_html_dir_path = sys.argv[3]
output_html_dir_path = sys.argv[4]

offset = 0
if len(sys.argv) >= 6:
    offset = int(sys.argv[5])

page_ids = []

with open(input_titles_path) as f:
    reader = csv.reader(f, delimiter='\t')
    for i, row in enumerate(tqdm(reader)):
        #if i > 100:
        #    break
        page_id = row[0]
        namespace = row[1]
        title = row[2]
        if namespace == '0':
            page_ids.append(page_id)
#logger.debug('page ids: %s', page_ids)

redirect_ids = []

with open(input_errors_path) as f:
    reader = csv.reader(f)
    for i, row in enumerate(tqdm(reader)):
        #if i > 100:
        #    break
        page_id = row[0]
        title = row[1]
        error = row[2]
        if error.find('redirect=') == 0:
            redirect_ids.append(page_id)
#logger.debug('redirect ids: %s', redirect_ids)

os.makedirs(output_html_dir_path, exist_ok = True)

for i, page_id in enumerate(tqdm(page_ids)):
    if int(page_id) < offset:
        continue
    path_from = os.path.join(input_html_dir_path, page_id + '.html')
    path_to   = os.path.join(output_html_dir_path, page_id + '.html')
    if page_id in redirect_ids:
        continue
    if not os.path.exists(path_from):
        logger.error('File not exists: %s', path_from)
        sys.exit(1)
    if not os.path.exists(path_to):
        os.link(path_from, path_to)
