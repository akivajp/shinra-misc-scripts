#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
リンキングタスク用の訓練データの妥当性や統計情報をチェックする
'''

import json
import os
import sys

from bs4 import BeautifulSoup

from tqdm.auto import tqdm
from logzero import logger

def get_attribute_key(rec):
    return (
        rec['page_id'],
        rec['attribute'],
        #rec['ENE']
        rec['html_offset']['start']['line_id'],
        rec['html_offset']['start']['offset'],
        rec['html_offset']['end']['line_id'],
        rec['html_offset']['end']['offset'],
    )

def get_dump_date(html_dir, category, page_id):
    html_path = os.path.join(html_dir, category, f'{page_id}.html')
    html = open(html_path, encoding='utf-8').read()
    soup = BeautifulSoup(html, 'lxml')
    title = soup.title.text.strip()
    try:
        if title.find('Wikipedia Dump ') >= 0:
            dump_date = title.split('Wikipedia Dump ')[1]
        else:
            dump_date = title.split('jawiki-')[1]
    except IndexError as e:
        logger.debug('title: %s', title)
        raise e
    return dump_date

def main(train_dir):
    ene_annotation_dir = os.path.join(train_dir, 'ene_annotation')
    link_annotation_dir = os.path.join(train_dir, 'link_annotation')
    html_dir = os.path.join(train_dir, 'html')

    ene_dist_paths = []
    link_dist_paths = []
    categories = []
    for entry in os.listdir(ene_annotation_dir):
        if entry.endswith('_dist.jsonl'):
            categories.append(entry.split('_dist.jsonl')[0])
            ene_dist_paths.append(os.path.join(ene_annotation_dir, entry))
            link_dist_paths.append(os.path.join(link_annotation_dir, entry))
    #logger.debug('dist_paths: %s', dist_paths)
    #logger.debug('categories: %s', categories)
    logger.info('# categories: %s', len(categories))

    #count_attributes = 0
    #count_extracted_attributes = 0
    #count_pages = 0
    count_pages_for_extraction = 0
    #count_pages_for_linking_target = 0
    #count_pages_for_linking = 0
    #count_cummulative_attribute_names = 0
    count_cummulative_attribute_names_for_extraction = 0
    #map_date_to_counts = {}
    map_date_to_counts = {}
    #attribute_names = set()
    #min_category_attribute_names = 10**10
    #max_category_attribute_names = 0
    #category_for_max_attribute_names = None
    #for i, dist_path in enumerate(dist_paths):
    map_date_to_sets = {}
    #min_page_attributes = 10**10
    #max_page_attributes = 0
    #info_for_max_page_attributes = None
    #min_attributes_per_page_and_attribute_name = 10**10
    #max_attributes_per_page_and_attribute_name = 0
    #info_for_max_attributes_per_page_and_attribute_name = None
    #count_overlapping_offsets_with_single_attribute_names = 0
    #count_overlapping_offsets_with_multiple_attribute_names = 0
    #count_same_offsets_with_multiple_attribute_names = 0
    attribute_set_for_extraction = set()
    attribute_set_for_linking = set()
    attribute_name_set_for_extraction = set()
    page_set_for_extraction = set()
    #page_set_for_linking = set()
    #count_extracted_attribute_records = 0
    count_attribute_links = 0
    #count_attributes_with_links = 0
    count_attributes_without_links = 0
    for i, ene_dist_path in enumerate(tqdm(
        ene_dist_paths,
        desc='processing categories'
    )):
        category = categories[i]
        link_dist_path = link_dist_paths[i]
        #if i >= 1:
        #if i >= 2:
        #if i >= 10:
        #    break
        map_page_id_to_date = {}
        #map_page_id_to_count_attributes = {}
        #map_page_id_to_attribute_offsets = {}
        #map_page_id_to_counts = {}
        #category_attribute_names = set()
        category_attribute_names_for_extraction = set()
        with open(ene_dist_path, encoding='utf-8') as f:
            #page_set = set()
            for j, line in enumerate(tqdm(
                f,
                desc=f'processing attributes for category: {category}',
                leave=False,
            )):
                #if j > 10:
                #    break
                #d_ene = json.loads(line)
                rec_ene = json.loads(line)
                page_id = rec_ene['page_id']
                attribute = rec_ene['attribute']
                ene = rec_ene['ENE']
                #title = rec_ene['title']
                #logger.debug('rec_ene: %s', rec_ene)
                key = get_attribute_key(rec_ene)
                if key in attribute_set_for_extraction:
                    raise ValueError(f'key: {key} is duplicated')
                attribute_set_for_extraction.add(key)
                attribute_name_set_for_extraction.add(attribute)
                page_set_for_extraction.add(page_id)
                #count_extracted_attribute_records += 1
                #sys.exit(1)
                #if page_id not in page_set:
                if page_id not in map_page_id_to_date:
                    #html_path = os.path.join(html_dir, category, f'{page_id}.html')
                    #html = open(html_path, encoding='utf-8').read()
                    #soup = BeautifulSoup(html, 'lxml')
                    #title = soup.title.text.strip()
                    #try:
                    #    if title.find('Wikipedia Dump ') >= 0:
                    #        dump_date = title.split('Wikipedia Dump ')[1]
                    #    else:
                    #        dump_date = title.split('jawiki-')[1]
                    #except IndexError as e:
                    #    logger.debug('title: %s', title)
                    #    raise e
                    dump_date = get_dump_date(html_dir, category, page_id)
                #    #logger.debug('dump_date: %s', dump_date)
                    map_page_id_to_date[page_id] = dump_date
                #    map_page_id_to_count_attributes[page_id] = 0
                #    attribute_offsets = []
                #    map_page_id_to_attribute_offsets[page_id] = attribute_offsets
                    #counts_on_page_id = {}
                    #count_on_attribute_name = {}
                    count_extracted_attributes_on_attribute_name = {}
                    #counts_on_page_id['count_on_attribute_name'] = count_on_attribute_name
                    #counts_on_page_id['count_extracted_attributes_on_attribute_name'] = \
                    #    count_extracted_attributes_on_attribute_name
                    #map_page_id_to_counts[page_id] = counts_on_page_id
                else:
                    dump_date = map_page_id_to_date[page_id]
                #    attribute_offsets = map_page_id_to_attribute_offsets[page_id]
                    #counts_on_page_id = map_page_id_to_counts[page_id]
                #    count_on_attribute_name = counts_on_page_id['count_on_attribute_name']
                    #count_extracted_attributes_on_attribute_name = \
                    #    counts_on_page_id['count_extracted_attributes_on_attribute_name']
                if dump_date in map_date_to_counts:
                    counts_on_date = map_date_to_counts[dump_date]
                    sets_on_date = map_date_to_sets[dump_date]
                else:
                    counts_on_date = {}
                    sets_on_date = {}
                    #counts_on_date['pages'] = set()
                    #counts_on_date['pages'] = 0
                    counts_on_date['pages_for_extraction'] = 0
                    counts_on_date['pages_for_linking_target'] = 0
                    #counts_on_date['attributes'] = 0
                    #counts_on_date['extracted_attributes'] = 0
                    counts_on_date['attributes_for_extraction'] = 0
                    #counts_on_date['attribute_names'] = 0
                    #counts_on_date['extracted_attribute_names'] = 0
                    counts_on_date['attribute_names_for_extraction'] = 0
                    #sets_on_date['pages'] = set()
                    sets_on_date['pages_for_extraction'] = set()
                    sets_on_date['pages_for_linking_target'] = set()
                    #sets_on_date['pages_for_linking'] = set()
                    #sets_on_date['categories'] = set()
                    sets_on_date['categories_for_extraction'] = set()
                    #sets_on_date['categories_for_linking'] = set()
                    #sets_on_date['attribute_names'] = set()
                    #sets_on_date['extracted_attribute_names'] = set()
                    sets_on_date['attribute_names_for_extraction'] = set()
                    #sets_on_date['attribute_names_for_linking'] = set()
                    map_date_to_counts[dump_date] = counts_on_date
                    map_date_to_sets[dump_date] = sets_on_date
                #if attribute not in count_on_attribute_name:
                #    count_on_attribute_name[attribute] = 0
                if attribute not in count_extracted_attributes_on_attribute_name:
                    count_extracted_attributes_on_attribute_name[attribute] = 0
                #page_set.add(page_id)
                page_set_for_extraction.add(page_id)
                #count_attributes += 1
                #sets_on_date['pages'].add(page_id)
                sets_on_date['pages_for_extraction'].add(page_id)
                #sets_on_date['categories'].add(ene)
                sets_on_date['categories_for_extraction'].add(ene)
                #sets_on_date['attribute_names'].add(attribute)
                sets_on_date['attribute_names_for_extraction'].add(attribute)
                #counts_on_date['attributes'] += 1
                counts_on_date['attributes_for_extraction'] += 1
                #counts_on_date['pages'] = len(sets_on_date['pages'])
                #counts_on_date['categories'] = len(sets_on_date['categories'])
                #counts_on_date['attribute_names'] = len(sets_on_date['attribute_names'])
                counts_on_date['pages_for_extraction'] = len(sets_on_date['pages_for_extraction'])
                counts_on_date['categories_for_extraction'] = len(sets_on_date['categories_for_extraction'])
                counts_on_date['attribute_names_for_extraction'] = len(sets_on_date['attribute_names_for_extraction'])
                #category_attribute_names.add(attribute)
                category_attribute_names_for_extraction.add(attribute)
                #attribute_names.add(attribute)
                #this_offset = rec_ene['html_offset']
                #this_offset['attribute'] = attribute
                ## NOTE: 既存のオフセットとの重複をチェック
                #for offset in attribute_offsets:
                #    if this_offset['start']['line_id'] < offset['start']['line_id']:
                #        continue
                #    if this_offset['start']['line_id'] > offset['end']['line_id']:
                #        continue
                #    if this_offset['start']['line_id'] == offset['start']['line_id']:
                #        if this_offset['start']['offset'] < offset['start']['offset']:
                #            continue
                #        if this_offset['start']['offset'] >= offset['end']['offset']:
                #            # NOTE: end-offsetはその位置を含まない
                #            continue
                #    # NOTE: 重複している
                #    if (
                #        this_offset['start']['line_id'] == offset['start']['line_id']
                #        and this_offset['start']['offset'] == offset['start']['offset']
                #        and this_offset['end']['line_id'] == offset['end']['line_id']
                #        and this_offset['end']['offset'] == offset['end']['offset']
                #    ):
                #        count_same_offsets_with_multiple_attribute_names += 1
                #    if this_offset['attribute'] == offset['attribute']:
                #        count_overlapping_offsets_with_single_attribute_names += 1
                #    else:
                #        count_overlapping_offsets_with_multiple_attribute_names += 1
                #attribute_offsets.append(this_offset)

                #map_page_id_to_count_attributes[page_id] += 1
                #if map_page_id_to_count_attributes[page_id] > max_page_attributes:
                #    max_page_attributes = map_page_id_to_count_attributes[page_id]
                #    info_for_max_page_attributes = dict(
                #        category = category,
                #        page_id = page_id,
                #        title = title,
                #    )

                #count_on_attribute_name[attribute] += 1
                #if count_on_attribute_name[attribute] > max_attributes_per_page_and_attribute_name:
                #    max_attributes_per_page_and_attribute_name = count_on_attribute_name[attribute]
                #    #info_for_max_attributes_per_page_and_attribute_name = d
                #    info_for_max_attributes_per_page_and_attribute_name = dict(
                #        category = category,
                #        page_id = page_id,
                #        title = title,
                #        attribute = attribute,
                #    )

            ##count_pages += len(page_set)
            #count_pages += len(map_page_id_to_date)
            count_pages_for_extraction += len(map_page_id_to_date)
            #count_cummulative_attribute_names += len(category_attribute_names)
            count_cummulative_attribute_names_for_extraction += \
                len(category_attribute_names_for_extraction)
            #min_category_attribute_names = min(
            #    min_category_attribute_names,
            #    len(category_attribute_names),
            #)
            ##max_category_attribute_names = max(
            ##    max_category_attribute_names,
            ##    len(category_attribute_names),
            ##)
            #if len(category_attribute_names) > max_category_attribute_names:
            #    max_category_attribute_names = len(category_attribute_names)
            #    category_for_max_attribute_names = category
            #for page_id, count in map_page_id_to_count_attributes.items():
            #    min_page_attributes = min(min_page_attributes, count)
            #    #max_page_attributes = max(max_page_attributes, count)
            #for attribute, count in count_on_attribute_name.items():
            #    min_attributes_per_page_and_attribute_name = min(
            #        min_attributes_per_page_and_attribute_name, count
            #    )
            #    #max_attributes_per_page_and_attribute_name = max(
            #    #    max_attributes_per_page_and_attribute_name, count
            #    #)
            #for page_id, counts_on_page_id in map_page_id_to_counts.items():
            #    for attribute, count in counts_on_page_id['count_on_attribute_name'].items():
            #        min_attributes_per_page_and_attribute_name = min(
            #            min_attributes_per_page_and_attribute_name, count
            #        )
            #        #max_attributes_per_page_and_attribute_name = max(
            #        #    max_attributes_per_page_and_attribute_name, count
            #        #)

        with open(link_dist_path, 'r', encoding='utf-8') as f:
            for j, line in enumerate(tqdm(
                f,
                desc=f'processing linking for category: {category}',
                leave=False,
            )):
                #if j > 10:
                #    break
                link_rec = json.loads(line)
                #logger.debug('link_rec: %s', link_rec)
                key = get_attribute_key(link_rec)
                attribute_set_for_linking.add(key)
                if key not in attribute_set_for_extraction:
                    raise ValueError(
                        f'key not found in attribute_set_for_extraction: {key}'
                    )
                link_page_id = link_rec['link_page_id']
                if link_page_id is None:
                    count_attributes_without_links += 1
                    continue
                else:
                    #count_attributes_with_links += 1
                    count_attribute_links += 1

                if link_page_id not in map_page_id_to_date: 
                    dump_date = get_dump_date(html_dir, category, page_id)
                    map_page_id_to_date[page_id] = dump_date
                else:
                    dump_date = map_page_id_to_date[page_id]
                sets_on_date = map_date_to_sets[dump_date]
                counts_on_date = map_date_to_counts[dump_date]
                sets_on_date['pages_for_linking_target'].add(link_page_id)
                counts_on_date['pages_for_linking_target'] = \
                    len(sets_on_date['pages_for_linking_target'])

    # 属性値抽出の全レコードがリンキングの対象となっていることを確認
    for key in attribute_set_for_extraction:
        if key not in attribute_set_for_linking:
            logger.warning('key not found in attribute_set_for_linking: %s', key)
            raise ValueError(
                f'key not found in attribute_set_for_linking: {key}'
            )

    logger.info('# total extracted attributes: %s', len(attribute_set_for_extraction))
    logger.info('unique attribute names for extraction: %s', len(attribute_name_set_for_extraction))
    logger.info('# total pages for extraction: %s', count_pages_for_extraction)
    logger.info(
        'cumulative attribute names for extraction: %s',
        count_cummulative_attribute_names_for_extraction
    ) 
    logger.info('-----')
    logger.info('# total attribute links: %s', count_attribute_links)
    logger.info('# total attributes without links: %s', count_attributes_without_links)
    #logger.info('# total attribute with links: %s', count_attributes_with_links)
    logger.info(
        '# total attribute with links: %s',
        len(attribute_set_for_extraction) - count_attributes_without_links
    )
    logger.info('-----')
    logger.info('map_date_to_counts: %s', map_date_to_counts)

if __name__ == '__main__':
    main(sys.argv[1])
