#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    新しく追加したページを特定する
"""

import json
import sys

from logzero import logger
from tqdm import tqdm

classification_jsonl_path = sys.argv[1]
last_page_id = int(sys.argv[2])

with open(classification_jsonl_path) as f:
    for i, line in enumerate(tqdm(f)):
        d = json.loads(line)
        page_id = int(d['page_id'])
        if page_id > last_page_id:
            sys.stdout.write(line)

