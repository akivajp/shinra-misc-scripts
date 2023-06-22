#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
属性値抽出・リンキングの配布用データから該当するページIDを削除する
'''

import argparse
import csv
import json
import os
import sys

from logzero import logger
from tqdm.auto import tqdm

ACTUALLY_REMOVE = True
#ACTUALLY_REMOVE = False

def remove_page_files(
    dist_text_dir: str,
    extension: str,
    valid_page_ids: set,
    removed_page_ids: set,
):
    for filename in os.listdir(dist_text_dir):
        if not filename.endswith(extension):
            logger.error('unexpected filename: %s', filename)
            sys.exit(1)
        page_id = filename.replace(extension, '')
        if page_id in valid_page_ids:
            continue
        path = os.path.join(dist_text_dir, filename)
        if not ACTUALLY_REMOVE:
            if page_id not in removed_page_ids:
                logger.error('unexpected page_id: %s', page_id)
                sys.exit(1)
        logger.debug('removing "%s"', path)
        if ACTUALLY_REMOVE:
            os.remove(path)

def main(
    remove_target_csv_path: str,
    ene_definition_jsonl_path: str,
    dist_directory_path: str,
):
    map_ene_id_to_name = {}
    with open(ene_definition_jsonl_path, encoding='utf-8') as f:
        for line in tqdm(f, desc=f'loading "{ene_definition_jsonl_path}"'):
            d = json.loads(line)
            ene_id = d['ENE_id']
            ene_name = d['name']['en']
            map_ene_id_to_name[ene_id] = ene_name

    #set_category_and_page_id = set()
    map_category_to_removing_page_id_set = {}
    all_removing_page_id_set = set()
    duplicated_removing_page_id_set = set()
    with open(remove_target_csv_path, encoding='utf-8-sig') as f:
        #reader = csv.reader(f)
        #page_ids = [row[0] for row in reader]
        reader = csv.DictReader(f)
        for row in tqdm(reader, desc=f'loading "{remove_target_csv_path}"'):
            #logger.debug('row: %s', row)
            page_id = row['page_id']
            ene_id = row['属性値・リンキングのアノテーション']
            ene_name = map_ene_id_to_name[ene_id]
            page_id_set = map_category_to_removing_page_id_set.setdefault(ene_name, set())
            page_id_set.add(page_id)
            if page_id in all_removing_page_id_set:
                duplicated_removing_page_id_set.add(page_id)
            all_removing_page_id_set.add(page_id)
    #logger.debug('map_category_to_page_id_set: %s', map_category_to_page_id_set)

    extraction_dist_dir = os.path.join(dist_directory_path, 'annotation')
    linking_attribute_dist_dir = os.path.join(dist_directory_path, 'ene_annotation')
    linking_link_dist_dir = os.path.join(dist_directory_path, 'link_annotation')
    html_dir = os.path.join(dist_directory_path, 'html')
    plain_dir = os.path.join(dist_directory_path, 'plain')

    if os.path.isdir(extraction_dist_dir):
        #logger.info('removing "%s"', extraction_dist_dir)
        #os.system(f'rm -rf "{extraction_dist_dir}"')
        categories = []
        for filename in os.listdir(extraction_dist_dir):
            if filename.endswith('_dist.jsonl'):
                #logger.debug('filename: %s', filename)
                category = filename.replace('_dist.jsonl', '')
                categories.append(category)
        categories.sort()
        #logger.debug('categories: %s', categories)
        #for category in tqdm(categories, desc='processing dist files'):
        count_total_removed_records = 0
        count_total_valid_records = 0
        count_total_removed_page_ids = 0
        all_removed_page_id_set = set()
        all_category_page_id_pair_with_no_records = []
        for category in categories:
            #if category not in map_category_to_removing_page_id_set:
            #    continue
            #removing_page_id_set = map_category_to_removing_page_id_set[category]
            removing_page_id_set = map_category_to_removing_page_id_set.get(category, set())
            dist_path = os.path.join(extraction_dist_dir, f'{category}_dist.jsonl')
            view_path = os.path.join(extraction_dist_dir, f'{category}_dist_for_view.jsonl')
            dist_html_dir = os.path.join(html_dir, category)
            dist_plain_dir = os.path.join(plain_dir, category)
            logger.debug('dist_path: %s', dist_path)
            with open(dist_path, encoding='utf-8') as f:
                lines = f.readlines()
            logger.debug('len(lines): %s', len(lines))
            valid_page_ids = set()
            removed_page_ids = set()
            count_valid_records = 0
            count_removed_records = 0
            actual_dist_path = '/dev/null'
            actual_view_path = '/dev/null'
            if ACTUALLY_REMOVE:
                actual_dist_path = dist_path
                actual_view_path = view_path
            with (
                open(actual_dist_path, mode='w', encoding='utf-8') as f,
                open(actual_view_path, mode='w', encoding='utf-8') as f_view,
            ):
                for line in lines:
                    d = json.loads(line)
                    page_id = d['page_id']
                    if page_id in removing_page_id_set:
                        #logger.debug('removing page_id: %s', page_id)
                        removed_page_ids.add(page_id)
                        count_removed_records += 1
                        count_total_removed_records += 1
                        all_removed_page_id_set.add(page_id)
                        continue
                    valid_page_ids.add(page_id)
                    count_valid_records += 1
                    count_total_valid_records += 1
                    f.write(line)
                    f_view.write(json.dumps(json.loads(line), ensure_ascii=False, indent=4)+"\n")
            for page_id in removing_page_id_set - removed_page_ids:
                #logger.warn('page_id: %s', page_id)
                all_category_page_id_pair_with_no_records.append((category, page_id))
            remove_page_files(dist_html_dir, '.html', valid_page_ids, removed_page_ids)
            remove_page_files(dist_plain_dir, '.txt', valid_page_ids, removed_page_ids)
            logger.debug('count_valid_records: %s', count_valid_records)
            logger.debug('count_removed_records: %s', count_removed_records)
            logger.debug('len(valid_page_ids): %s', len(valid_page_ids))
            logger.debug('len(removed_page_ids): %s', len(removed_page_ids))
            count_total_removed_page_ids += len(removed_page_ids)
        logger.debug('-----')
        logger.debug('all_category_page_id_pair_with_no_records: %s', all_category_page_id_pair_with_no_records)
        logger.debug('duplicated_removing_page_id_set: %s', duplicated_removing_page_id_set)
        logger.debug('count_total_valid_records: %s', count_total_valid_records)
        logger.debug('count_total_removed_records: %s', count_total_removed_records)
        logger.debug('count_total_removed_page_ids: %s', count_total_removed_page_ids)
        logger.debug('len(all_removed_page_id_set): %s', len(all_removed_page_id_set))
    if all([
        os.path.isdir(linking_attribute_dist_dir),
        os.path.isdir(linking_link_dist_dir),
    ]):
        categories = []
        for filename in os.listdir(linking_attribute_dist_dir):
            if filename.endswith('_dist.jsonl'):
                category = filename.replace('_dist.jsonl', '')
                categories.append(category)
        categories.sort()
        count_total_removed_attribute_records = 0
        count_total_removed_link_records = 0
        count_total_valid_attribute_records = 0
        count_total_valid_link_records = 0
        count_total_removed_attribute_page_ids = 0
        count_total_removed_link_page_ids = 0
        #all_removed_page_id_set = set()
        #all_category_page_id_pair_with_no_records = []
        for category in categories:
            #if category not in map_category_to_removing_page_id_set:
            #    continue
            #removing_page_id_set = map_category_to_removing_page_id_set[category]
            removing_page_id_set = map_category_to_removing_page_id_set.get(category, set())
            attribute_dist_path = os.path.join(linking_attribute_dist_dir, f'{category}_dist.jsonl')
            link_dist_path = os.path.join(linking_link_dist_dir, f'{category}_dist.jsonl')
            attribute_view_path = os.path.join(linking_attribute_dist_dir, f'{category}_dist_for_view.jsonl')
            link_view_path = os.path.join(linking_link_dist_dir, f'{category}_dist_for_view.jsonl')
            dist_html_dir = os.path.join(html_dir, category)
            dist_plain_dir = os.path.join(plain_dir, category)
            logger.debug('attribute_dist_path: %s', attribute_dist_path)
            valid_attribute_page_ids = set()
            valid_link_page_ids = set()
            removed_attribute_page_ids = set()
            removed_link_page_ids = set()
            count_valid_attribute_records = 0
            count_valid_link_records = 0
            count_removed_attribute_records = 0
            count_removed_link_records = 0
            actual_dist_path = '/dev/null'
            actual_view_path = '/dev/null'
            if ACTUALLY_REMOVE:
                actual_dist_path = attribute_dist_path
                actual_view_path = attribute_view_path
            with open(attribute_dist_path, encoding='utf-8') as f:
                lines = f.readlines()
            logger.debug('len(lines): %s', len(lines))
            with (
                open(actual_dist_path, mode='w', encoding='utf-8') as f,
                open(actual_view_path, mode='w', encoding='utf-8') as f_view,
            ):
                for line in lines:
                    d = json.loads(line)
                    page_id = d['page_id']
                    if page_id in removing_page_id_set:
                        removed_attribute_page_ids.add(page_id)
                        count_removed_attribute_records += 1
                        count_total_removed_attribute_records += 1
                        continue
                    valid_attribute_page_ids.add(page_id)
                    count_valid_attribute_records += 1
                    count_total_valid_attribute_records += 1
                    f.write(line)
                    f_view.write(json.dumps(json.loads(line), ensure_ascii=False, indent=4)+"\n")
            if ACTUALLY_REMOVE:
                actual_dist_path = link_dist_path
                actual_view_path = link_view_path
            logger.debug('link_dist_path: %s', link_dist_path)
            with open(link_dist_path, encoding='utf-8') as f:
                lines = f.readlines()
            logger.debug('len(lines): %s', len(lines))
            with (
                open(actual_dist_path, mode='w', encoding='utf-8') as f,
                open(actual_view_path, mode='w', encoding='utf-8') as f_view,
            ):
                for line in lines:
                    d = json.loads(line)
                    page_id = d['page_id']
                    if page_id in removing_page_id_set:
                        removed_link_page_ids.add(page_id)
                        count_removed_link_records += 1
                        count_total_removed_link_records += 1
                        continue
                    valid_link_page_ids.add(page_id)
                    count_valid_link_records += 1
                    count_total_valid_link_records += 1
                    f.write(line)
                    f_view.write(json.dumps(json.loads(line), ensure_ascii=False, indent=4)+"\n")
            remove_page_files(dist_html_dir, '.html', valid_link_page_ids, removed_link_page_ids)
            remove_page_files(dist_plain_dir, '.txt', valid_link_page_ids, removed_link_page_ids)
            logger.debug('count_valid_attribute_records: %s', count_valid_attribute_records)
            logger.debug('count_valid_link_records: %s', count_valid_link_records)
            logger.debug('count_removed_attribute_records: %s', count_removed_attribute_records)
            logger.debug('count_removed_link_records: %s', count_removed_link_records)
            logger.debug('len(valid_attribute_page_ids): %s', len(valid_attribute_page_ids))
            logger.debug('len(valid_link_page_ids): %s', len(valid_link_page_ids))
            logger.debug('len(removed_attribute_page_ids): %s', len(removed_attribute_page_ids))
            logger.debug('len(removed_link_page_ids): %s', len(removed_link_page_ids))
            count_total_removed_attribute_page_ids += len(removed_attribute_page_ids)
            count_total_removed_link_page_ids += len(removed_link_page_ids)
        logger.debug('-----')
        logger.debug('count_total_valid_attribute_records: %s', count_total_valid_attribute_records)
        logger.debug('count_total_valid_link_records: %s', count_total_valid_link_records)
        logger.debug('count_total_removed_attribute_records: %s', count_total_removed_attribute_records)
        logger.debug('count_total_removed_link_records: %s', count_total_removed_link_records)
        logger.debug('count_total_removed_attribute_page_ids: %s', count_total_removed_attribute_page_ids)
        logger.debug('count_total_removed_link_page_ids: %s', count_total_removed_link_page_ids)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--remove-target-csv-path', '-R', type=str, required=True)
    parser.add_argument('--ene-definition-jsonl-path', '-E', type=str, required=True)
    parser.add_argument('--dist-directory-path', '-D', type=str, required=True)
    args = parser.parse_args()
    logger.debug('args: %s', args)
    main(
        remove_target_csv_path=args.remove_target_csv_path,
        ene_definition_jsonl_path=args.ene_definition_jsonl_path,
        dist_directory_path=args.dist_directory_path,
    )
