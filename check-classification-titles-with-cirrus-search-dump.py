#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
分類タスク用の全件データとCirrus Search Dumpでタイトルの一致を確認する
'''

import json
import sys

from tqdm.auto import tqdm
from logzero import logger

def main(cirrus_search_dump_path, annotation_jsonl_path, fixed_jsonl_path):
    cirrus_dict = {}
    with open(cirrus_search_dump_path, encoding='utf-8') as f:
        for i, line in enumerate(tqdm(
            f,
            desc=f'scanning cirrus search dump: {cirrus_search_dump_path}',
        )):
            #if i > 2:
            #    break
            d = json.loads(line)
            if i % 2 == 0:
                index = d['index']
                if index.get('_type') != 'page':
                    page_id = None
                    continue
                page_id = d['index']['_id']
                #cirrus_dict[page_id] = title
            else:
                #logger.debug('d keys: %s', d.keys())
                if page_id is not None:
                    title = d['title']
                    #logger.debug('title: %s', title)
                    cirrus_dict[page_id] = title

    numFixed = 0
    with open(fixed_jsonl_path, 'w', encoding='utf-8') as f_fixed:
        with open(annotation_jsonl_path, encoding='utf-8') as f:
            for line in tqdm(
                f,
                desc=f'scanning annotation jsonl: {annotation_jsonl_path}',
            ):
                d = json.loads(line)
                page_id = d['page_id']
                if page_id not in cirrus_dict:
                    #logger.error(f'page_id {page_id} is not in cirrus search dump')
                    #continue
                    raise Exception(f'page_id {page_id} is not in cirrus search dump')
                if d['title'] != cirrus_dict[page_id]:
                    #logger.error(f'page_id {page_id} title is different')
                    #logger.error(f'cirrus: {cirrus_dict[page_id]}')
                    #logger.error(f'annotation: {d["title"]}')
                    d['title'] = cirrus_dict[page_id]
                    numFixed += 1
                f_fixed.write(json.dumps(d, ensure_ascii=False))
                f_fixed.write('\n')
    logger.info('numFixed: %s', numFixed)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
