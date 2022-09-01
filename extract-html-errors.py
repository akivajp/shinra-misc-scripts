#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
    Wikipedia記事HTMLファイルのディレクトリからエラーが含まれるものを分離
'''

import os
import shutil
import sys

from bs4 import BeautifulSoup
from logzero import logger
from tqdm import tqdm

REGULAR_ERROR_PAGE_ID = '146616'
ERROR_TITLE = 'エラー - Wikipedia'

#target_html = sys.argv[1]
html_dir = sys.argv[1]
error_dir = sys.argv[2]
fatal_dir = sys.argv[3]
empty_dir = sys.argv[4]
warning_dir = sys.argv[5]

def check_title_error(path, soup):
    base = os.path.basename(path)
    #logger.debug('base: %s', base)
    stem, ext = os.path.splitext(base)
    #logger.debug('stem: %s', stem)
    #logger.debug('title: %s', soup.title)
    if not soup.title:
        return False
    #logger.debug('title text: %s', soup.title.text)
    title = soup.title.text
    if title == ERROR_TITLE:
        if stem != REGULAR_ERROR_PAGE_ID:
            logger.warning('title error: %s', path)
            if not os.path.exists(error_dir):
                os.makedirs(error_dir)
            shutil.move(path, error_dir)
            return True

def check_fatal_error(path, soup):
    #logger.debug('soup: %s', soup)
    first_b = soup.find('b')
    if not first_b:
        return False
    if first_b.text == 'Fatal error':
        logger.warning('fatal error: %s', path)
        if not os.path.exists(fatal_dir):
            os.makedirs(fatal_dir)
        shutil.move(path, fatal_dir)
        return True

def check_empty(path, soup):
    #logger.debug('soup: %s', soup)
    #logger.debug('soup: %s', bool(soup))
    #logger.debug('soup text: %s', soup.text)
    #logger.debug('soup: %s', bool(soup.text))
    if not soup.text:
        logger.warning('empty: %s', path)
        if not os.path.exists(empty_dir):
            os.makedirs(empty_dir)
        shutil.move(path, empty_dir)
        return True

def check_warning(path, soup):
    #logger.debug('soup: %s', soup)
    first_b = soup.find('b')
    if not first_b:
        return False
    if first_b.text == 'Warning':
        logger.warning('warning: %s', path)
        if not os.path.exists(warning_dir):
            os.makedirs(warning_dir)
        shutil.move(path, warning_dir)
        return True

with os.scandir(html_dir) as it:
    for entry in tqdm(it):
        #logger.debug('entry: %s', entry)
        #logger.debug('entry name: %s', entry.name)
        #logger.debug('entry path: %s', entry.path)
        #logger.debug('entry file: %s', entry.is_file())
        #break
        if not entry.is_file():
            continue
        target_html = entry.path
        with open(target_html) as f:
            soup = BeautifulSoup(f, 'html.parser')
            check_title_error(target_html, soup)
            check_fatal_error(target_html, soup)
            check_empty(target_html, soup)
            check_warning(target_html, soup)
