#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
カテゴリ分類用TSVファイルをJSON Lines形式に変換する
'''

import sys
#import csv
import json

import argparse

# 標準のCSVライブラリは極端に長い行をエラーも警告も無く読み飛ばすエラーがあるっぽい

from logzero import logger

def main(input_path, tag, definition_jsonl_path, add_category_names):

    mapJapaneseName2Definition = {}
    with open(definition_jsonl_path) as f:
        for line in f:
            definition = json.loads(line)
            #logger.debug('definition: %s', definition)
            name = definition['name']
            mapJapaneseName2Definition[name['ja']] = definition

    with open(input_path) as f:
        # ヘッダを読み飛ばす
        # ファイル毎にカラム名に統一性が無く、そもそも名前の無いカラムなどもあったため
        f.readline()

        for i, line in enumerate(f):
            #if i > 20:
            #    break
            #logger.debug('row: %s', row)
            row = line.strip().split('\t')
            pageid = row[0]
            title = row[1]
            enes_ja = row[2].split(':')
            output = {}
            output['page_id'] = str(pageid)
            output['title'] = title
            #enes = [{'prob': 1.0, 'ENE': ene} for ene in enes]
            #output['ENEs'] = {tag: dist}
            #output['ENEs'] = {tag: enes}
            eneProbs = []
            for ene_ja in enes_ja:
                if ene_ja == '':
                    # 時々 : で終わるなどして空文字列が入ってしまっている場合がある
                    continue
                try:
                    definition = mapJapaneseName2Definition[ene_ja]
                except KeyError as e:
                    logger.error('i: %s', i)
                    logger.error('ENE not found: "%s"', ene_ja)
                    logger.error('line: %s', line)
                    raise e
                eneProb = {
                    'prob': 1.0,
                    'ENE': definition['ENE_id'],
                }
                if add_category_names:
                    eneProb['ENE_en'] = definition['name']['en']
                    eneProb['ENE_ja'] = ene_ja
                eneProbs.append(eneProb)
            if len(eneProbs) == 0:
                logger.error('i: %s', i)
                logger.error('line: %s', line)
                raise Exception('No ENEs found')
            output['ENEs'] = {tag: eneProbs}
            print(json.dumps(output, ensure_ascii=False))
            #break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert classification tsv to jsonl'
    )
    parser.add_argument(
        '--definition-jsonl', '-d', type=str, required=True,
        help='ENE definition jsonl path',
    )
    parser.add_argument(
        '--tag', type=str, required=True,
        help='Tag name',
    )
    parser.add_argument(
        '--input', '-i', type=str, required=True,
        help='Input tsv path',
    )
    parser.add_argument(
        '--add-category-names', action='store_true',
        help='Add English and Japanese category names',
    )
    args = parser.parse_args()
    main(args.input, args.tag, args.definition_jsonl, args.add_category_names)
