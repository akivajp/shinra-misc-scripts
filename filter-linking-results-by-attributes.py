#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    リンキングタスクの結果を属性値抽出の結果でフィルタリングする
'''

import json
import sys

from logzero import logger
from tqdm import tqdm

attributes_path = sys.argv[1]
linking_path = sys.argv[2]

def get_key(d):
    page_id = d['page_id']
    title = d['title']
    ene = d['ENE']
    attribute = d['attribute']
    html_offset = d['html_offset']
    start = html_offset['start']
    start_line = start['line_id']
    start_offset = start['offset']
    end = html_offset['end']
    end_line = end['line_id']
    end_offset = end['offset']
    text = html_offset['text']
    key = (page_id, ene, attribute, start_line, start_offset, end_line, end_offset, text)
    return key


linking_results = {}
with open(linking_path, 'r') as f:
    for line in tqdm(f):
        d = json.loads(line)
        key = get_key(d)
        #logger.info('key: %s', key)
        linking_results[key] = d

with open(attributes_path, 'r') as f:
    for line in tqdm(f):
        d = json.loads(line)
        #logger.info('d: %s', d)
        key = get_key(d)
        if key in linking_results:
            found = linking_results[key]
            print(json.dumps(found, ensure_ascii=False))
        else:
            del d['score']
            d['link_page_id'] = None
            print(json.dumps(d, ensure_ascii=False))
