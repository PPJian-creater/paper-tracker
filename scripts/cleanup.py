#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清理脚本
功能：清理 papers.json 中的重复文献和超期文献
用法：python scripts/cleanup.py
"""

import json
import os
from datetime import datetime


def load_papers():
    """加载已有文献"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'papers.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存文献到文件"""
    os.makedirs('data', exist_ok=True)
    with open('data/papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)


def normalize_doi(doi):
    """规范化 DOI：去掉前缀，统一小写"""
    if not doi:
        return ''
    doi = doi.lower().strip()
    if doi.startswith('https://doi.org/'):
        doi = doi[16:]
    elif doi.startswith('http://doi.org/'):
        doi = doi[15:]
    return doi


def cleanup_papers():
    """主清理函数"""
    papers = load_papers()
    total_before = len(papers)
    today = datetime.now().date()

    print("=" * 60)
    print("数据清理脚本")
    print("=" * 60)
    print(f"清理前文献总数: {total_before}")
    print()

    # 第一步：全局 DOI 去重（保留第一条）
    seen_dois = set()
    deduped = []
    dup_count = 0

    for p in papers:
        doi = normalize_doi(p.get('doi', ''))
        if doi:
            if doi in seen_dois:
                dup_count += 1
                continue
            seen_dois.add(doi)
        # 没有 DOI 的文献直接保留（不丢弃）
        deduped.append(p)

    if dup_count > 0:
        print(f"【去重】移除重复文献: {dup_count} 篇")
    else:
        print("【去重】未发现重复文献")

    # 第二步：删除未来日期文献
    cleaned = []
    future_count = 0

    for p in deduped:
        pub_date = p.get('published_date', '')
        if pub_date:
            try:
                if datetime.strptime(pub_date, '%Y-%m-%d').date() > today:
                    future_count += 1
                    continue
            except ValueError:
                pass  # 日期格式异常，保留
        cleaned.append(p)

    if future_count > 0:
        print(f"【日期】移除未来日期文献: {future_count} 篇")
    else:
        print("【日期】未发现未来日期文献")

    total_after = len(cleaned)
    removed = total_before - total_after

    print()
    print(f"清理完成:")
    print(f"  移除总数: {removed} 篇")
    print(f"  剩余总数: {total_after} 篇")
    print()

    save_papers(cleaned)
    print("已保存清理后的数据到 data/papers.json")

    return removed, total_after


if __name__ == '__main__':
    cleanup_papers()
