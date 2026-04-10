#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSCI期刊文献爬虫 - GitHub Actions版本
"""
import requests
import json
import time
import os
import sys
from datetime import datetime, timedelta

# OpenAlex API配置
OPENALEX_BASE = "https://api.openalex.org"
EMAIL = os.environ.get('EMAIL', 'user@example.com')
HEADERS = {
    'User-Agent': 'PA-PPS Literature Tracker (GitHub Actions)',
    'Accept': 'application/json'
}

# 期刊配置
JOURNALS_CONFIG = {
    "public_administration": [
        {"name": "Administration & Society", "issn": "0095-3997"},
        {"name": "Administrative Theory & Praxis", "issn": "1084-1806"},
        {"name": "Australian Journal of Public Administration", "issn": "0313-6647"},
        {"name": "Chinese Public Administration Review", "issn": "1539-6754"},
        {"name": "Governance", "issn": "0952-1895"},
        {"name": "Government Information Quarterly", "issn": "0740-624X"},
        {"name": "International Journal of Public Administration", "issn": "0190-0692"},
        {"name": "International Public Management Journal", "issn": "1096-7494"},
        {"name": "International Review of Administrative Sciences", "issn": "0020-8523"},
        {"name": "Journal of Chinese Governance", "issn": "2381-2346"},
        {"name": "Journal of Public Administration Research and Theory", "issn": "1053-1858"},
        {"name": "Public Administration", "issn": "0033-3298"},
        {"name": "Public Administration Quarterly", "issn": "0735-8382"},
        {"name": "Public Administration Review", "issn": "0033-3352"},
        {"name": "Public Administration and Development", "issn": "0271-2075"},
        {"name": "Public Management Review", "issn": "1471-9037"},
        {"name": "Public Money & Management", "issn": "0954-0962"},
        {"name": "Public Performance & Management Review", "issn": "1530-9576"},
        {"name": "Regulation & Governance", "issn": "1748-5983"},
        {"name": "The American Review of Public Administration", "issn": "0275-0740"}
    ],
    "public_policy": [
        {"name": "Behavioural Public Policy", "issn": "2398-063X"},
        {"name": "Critical Policy Studies", "issn": "1946-0171"},
        {"name": "European Policy Analysis", "issn": "2380-6567"},
        {"name": "Journal of Asian Public Policy", "issn": "1751-6234"},
        {"name": "Journal of Comparative Policy Analysis", "issn": "1387-6988"},
        {"name": "Journal of European Public Policy", "issn": "1350-1763"},
        {"name": "Journal of Policy Analysis and Management", "issn": "0276-8739"},
        {"name": "Journal of Policy Studies", "issn": None},
        {"name": "Journal of Public Policy", "issn": "0143-814X"},
        {"name": "Journal of Social Policy", "issn": "0047-2794"},
        {"name": "Policy & Internet", "issn": "1944-2866"},
        {"name": "Policy & Politics", "issn": "0305-5736"},
        {"name": "Policy Design and Practice", "issn": "2574-1292"},
        {"name": "Policy Sciences", "issn": "0032-2687"},
        {"name": "Policy Studies", "issn": "0144-2872"},
        {"name": "Policy Studies Journal", "issn": "0190-292X"},
        {"name": "Policy and Society", "issn": "1449-4035"},
        {"name": "Politics & Policy", "issn": "1555-5623"},
        {"name": "Public Policy and Administration", "issn": "0952-0767"},
        {"name": "Research Policy", "issn": "0048-7333"},
        {"name": "Review of Policy Research", "issn": "1541-132X"},
        {"name": "Science and Public Policy", "issn": "0302-3427"},
        {"name": "Social Policy & Administration", "issn": "0144-5596"}
    ]
}


def search_journal_by_issn(issn):
    """通过ISSN搜索期刊"""
    if not issn:
        return None
    
    url = f"{OPENALEX_BASE}/sources"
    params = {'filter': f'issn:{issn}', 'mailto': EMAIL}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                return data['results'][0]
    except Exception as e:
        print(f"搜索期刊失败 ISSN {issn}: {e}")
    
    return None


def search_journal_by_name(name):
    """通过名称搜索期刊"""
    url = f"{OPENALEX_BASE}/sources"
    params = {'search': name, 'mailto': EMAIL}
    
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                for result in data['results']:
                    if name.lower() in result.get('display_name', '').lower() or \
                       result.get('display_name', '').lower() in name.lower():
                        return result
                return data['results'][0]
    except Exception as e:
        print(f"搜索期刊失败 {name}: {e}")
    
    return None


def get_journal_openalex_id(journal_info):
    """获取期刊的OpenAlex ID"""
    name = journal_info['name']
    issn = journal_info.get('issn')
    
    if issn:
        result = search_journal_by_issn(issn)
        if result:
            print(f"  [OK] 通过ISSN找到: {name}")
            return result.get('id'), result.get('display_name')
    
    result = search_journal_by_name(name)
    if result:
        print(f"  [OK] 通过名称找到: {name}")
        return result.get('id'), result.get('display_name')
    
    print(f"  [SKIP] 未找到期刊: {name}")
    return None, None


def fetch_papers_by_journal(source_id, from_date=None, to_date=None, per_page=200):
    """获取指定期刊的文献"""
    url = f"{OPENALEX_BASE}/works"
    
    filters = [f'primary_location.source.id:{source_id}']
    if from_date:
        filters.append(f'from_publication_date:{from_date}')
    if to_date:
        filters.append(f'to_publication_date:{to_date}')
    
    params = {
        'filter': ','.join(filters),
        'per-page': per_page,
        'sort': 'publication_date:desc',
        'mailto': EMAIL
    }
    
    papers = []
    cursor = None
    
    while True:
        if cursor:
            params['cursor'] = cursor
        
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=60)
            
            if response.status_code == 429:
                print("    达到速率限制，等待10秒...")
                time.sleep(10)
                continue
            
            if response.status_code != 200:
                print(f"    请求失败: {response.status_code}")
                break
            
            data = response.json()
            results = data.get('results', [])
            
            if not results:
                break
            
            for work in results:
                paper = parse_work(work)
                if paper:
                    papers.append(paper)
            
            print(f"    已获取 {len(papers)} 篇文献...")
            
            cursor = data.get('meta', {}).get('next_cursor')
            if not cursor or len(results) < per_page:
                break
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    获取文献出错: {e}")
            break
    
    return papers


def parse_work(work):
    """解析OpenAlex work对象"""
    try:
        openalex_id = work.get('id', '').replace('https://openalex.org/', '')
        title = work.get('display_name', '')
        
        # 摘要处理
        abstract_inverted = work.get('abstract_inverted_index', {})
        abstract = reconstruct_abstract(abstract_inverted) if abstract_inverted else ''
        
        # 发布日期
        pub_date = work.get('publication_date', '')
        if not pub_date:
            pub_year = work.get('publication_year', '')
            if pub_year:
                pub_date = f"{pub_year}-01-01"
        
        # 期刊信息
        primary_loc = work.get('primary_location', {}) or {}
        source = primary_loc.get('source', {}) or {}
        journal_name = source.get('display_name', '')
        
        # URL
        url = primary_loc.get('landing_page_url', '') or work.get('id', '')
        doi = work.get('doi', '')
        
        # 关键词
        keywords_list = work.get('keywords', []) or []
        keywords = [k.get('display_name', '') for k in keywords_list if k]
        
        # 作者
        authorships = work.get('authorships', []) or []
        authors = []
        for auth in authorships:
            author_info = auth.get('author', {})
            if author_info:
                authors.append(author_info.get('display_name', ''))
        
        return {
            'openalex_id': openalex_id,
            'title': title,
            'abstract': abstract,
            'journal_name': journal_name,
            'published_date': pub_date,
            'url': url,
            'doi': doi,
            'keywords': keywords,
            'authors': authors[:10]
        }
    except Exception as e:
        print(f"解析work出错: {e}")
        return None


def reconstruct_abstract(inverted_index):
    """从反转索引重建摘要文本"""
    if not inverted_index:
        return ''
    
    try:
        word_positions = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions[pos] = word
        
        sorted_words = [word_positions[i] for i in sorted(word_positions.keys())]
        return ' '.join(sorted_words)
    except:
        return ''


def load_existing_papers():
    """加载已存在的文献"""
    data_file = 'data/papers.json'
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存文献到文件"""
    os.makedirs('data', exist_ok=True)
    with open('data/papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)


def crawl_journals(days=30):
    """爬取期刊文献"""
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    print(f"开始爬取文献: {from_date} 至 {to_date}")
    print("=" * 60)
    
    # 加载已有文献
    existing_papers = load_existing_papers()
    existing_ids = {p['openalex_id'] for p in existing_papers}
    
    total_added = 0
    journal_stats = {}
    
    # 处理所有期刊
    all_journals = (
        [(j, 'PA') for j in JOURNALS_CONFIG['public_administration']] +
        [(j, 'PP') for j in JOURNALS_CONFIG['public_policy']]
    )
    
    for journal, category in all_journals:
        print(f"\n[{category}] 处理期刊: {journal['name']}")
        
        source_id, display_name = get_journal_openalex_id(journal)
        
        if not source_id:
            print(f"  跳过: 无法找到期刊ID")
            continue
        
        papers = fetch_papers_by_journal(source_id, from_date, to_date)
        
        added_count = 0
        for paper in papers:
            if paper['openalex_id'] not in existing_ids:
                paper['category'] = category
                existing_papers.append(paper)
                existing_ids.add(paper['openalex_id'])
                added_count += 1
        
        print(f"  新增 {added_count} 篇文献")
        journal_stats[journal['name']] = added_count
        total_added += added_count
        
        time.sleep(1)
    
    # 保存数据
    save_papers(existing_papers)
    
    print(f"\n{'=' * 60}")
    print(f"爬取完成! 共新增 {total_added} 篇文献")
    print(f"总计 {len(existing_papers)} 篇文献")
    
    return total_added, journal_stats


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='SSCI期刊文献爬虫')
    parser.add_argument('--days', type=int, default=2,
                       help='爬取最近多少天的文献')
    
    args = parser.parse_args()
    
    crawl_journals(days=args.days)
