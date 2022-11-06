#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Wikipedia記事HTMLファイルのディレクトリから冒頭の警告テキストを除去する
'''

import os
import shutil
import sys

from logzero import logger
from tqdm import tqdm

warning_html_dir = sys.argv[1]
target_html_dir = sys.argv[2]

if not os.path.exists(target_html_dir):
    os.makedirs(target_html_dir)

with os.scandir(warning_html_dir) as it:
    for entry in tqdm(it):
        if not entry.is_file():
            continue
        input_html = entry.path
        with open(input_html) as f:
            logger.debug('input file: %s', input_html)
            f_out = None
            for i, line in enumerate(f):
                if i == 0:
                    logger.debug('first line: %s', line)
                    if line.strip() == '<br />':
                        #logger.debug('OK')
                        pass
                    elif line.strip() == '<!DOCTYPE html>':
                        pass
                    else:
                        logger.debug('NG')
                        sys.exit(1)
                        break
                if i == 1:
                    logger.debug('second line: %s', line)
                    if line.startswith('<b>Warning</b>:'):
                        #logger.debug('OK')
                        pass
                    elif line.startswith('<html class'):
                        #logger.debug('OK')
                        pass
                    else:
                        logger.debug('NG')
                        sys.exit(1)
                        break
                if i == 2:
                    base = os.path.basename(input_html)
                    output_html = os.path.join(target_html_dir, base)
                    logger.debug('output file: %s', output_html)
                    f_out = open(output_html, 'w')
                if i >= 2:
                    f_out.write(line)
        #break
