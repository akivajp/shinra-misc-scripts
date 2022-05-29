#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    分類用JSONLファイルのタイトルとCirrus Search Dumpのタイトルの不一致を特定し、修正版を出力する
"""

import csv
import gzip
import json
import sys

from logzero import logger
from tqdm import tqdm

cirrus_dump_path = sys.argv[1]
classification_json_path = sys.argv[2]
output_diff_tsv_path = sys.argv[3]
output_title_corrected_json_path = sys.argv[4]

cirrus_id_to_title = {}

#with open(cirrus_dump_path, 'r') as f:
with gzip.open(cirrus_dump_path, 'rt') as g:
    #g = gzip.GzipFile(fileobj=f, encoding='utf-8')
    for i, line in enumerate(tqdm(g)):
        #if i > 100000:
        #    break
        d = json.loads(line)
        if i % 2 == 0:
            assert d['index']['_type'] == 'page'
            page_id = str(d['index']['_id'])
        if i % 2 == 1:
            title = d['title']
            cirrus_id_to_title[page_id] = title

tsv_writer = csv.DictWriter(
    open(output_diff_tsv_path, 'w'),
    fieldnames=['page_id', 'wrong_title', 'correct_title'],
    delimiter='\t',
)
tsv_writer.writeheader()

correct_writer = open(output_title_corrected_json_path, 'w')

with open(classification_json_path, 'r') as f:
    for i, line in enumerate(tqdm(f)):
        #if i > 100:
        #    break
        d = json.loads(line)
        #logger.debug('d: %s', d)
        page_id = str(d['pageid'])
        sampled_title = d['title']
        if page_id not in cirrus_id_to_title:
            logger.warning('page_id %s not in cirrus_id_to_title', page_id)
            #continue
            sys.exit(1)
        cirrus_title = cirrus_id_to_title[page_id]
        #if True:
        if cirrus_title != sampled_title:
            #logger.debug('page id: %s', page_id)
            #logger.debug('cirrus title: %s', cirrus_title)
            #logger.debug('sampled title: %s', sampled_title)
            #logger.debug('--')
            rec = {}
            rec['page_id'] = page_id
            rec['wrong_title'] = sampled_title
            rec['correct_title'] = cirrus_title
            tsv_writer.writerow(rec)
        d['title'] = cirrus_title
        correct_writer.write(json.dumps(d, ensure_ascii=False) + '\n')
