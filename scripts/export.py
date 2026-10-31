#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据为前端可用格式
"""
import json
import os
from datetime import datetime
from collections import Counter

FIRST_SEEN_FILE = 'data/first_seen.json'


def load_papers():
    """加载文献数据"""
    with open('data/papers.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def normalize_doi(doi):
    """规范化 DOI：去协议前缀、转小写、去空白"""
    d = (doi or '').strip().lower()
    if d.startswith('https://doi.org/'):
        d = d[16:]
    elif d.startswith('http://doi.org/'):
        d = d[15:]
    elif d.startswith('doi:'):
        d = d[4:]
    return d.strip()


def make_paper_key(paper):
    """稳定主键：DOI -> OpenAlex ID -> 标题|期刊。与前端 msPaperKey 规则一致"""
    doi = normalize_doi(paper.get('doi'))
    if doi:
        return 'doi:' + doi
    oaid = (paper.get('openalex_id') or '').strip()
    if oaid:
        return 'oa:' + oaid
    title = (paper.get('title') or '').strip().lower()
    journal = (paper.get('journal_name') or '').strip().lower()
    return 't:' + title + '|' + journal


def apply_first_seen(papers):
    """给每篇论文补 paper_key 与 first_seen（首次进入数据库的日期）。

    账本 data/first_seen.json 随仓库提交，键为 paper_key。
    首次运行（账本不存在）用 published_date 回填存量，避免全部记成今天；
    之后新增的论文一律记今天。
    """
    registry = {}
    seeded = os.path.exists(FIRST_SEEN_FILE)
    if seeded:
        try:
            with open(FIRST_SEEN_FILE, 'r', encoding='utf-8') as f:
                registry = json.load(f) or {}
        except Exception as e:
            print(f"警告: first_seen 账本读取失败，按首次运行处理 ({e})")
            registry = {}
            seeded = False

    today = datetime.now().strftime('%Y-%m-%d')
    added = 0
    for p in papers:
        key = make_paper_key(p)
        p['paper_key'] = key
        fs = p.get('first_seen') or registry.get(key)
        if not fs:
            fs = today if seeded else (p.get('published_date') or today)
            added += 1
        p['first_seen'] = fs
        registry[key] = fs

    try:
        with open(FIRST_SEEN_FILE, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=0, sort_keys=True)
    except Exception as e:
        print(f"警告: first_seen 账本写入失败 ({e})")

    print(f"入库日期: 新增 {added} 条，账本共 {len(registry)} 条")
    return registry



def export_data():
    """导出数据"""
    papers = load_papers()

    # 最终兜底：过滤掉未来日期文献（防止数据层偶发问题影响页面展示）
    today = datetime.now().date()
    original_count = len(papers)
    papers = [
        p for p in papers
        if not p.get('published_date') or
        datetime.strptime(p['published_date'], '%Y-%m-%d').date() <= today
    ]
    filtered_count = original_count - len(papers)
    if filtered_count > 0:
        print(f"导出过滤: 跳过 {filtered_count} 篇未来日期文献")

    # 加载国内期刊数据（独立存储）
    cn_papers = []
    cn_file = 'data/cn_papers.json'
    if os.path.exists(cn_file):
        with open(cn_file, 'r', encoding='utf-8') as f:
            cn_papers = json.load(f)
        # 国内期刊论文默认标记为大陆作者
        for p in cn_papers:
            p['has_mainland_author'] = True

    # 合并所有文献用于导出
    all_papers = papers + cn_papers

    # 补写稳定主键与入库日期（首次运行用 published_date 回填存量）
    apply_first_seen(all_papers)

    # 统计信息
    stats = {
        'total': len(all_papers),
        'pa_count': sum(1 for p in papers if p.get('category') == 'PA'),
        'pp_count': sum(1 for p in papers if p.get('category') == 'PP'),
        'pol_count': sum(1 for p in papers if p.get('category') == 'POL'),
        'econ_count': sum(1 for p in papers if p.get('category') == 'ECON'),
        'other_count': sum(1 for p in papers if p.get('category') == 'OTHER'),
        'utd_count': sum(1 for p in papers if p.get('category') == 'UTD'),
        'china_count': sum(1 for p in papers if p.get('category') == 'CHINA'),
        'cn_count': sum(1 for p in cn_papers if p.get('category') == 'CN'),
        'mainland_author_count': sum(1 for p in all_papers if p.get('has_mainland_author') is True),
        'journals': len(set(p['journal_name'] for p in all_papers)),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 按期刊统计
    journal_stats = Counter(p['journal_name'] for p in all_papers)
    stats['by_journal'] = [
        {'name': name, 'count': count}
        for name, count in journal_stats.most_common()
    ]

    # 近30天趋势
    last_30_days = {}
    today = datetime.now()
    for i in range(30):
        d = (today - __import__('datetime').timedelta(days=i)).strftime('%Y-%m-%d')
        last_30_days[d] = 0

    for p in all_papers:
        date = p.get('published_date', '')
        if date in last_30_days:
            last_30_days[date] += 1

    stats['trend'] = [
        {'date': d, 'count': c}
        for d, c in sorted(last_30_days.items())
    ]

    # 今日更新
    today_str = today.strftime('%Y-%m-%d')
    stats['today'] = sum(1 for p in all_papers if p.get('published_date') == today_str)

    # 导出主数据文件（合并后的全部文献）
    output = {
        'papers': all_papers,
        'stats': stats,
        'export_time': datetime.now().isoformat()
    }

    with open('data/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"导出完成: {len(all_papers)} 篇文献")
    print(f"  PA: {stats['pa_count']}, PP: {stats['pp_count']}, POL: {stats['pol_count']}, ECON: {stats['econ_count']}, OTHER: {stats['other_count']}, CHINA: {stats['china_count']}, CN: {stats['cn_count']}")
    print(f"  今日新增: {stats['today']}")
    
    return output


if __name__ == '__main__':
    if not os.path.exists('data/papers.json'):
        print("警告: data/papers.json 不存在，创建空数据")
        os.makedirs('data', exist_ok=True)
        with open('data/papers.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    export_data()
