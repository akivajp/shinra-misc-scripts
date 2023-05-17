#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
属性値抽出タスク用の訓練データの妥当性や統計情報をチェックする
'''

import json
import os
import sys

from bs4 import BeautifulSoup

from tqdm.auto import tqdm
from logzero import logger

def main(train_dir):
    annotation_dir = os.path.join(train_dir, 'annotation')
    html_dir = os.path.join(train_dir, 'html')

    dist_paths = []
    categories = []
    for entry in os.listdir(annotation_dir):
        if entry.endswith('_dist.jsonl'):
            categories.append(entry.split('_dist.jsonl')[0])
            dist_paths.append(os.path.join(annotation_dir, entry))
    #logger.debug('dist_paths: %s', dist_paths)
    #logger.debug('categories: %s', categories)
    logger.info('# categories: %s', len(categories))

    count_attributes = 0
    count_pages = 0
    count_cummulative_attribute_names = 0
    map_date_to_counts = {}
    attribute_names = set()
    min_category_attribute_names = 10**10
    max_category_attribute_names = 0
    category_for_max_attribute_names = None
    #for i, dist_path in enumerate(dist_paths):
    map_date_to_sets = {}
    min_page_attributes = 10**10
    max_page_attributes = 0
    info_for_max_page_attributes = None
    min_attributes_per_page_and_attribute_name = 10**10
    max_attributes_per_page_and_attribute_name = 0
    info_for_max_attributes_per_page_and_attribute_name = None
    count_overlapping_offsets_with_single_attribute_names = 0
    count_overlapping_offsets_with_multiple_attribute_names = 0
    count_same_offsets_with_multiple_attribute_names = 0
    for i, dist_path in enumerate(tqdm(
        dist_paths,
        desc='processing categories'
    )):
        category = categories[i]
        #if i >= 1:
        #if i >= 2:
        #    break
        map_page_id_to_date = {}
        map_page_id_to_count_attributes = {}
        map_page_id_to_attribute_offsets = {}
        map_page_id_to_counts = {}
        category_attribute_names = set()
        with open(dist_path, encoding='utf-8') as f:
            #page_set = set()
            for j, line in enumerate(tqdm(
                f,
                desc=f'processing for category: {category}',
                leave=False,
            )):
                #if j > 10:
                #    break
                d = json.loads(line)
                page_id = d['page_id']
                attribute = d['attribute']
                ene = d['ENE']
                title = d['title']
                #logger.debug('d: %s', d)
                #if page_id not in page_set:
                if page_id not in map_page_id_to_date:
                    html_path = os.path.join(html_dir, category, f'{page_id}.html')
                    html = open(html_path, encoding='utf-8').read()
                    #soup = BeautifulSoup(html, 'html.parser')
                    soup = BeautifulSoup(html, 'lxml')
                    #logger.debug('title: %s', soup.title)
                    #logger.debug('title text: %s', soup.title.text)
                    title = soup.title.text.strip()
                    try:
                        if title.find('Wikipedia Dump ') >= 0:
                            dump_date = title.split('Wikipedia Dump ')[1]
                        else:
                            dump_date = title.split('jawiki-')[1]
                    except IndexError as e:
                        logger.debug('title: %s', title)
                        raise e
                    #logger.debug('dump_date: %s', dump_date)
                    map_page_id_to_date[page_id] = dump_date
                    map_page_id_to_count_attributes[page_id] = 0
                    attribute_offsets = []
                    map_page_id_to_attribute_offsets[page_id] = attribute_offsets
                    counts_on_page_id = {}
                    count_on_attribute_name = {}
                    counts_on_page_id['count_on_attribute_name'] = count_on_attribute_name
                    map_page_id_to_counts[page_id] = counts_on_page_id
                else:
                    dump_date = map_page_id_to_date[page_id]
                    attribute_offsets = map_page_id_to_attribute_offsets[page_id]
                    counts_on_page_id = map_page_id_to_counts[page_id]
                    count_on_attribute_name = counts_on_page_id['count_on_attribute_name']
                if dump_date in map_date_to_counts:
                    counts_on_date = map_date_to_counts[dump_date]
                    sets_on_date = map_date_to_sets[dump_date]
                else:
                    counts_on_date = {}
                    sets_on_date = {}
                    #counts_on_date['pages'] = set()
                    counts_on_date['pages'] = 0
                    counts_on_date['attributes'] = 0
                    counts_on_date['attribute_names'] = 0
                    sets_on_date['pages'] = set()
                    sets_on_date['categories'] = set()
                    sets_on_date['attribute_names'] = set()
                    map_date_to_counts[dump_date] = counts_on_date
                    map_date_to_sets[dump_date] = sets_on_date
                if attribute not in count_on_attribute_name:
                    count_on_attribute_name[attribute] = 0
                #page_set.add(page_id)
                count_attributes += 1
                sets_on_date['pages'].add(page_id)
                sets_on_date['categories'].add(ene)
                sets_on_date['attribute_names'].add(attribute)
                counts_on_date['attributes'] += 1
                counts_on_date['pages'] = len(sets_on_date['pages'])
                counts_on_date['categories'] = len(sets_on_date['categories'])
                counts_on_date['attribute_names'] = len(sets_on_date['attribute_names'])
                category_attribute_names.add(attribute)
                attribute_names.add(attribute)
                this_offset = d['html_offset']
                this_offset['attribute'] = attribute
                # NOTE: 既存のオフセットとの重複をチェック
                for offset in attribute_offsets:
                    if this_offset['start']['line_id'] < offset['start']['line_id']:
                        continue
                    if this_offset['start']['line_id'] > offset['end']['line_id']:
                        continue
                    if this_offset['start']['line_id'] == offset['start']['line_id']:
                        if this_offset['start']['offset'] < offset['start']['offset']:
                            continue
                        if this_offset['start']['offset'] >= offset['end']['offset']:
                            # NOTE: end-offsetはその位置を含まない
                            continue
                    # NOTE: 重複している
                    if (
                        this_offset['start']['line_id'] == offset['start']['line_id']
                        and this_offset['start']['offset'] == offset['start']['offset']
                        and this_offset['end']['line_id'] == offset['end']['line_id']
                        and this_offset['end']['offset'] == offset['end']['offset']
                    ):
                        count_same_offsets_with_multiple_attribute_names += 1
                    if this_offset['attribute'] == offset['attribute']:
                        count_overlapping_offsets_with_single_attribute_names += 1
                    else:
                        count_overlapping_offsets_with_multiple_attribute_names += 1
                attribute_offsets.append(this_offset)

                map_page_id_to_count_attributes[page_id] += 1
                if map_page_id_to_count_attributes[page_id] > max_page_attributes:
                    max_page_attributes = map_page_id_to_count_attributes[page_id]
                    info_for_max_page_attributes = dict(
                        category = category,
                        page_id = page_id,
                        title = title,
                    )

                count_on_attribute_name[attribute] += 1
                if count_on_attribute_name[attribute] > max_attributes_per_page_and_attribute_name:
                    max_attributes_per_page_and_attribute_name = count_on_attribute_name[attribute]
                    #info_for_max_attributes_per_page_and_attribute_name = d
                    info_for_max_attributes_per_page_and_attribute_name = dict(
                        category = category,
                        page_id = page_id,
                        title = title,
                        attribute = attribute,
                    )

            #count_pages += len(page_set)
            count_pages += len(map_page_id_to_date)
            count_cummulative_attribute_names += len(category_attribute_names)
            min_category_attribute_names = min(
                min_category_attribute_names,
                len(category_attribute_names),
            )
            #max_category_attribute_names = max(
            #    max_category_attribute_names,
            #    len(category_attribute_names),
            #)
            if len(category_attribute_names) > max_category_attribute_names:
                max_category_attribute_names = len(category_attribute_names)
                category_for_max_attribute_names = category
            for page_id, count in map_page_id_to_count_attributes.items():
                min_page_attributes = min(min_page_attributes, count)
                #max_page_attributes = max(max_page_attributes, count)
            #for attribute, count in count_on_attribute_name.items():
            #    min_attributes_per_page_and_attribute_name = min(
            #        min_attributes_per_page_and_attribute_name, count
            #    )
            #    #max_attributes_per_page_and_attribute_name = max(
            #    #    max_attributes_per_page_and_attribute_name, count
            #    #)
            for page_id, counts_on_page_id in map_page_id_to_counts.items():
                for attribute, count in counts_on_page_id['count_on_attribute_name'].items():
                    min_attributes_per_page_and_attribute_name = min(
                        min_attributes_per_page_and_attribute_name, count
                    )
                    #max_attributes_per_page_and_attribute_name = max(
                    #    max_attributes_per_page_and_attribute_name, count
                    #)

    logger.info('# total attributes: %s', count_attributes)
    logger.info('# total pages: %s', count_pages)
    logger.info('min category attribute names: %s', min_category_attribute_names)
    logger.info('max category attribute names: %s', max_category_attribute_names)
    logger.info('category for max attribute names: %s', category_for_max_attribute_names)
    logger.info('unique attribute names: %s', len(attribute_names))
    logger.info('cumulative attribute names: %s', count_cummulative_attribute_names) 
    logger.info('min page attributes: %s', min_page_attributes)
    logger.info('max page attributes: %s', max_page_attributes)
    logger.info('info for max page attributes: %s', info_for_max_page_attributes)
    logger.info('min attributes per page and attribute name: %s', min_attributes_per_page_and_attribute_name)
    logger.info('max attributes per page and attribute name: %s', max_attributes_per_page_and_attribute_name)
    logger.info('info for max attributes per page and attribute name: %s', info_for_max_attributes_per_page_and_attribute_name)
    logger.info('# same offsets with multiple attribute names: %s', count_same_offsets_with_multiple_attribute_names)
    logger.info('# overlapping offsets with single attribute names: %s', count_overlapping_offsets_with_single_attribute_names)
    logger.info('# overlapping offsets with multiple attribute names: %s', count_overlapping_offsets_with_multiple_attribute_names)
    logger.info('map_date_to_counts: %s', map_date_to_counts)

if __name__ == '__main__':
    main(sys.argv[1])
