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
import html
import re
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
        {"name": "Journal of Policy Studies", "issn": "2799-9130"},
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
    ],
    "political_science": [
        {"name": "American Journal of Political Science", "issn": "0092-5853"},
        {"name": "American Political Science Review", "issn": "0003-0554"},
        {"name": "Annual Review of Political Science", "issn": "1094-2939"},
        {"name": "British Journal of Political Science", "issn": "0007-1234"},
        {"name": "Comparative Political Studies", "issn": "0010-4140"},
        {"name": "Comparative Politics", "issn": "0010-4159"},
        {"name": "Democratization", "issn": "1351-0347"},
        {"name": "Electoral Studies", "issn": "0261-3794"},
        {"name": "European Journal of Political Research", "issn": "0304-4130"},
        {"name": "European Political Science Review", "issn": "1755-7739"},
        {"name": "European Union Politics", "issn": "1465-1165"},
        {"name": "International Organization", "issn": "0020-8183"},
        {"name": "International Security", "issn": "0162-2889"},
        {"name": "International Studies Quarterly", "issn": "0020-8833"},
        {"name": "Journal of Conflict Resolution", "issn": "0022-0027"},
        {"name": "Journal of Democracy", "issn": "1045-5736"},
        {"name": "Journal of Theoretical Politics", "issn": "0951-6298"},
        {"name": "Legislative Studies Quarterly", "issn": "0362-9805"},
        {"name": "PS: Political Science & Politics", "issn": "1049-0965"},
        {"name": "Party Politics", "issn": "1354-0688"},
        {"name": "Perspectives on Politics", "issn": "1537-5927"},
        {"name": "Philosophy & Public Affairs", "issn": "0048-3915"},
        {"name": "Political Analysis", "issn": "1047-1987"},
        {"name": "Political Behavior", "issn": "0190-9320"},
        {"name": "Political Geography", "issn": "0962-6298"},
        {"name": "Political Psychology", "issn": "0162-895X"},
        {"name": "Political Research Quarterly", "issn": "1065-9129"},
        {"name": "Political Science Research and Methods", "issn": "2049-8470"},
        {"name": "Political Theory", "issn": "0090-5917"},
        {"name": "Politics & Gender", "issn": "1743-923X"},
        {"name": "Public Choice", "issn": "0048-5829"},
        {"name": "Public Opinion Quarterly", "issn": "0033-362X"},
        {"name": "Research & Politics", "issn": "2053-1680"},
        {"name": "Scandinavian Political Studies", "issn": "0080-6757"},
        {"name": "The Journal of Politics", "issn": "0022-3816"},
        {"name": "West European Politics", "issn": "0140-2382"}
    ],
    "china_studies": [
        {"name": "China Information", "issn": "0920-203X"},
        {"name": "China Perspectives", "issn": "2070-3449"},
        {"name": "Journal of Chinese Political Science", "issn": "1080-6954"},
        {"name": "Journal of Contemporary China", "issn": "1067-0564"},
        {"name": "Modern China", "issn": "0097-7004"},
        {"name": "The China Journal", "issn": "1324-9347"},
        {"name": "The China Quarterly", "issn": "0305-7410"}
    ]
}

# 期刊名称标准化映射（OpenAlex返回名称 → 配置标准名称）
JOURNAL_NAME_MAPPING = {
    # 公共行政 (PA)
    "Journal of Public Administration Research and Theory": "Journal of Public Administration Research and Theory",
    
    # 公共政策 (PP) - 名称变体映射
    "Journal of Comparative Policy Analysis Research and Practice": "Journal of Comparative Policy Analysis",
    "Journal of Comparative Policy Analysis: Research and Practice": "Journal of Comparative Policy Analysis",
    "Politics &amp; Policy": "Politics & Policy",
    "Politics &amp Policy": "Politics & Policy",
    "Social Policy and Administration": "Social Policy & Administration",
    "Policy and Society": "Policy and Society",
    "Policy &amp; Internet": "Policy & Internet",
    "Policy &amp Internet": "Policy & Internet",
    "Policy &amp; Politics": "Policy & Politics",
    "Policy &amp Politics": "Policy & Politics",
    "Journal of Policy Analysis &amp; Management": "Journal of Policy Analysis and Management",
    "Public Policy &amp; Administration": "Public Policy and Administration",
    
    # 政治学 (POL) - 名称变体映射
    "PS: Political Science &amp; Politics": "PS: Political Science & Politics",
    "PS Political Science &amp; Politics": "PS: Political Science & Politics",
    "PS Political Science & Politics": "PS: Political Science & Politics",
    "Politics &amp; Gender": "Politics & Gender",
    "Politics &amp Gender": "Politics & Gender",
    "Journal of Theoretical Politics": "Journal of Theoretical Politics",
    "Philosophy &amp; Public Affairs": "Philosophy & Public Affairs",
    "Philosophy &amp Public Affairs": "Philosophy & Public Affairs",
    "Political Science Research &amp; Methods": "Political Science Research and Methods",
    "Political Science Research &amp Methods": "Political Science Research and Methods",
    "American Political Science Review": "American Political Science Review",
    "American Journal of Political Science": "American Journal of Political Science",
    "The Journal of Politics": "The Journal of Politics",
    "Journal of Conflict Resolution": "Journal of Conflict Resolution",
    "Journal of Democracy": "Journal of Democracy",
    "Comparative Political Studies": "Comparative Political Studies",
    "Political Research Quarterly": "Political Research Quarterly",
    "British Journal of Political Science": "British Journal of Political Science",
    "Research &amp; Politics": "Research & Politics",
    "Research &amp Politics": "Research & Politics",
    "Research & Politics": "Research & Politics",
    "Political Behavior": "Political Behavior",
    "Electoral Studies": "Electoral Studies",
    "European Union Politics": "European Union Politics",
    "Party Politics": "Party Politics",
    "Political Geography": "Political Geography",
    "West European Politics": "West European Politics",
    "Political Psychology": "Political Psychology",
    "International Organization": "International Organization",
    "International Studies Quarterly": "International Studies Quarterly",
    "International Security": "International Security",
    "Perspectives on Politics": "Perspectives on Politics",
    "European Journal of Political Research": "European Journal of Political Research",
    "Annual Review of Political Science": "Annual Review of Political Science",
    "Political Theory": "Political Theory",
    "Comparative Politics": "Comparative Politics",
    "Legislative Studies Quarterly": "Legislative Studies Quarterly",
    "Political Analysis": "Political Analysis",
    "European Political Science Review": "European Political Science Review",
    "Scandinavian Political Studies": "Scandinavian Political Studies",
    "Democratization": "Democratization",
    "Political Science Research and Methods": "Political Science Research and Methods",
    "Public Choice": "Public Choice",
    "Public Opinion Quarterly": "Public Opinion Quarterly",
    
    # 中国研究 (CHINA)
    "Journal of Contemporary China": "Journal of Contemporary China",
    "The China Quarterly": "The China Quarterly",
    "The China Journal": "The China Journal",
    "Modern China": "Modern China",
    "China Information": "China Information",
    "Journal of Chinese Political Science": "Journal of Chinese Political Science",
    "China Perspectives": "China Perspectives"
}


def normalize_journal_name(name):
    """标准化期刊名称"""
    if not name:
        return name
    # 先尝试直接映射
    if name in JOURNAL_NAME_MAPPING:
        return JOURNAL_NAME_MAPPING[name]
    # 处理 HTML 实体编码（如 &amp;）
    decoded_name = html.unescape(name)
    if decoded_name in JOURNAL_NAME_MAPPING:
        return JOURNAL_NAME_MAPPING[decoded_name]
    return name


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
                else:
                    skipped = work.get('display_name', '未知标题')
                    print(f"    [过滤] 跳过非学术文章: {skipped[:60]}...")
            
            print(f"    已获取 {len(papers)} 篇文献...")
            
            cursor = data.get('meta', {}).get('next_cursor')
            if not cursor or len(results) < per_page:
                break
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    获取文献出错: {e}")
            break
    
    return papers


# 非学术文章标题过滤关键词（不区分大小写，包含匹配）
NON_ACADEMIC_TITLE_PATTERNS = [
    'celebrating', 'anniversary', 'in memoriam', 'editorial:', 'preface:',
    'introduction to the issue', 'issue information', 'cover image',
    'table of contents', 'front matter', 'back matter', 'corrigendum',
    'erratum', 'retraction', 'retraction note', 'withdrawn',
    'book review', 'review essay', 'commentary:',
    'letter to the editor', 'call for papers',
    'conference report', 'meeting report', 'proceedings',
    'about this journal', 'about the authors',
    'dedication', 'tribute to', 'obituary',
    'list of reviewers', 'thank you to reviewers'
]

# 非学术文章标题（精确匹配，不区分大小写）
NON_ACADEMIC_TITLE_EXACT = [
    'reviewers',
    'acknowledgment',
    'acknowledgments',
    'preface',
    'editorial',
    'commentary'
]

def is_non_academic_title(title):
    """检查标题是否为非学术文章"""
    if not title:
        return True
    title_lower = title.lower().strip()
    # 精确匹配
    if title_lower in NON_ACADEMIC_TITLE_EXACT:
        return True
    # 包含匹配
    for pattern in NON_ACADEMIC_TITLE_PATTERNS:
        if pattern in title_lower:
            return True
    return False


def clean_text(text):
    """清理文本中的HTML标签"""
    if not text:
        return ''
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)
    # 清理多余空格
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_work(work):
    """解析OpenAlex work对象"""
    try:
        openalex_id = work.get('id', '').replace('https://openalex.org/', '')
        title = work.get('display_name', '')
        
        # 清理标题中的HTML标签
        title = clean_text(title)
        
        # 过滤非学术文章
        if is_non_academic_title(title):
            return None
        
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
        raw_journal_name = source.get('display_name', '')
        # 标准化期刊名称
        journal_name = normalize_journal_name(raw_journal_name)
        
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
    # 使用绝对路径，确保在任何工作目录下都能找到文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'papers.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存文献到文件"""
    # 重新标准化所有文献的期刊名称（处理增量更新的旧数据）
    for paper in papers:
        if 'journal_name' in paper:
            paper['journal_name'] = normalize_journal_name(paper['journal_name'])
    
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
        [(j, 'PP') for j in JOURNALS_CONFIG['public_policy']] +
        [(j, 'POL') for j in JOURNALS_CONFIG['political_science']] +
        [(j, 'CHINA') for j in JOURNALS_CONFIG['china_studies']]
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
