#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存量数据日期更新脚本
功能：为已有论文补充 Crossref 的 published-online 和 published-print 日期
用法：python scripts/update_dates.py
"""

import requests
import json
import os
import time
from datetime import datetime

# Crossref 请求头
EMAIL = os.environ.get('EMAIL', 'user@example.com')
CROSSREF_HEADERS = {
    'User-Agent': f'PA-PPS Literature Tracker (mailto:{EMAIL})'
}


def load_papers():
    """加载已有论文"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'papers.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存论文"""
    os.makedirs('data', exist_ok=True)
    with open('data/papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)


def fetch_crossref_dates(doi):
    """
    通过 Crossref API 获取论文日期
    返回: (published_online, published_print)
    """
    if not doi:
        return '', ''

    doi_clean = doi.lower().strip()
    if doi_clean.startswith('https://doi.org/'):
        doi_clean = doi_clean[16:]
    elif doi_clean.startswith('http://doi.org/'):
        doi_clean = doi_clean[15:]

    url = f"https://api.crossref.org/works/{doi_clean}"

    try:
        response = requests.get(url, headers=CROSSREF_HEADERS, timeout=15)
        if response.status_code != 200:
            return '', ''

        data = response.json()
        message = data.get('message', {})

        def parse_date_parts(date_parts):
            if date_parts and date_parts[0]:
                year = date_parts[0][0] if len(date_parts[0]) > 0 else None
                month = date_parts[0][1] if len(date_parts[0]) > 1 else 1
                day = date_parts[0][2] if len(date_parts[0]) > 2 else 1
                if year:
                    return f"{year:04d}-{month:02d}-{day:02d}"
            return ''

        online_parts = message.get('published-online', {}).get('date-parts', [[]])
        published_online = parse_date_parts(online_parts)

        print_parts = message.get('published-print', {}).get('date-parts', [[]])
        published_print = parse_date_parts(print_parts)

        return published_online, published_print

    except Exception as e:
        print(f"    查询失败: {e}")
        return '', ''


def update_existing_dates():
    """更新已有论文的日期字段"""
    papers = load_papers()
    total = len(papers)

    print("=" * 60)
    print("存量数据日期更新脚本")
    print("=" * 60)
    print(f"共有 {total} 篇论文需要检查")
    print()

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for i, paper in enumerate(papers):
        doi = paper.get('doi', '')
        title = paper.get('title', '')[:50]

        if not doi:
            skipped_count += 1
            continue

        # 检查是否已经有 Crossref 日期
        current_online = paper.get('published_online', '')
        current_print = paper.get('published_print', '')

        # 如果已经有 published_print，说明可能是 Crossref 补充的数据，跳过
        if current_print:
            skipped_count += 1
            continue

        print(f"[{i+1}/{total}] {title}...")

        # 查询 Crossref
        crossref_online, crossref_print = fetch_crossref_dates(doi)

        if crossref_online or crossref_print:
            # 更新日期字段
            old_online = paper.get('published_online', '')
            paper['published_online'] = crossref_online or old_online
            paper['published_print'] = crossref_print

            # 更新 published_date（优先 online，其次 print，兜底保留原值）
            paper['published_date'] = crossref_online or crossref_print or paper.get('published_date', '')

            updated_count += 1
            print(f"    更新: online={crossref_online}, print={crossref_print}")
        else:
            error_count += 1
            print(f"    未获取到 Crossref 日期")

        #  polite pool 速率限制：每秒最多 1 个请求
        time.sleep(1)

    print()
    print(f"更新完成:")
    print(f"  已更新: {updated_count} 篇")
    print(f"  跳过: {skipped_count} 篇")
    print(f"  失败: {error_count} 篇")
    print()

    save_papers(papers)
    print("已保存更新后的数据到 data/papers.json")

    return updated_count


if __name__ == '__main__':
    update_existing_dates()
