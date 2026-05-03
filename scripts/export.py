#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据为前端可用格式
"""
import json
import os
from datetime import datetime
from collections import Counter


def load_papers():
    """加载文献数据"""
    with open('data/papers.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def export_data():
    """导出数据"""
    papers = load_papers()
    
    # 统计信息
    stats = {
        'total': len(papers),
        'pa_count': sum(1 for p in papers if p.get('category') == 'PA'),
        'pp_count': sum(1 for p in papers if p.get('category') == 'PP'),
        'pol_count': sum(1 for p in papers if p.get('category') == 'POL'),
        'china_count': sum(1 for p in papers if p.get('category') == 'CHINA'),
        'journals': len(set(p['journal_name'] for p in papers)),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 按期刊统计
    journal_stats = Counter(p['journal_name'] for p in papers)
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
    
    for p in papers:
        date = p.get('published_date', '')
        if date in last_30_days:
            last_30_days[date] += 1
    
    stats['trend'] = [
        {'date': d, 'count': c}
        for d, c in sorted(last_30_days.items())
    ]
    
    # 今日更新
    today_str = today.strftime('%Y-%m-%d')
    stats['today'] = sum(1 for p in papers if p.get('published_date') == today_str)
    
    # 导出主数据文件
    output = {
        'papers': papers,
        'stats': stats,
        'export_time': datetime.now().isoformat()
    }
    
    with open('data/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"导出完成: {len(papers)} 篇文献")
    print(f"  PA: {stats['pa_count']}, PP: {stats['pp_count']}, POL: {stats['pol_count']}, CHINA: {stats['china_count']}")
    print(f"  今日新增: {stats['today']}")
    
    return output


if __name__ == '__main__':
    if not os.path.exists('data/papers.json'):
        print("警告: data/papers.json 不存在，创建空数据")
        os.makedirs('data', exist_ok=True)
        with open('data/papers.json', 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    export_data()
