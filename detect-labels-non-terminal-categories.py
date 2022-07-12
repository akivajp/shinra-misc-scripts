#!/usr/bin/env python3

'''
    JSONLファイルから非終端カテゴリを検出する
'''

import json
import sys

from logzero import logger
from tqdm import tqdm

definition_jsonl_path = sys.argv[1]
target_jsonl_path = sys.argv[2]

#ene_ids = set()
terminal_ene_ids = set()
non_terminal_ene_ids = set()
with open(definition_jsonl_path, 'r') as f:
    for i, line in enumerate(tqdm(f)):
        d = json.loads(line)
        ene_id = d['ENE_id']
        #ene_ids.add(ene_id)
        children = d['children_category']
        if len(children) > 0:
            non_terminal_ene_ids.add(ene_id)
        else:
            terminal_ene_ids.add(ene_id)
#logger.debug('# ene_ids: %s', len(ene_ids))
logger.debug('# terminal_ene_ids: %s', len(terminal_ene_ids))
logger.debug('# non_terminal_ene_ids: %s', len(non_terminal_ene_ids))

num_labels_with_terminal_category = 0
num_labels_with_non_terminal_category = 0
with open(target_jsonl_path, 'r') as f:
    for i, line in enumerate(tqdm(f)):
        d = json.loads(line)
        enes = d['ENEs']
        for key, probs in enes.items():
            for prob in probs:
                ene = prob['ENE']
                if ene in terminal_ene_ids:
                    num_labels_with_terminal_category += 1
                elif ene in non_terminal_ene_ids:
                    num_labels_with_non_terminal_category += 1
                else:
                    logger.warning('unknown ene: %s', ene)
logger.debug('# labels with terminal category: %s', num_labels_with_terminal_category)
logger.debug('# labels with non terminal category: %s', num_labels_with_non_terminal_category)
