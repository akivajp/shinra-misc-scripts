#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Wikipedia記事HTMLファイルのディレクトリからIDとタイトルの対応一覧を出力 (ENE情報付き)
'''

import bisect
import csv
import json
import os
import shutil
import sys

from bs4 import BeautifulSoup
from logzero import logger
from tqdm import tqdm

all_titles_path = sys.argv[1]
ene_prediction_path = sys.argv[2]
html_dir = sys.argv[3]

id2title = {}
with open(all_titles_path) as f:
    reader = csv.reader(f, delimiter='\t')
    for row in tqdm(reader):
        #logger.debug('row: %s', row)
        page_id, ns, title = row
        #id2title[page_id] = title
        id2title[int(page_id)] = title

id2ene = {}
with open(ene_prediction_path) as f:
    for line in tqdm(f):
        d = json.loads(line)
        #logger.debug('data: %s', d)
        pageid = int(d['pageid'])
        ene_list = []
        enes = d['ENEs']
        for tag, probs in enes.items():
            for prob in probs:
                ene_list.append(prob['ENE_ja'])
        id2ene[pageid] = str.join(',', ene_list)
        #break

#sys.exit(1)

found_ids = []
with os.scandir(html_dir) as it:
    for entry in tqdm(it):
        #logger.debug('entry: %s', entry)
        #logger.debug('entry name: %s', entry.name)
        #logger.debug('entry path: %s', entry.path)
        #logger.debug('entry file: %s', entry.is_file())
        page_id, ext = os.path.splitext(entry.name)
        #logger.debug('pageid: %s', page_id)
        #break
        if not entry.is_file():
            continue
        #target_html = entry.path
        #with open(target_html) as f:
        #    soup = BeautifulSoup(f, 'html.parser')
        #    if not soup.title:
        #        sys.exit(1)
        #    logger.debug('title text: %s', soup.title.text)
        #    title = soup.title.text
        #if page_id in id2title:
        #    title = id2title[page_id]
        #    logger.debug('title: %s', title)
        bisect.insort(found_ids, int(page_id))

#for page_id in found_ids:
for page_id in tqdm(found_ids):
    #logger.debug('page id: %s', page_id)
    #if page_id not in id2title:
    #    continue
    title = id2title[page_id]
    if page_id in id2ene:
        ene = id2ene[page_id]
    else:
        ene = 'NOT_IN_CIRRUS_DUMP'
    #logger.debug('page id: %s, title: %s', page_id, title)
    print(f'{page_id}\t{title}\t{ene}')
