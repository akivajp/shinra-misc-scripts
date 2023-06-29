#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
分類タスク用の全件データとスプリットデータで内容が一致しているかを確認
'''

import json
import os
import sys

#from bs4 import BeautifulSoup

from tqdm.auto import tqdm
from logzero import logger

def deep_compare(d1: dict, d2: dict):
    for k, v in d1.items():
        if k not in d2:
            logger.error(f'{k} is not in d2')
            return False
        if isinstance(v, dict):
            if not deep_compare(v, d2[k]):
                return False
        elif isinstance(v, list):
            if len(v) != len(d2[k]):
                logger.error(f'{k} length is different')
                return False
            for i in range(len(v)):
                if not deep_compare(v[i], d2[k][i]):
                    return False
        else:
            if v != d2[k]:
                logger.error(f'{k} is different: {v} != {d2[k]}')
                return False
    return True

def main(all_jsonl_path, split_jsonl_path, fixed_jsonl_path):
    split_dict = {}
    page_ids = []
    with open(split_jsonl_path, encoding='utf-8') as f:
        for line in tqdm(f, desc=f'loading split jsonl: {split_jsonl_path}'):
            d = json.loads(line)
            page_id = d['page_id']
            split_dict[page_id] = d
            page_ids.append(page_id)

    all_in_split_dict = {}
    with open(all_jsonl_path, encoding='utf-8') as f:
        for line in tqdm(f, desc=f'scanning all jsonl: {all_jsonl_path}'):
            d = json.loads(line)
            page_id = d['page_id']
            if page_id not in split_dict:
                continue
            all_in_split_dict[page_id] = d

    with open(fixed_jsonl_path, 'w', encoding='utf-8') as f:
        for page_id in tqdm(page_ids, desc='processing page ids'):
            if page_id not in all_in_split_dict:
                raise Exception(f'page_id {page_id} is not in {all_jsonl_path}')
            d_split = split_dict[page_id]
            d_all = all_in_split_dict[page_id]
            d_new = {}
            d_new['page_id'] = d_all['page_id']
            d_new['title'] = d_all['title']
            d_new['ENEs'] = d_all['ENEs']
            if not deep_compare(d_split, d_all):
                logger.warning(f'd_split: {d_split}')
                logger.warning(f'd_all: {d_all}')
                logger.warning(f'd_new: {d_new}')
            f.write(json.dumps(d_new, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
