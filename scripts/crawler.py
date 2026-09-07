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

# Crossref API配置（用于获取更准确的在线发表日期）
CROSSREF_HEADERS = {
    'User-Agent': f'PA-PPS Literature Tracker (mailto:{EMAIL})'
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
        {"name": "The American Review of Public Administration", "issn": "0275-0740"},
        {"name": "Canadian Public Administration", "issn": "1754-7121"},
        {"name": "Perspectives on Public Management and Governance", "issn": "2398-4929"},
        {"name": "Public Personnel Management", "issn": "1945-7421"},
        {"name": "Review of Public Personnel Administration", "issn": "1552-759X"}
    ],
    "public_policy": [
        {"name": "Behavioural Public Policy", "issn": "2398-063X"},
        {"name": "Critical Policy Studies", "issn": "1946-0171"},
        {"name": "European Policy Analysis", "issn": "2380-6567"},
        {"name": "Evidence & Policy", "issn": "1744-2656"},
        {"name": "Journal of Asian Public Policy", "issn": "1751-6234"},
        {"name": "Journal of Comparative Policy Analysis", "issn": "1387-6988"},
        {"name": "Journal of European Public Policy", "issn": "1350-1763"},
        {"name": "Journal of Policy Analysis and Management", "issn": "0276-8739"},
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
        {"name": "Social Policy & Administration", "issn": "0144-5596"},
        {"name": "Canadian Public Policy", "issn": "1911-9917"}
    ],
    "political_science": [
        {"name": "American Journal of Political Science", "issn": "0092-5853"},
        {"name": "American Political Science Review", "issn": "0003-0554"},
        {"name": "Annals of the American Academy of Political and Social Science", "issn": "1552-3349"},
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
        {"name": "International Studies Quarterly", "issn": "0020-8833"},
        {"name": "Journal of Conflict Resolution", "issn": "0022-0027"},
        {"name": "Journal of Democracy", "issn": "1045-5736"},
        {"name": "Journal Of Experimental Political Science", "issn": "2052-2649"},
        {"name": "Journal of Theoretical Politics", "issn": "0951-6298"},
        {"name": "Legislative Studies Quarterly", "issn": "0362-9805"},
        {"name": "PS: Political Science & Politics", "issn": "1049-0965"},
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
    "economics": [
        {"name": "American Economic Review", "issn": "0002-8282"},
        {"name": "Econometrica", "issn": "0012-9682"},
        {"name": "Journal of Political Economy", "issn": "0022-3808"},
        {"name": "Journal of Labor Economics", "issn": "0734-306X"},
        {"name": "Journal of Public Economics", "issn": "0047-2727"},
        {"name": "Quarterly Journal of Economics", "issn": "0033-5533"},
        {"name": "Review of Economic Studies", "issn": "0034-6527"},
        {"name": "Review of Economics and Statistics", "issn": "0034-6535"},
        {"name": "Journal of Economic Perspectives", "issn": "0895-3309"},
        {"name": "Journal of Economic Literature", "issn": "0022-0515"},
        {"name": "Journal of Development Economics", "issn": "0304-3878"},
        {"name": "Journal of the European Economic Association", "issn": "1542-4766"},
        {"name": "Journal of Comparative Economics", "issn": "0147-5967"},
        {"name": "Economic Journal", "issn": "0013-0133"},
        {"name": "Journal of Economic Geography", "issn": "1468-2702"},
        {"name": "Annual Review of Economics", "issn": "1941-1383"},
        {"name": "European Economic Review", "issn": "0014-2921"},
        {"name": "Econometric Theory", "issn": "0266-4666"},
        {"name": "Journal of Economic Theory", "issn": "0022-0531"},
        {"name": "International Economic Review", "issn": "0020-6598"}
    ],
    "china_studies": [
        {"name": "China Information", "issn": "0920-203X"},
        {"name": "China Perspectives", "issn": "2070-3449"},
        {"name": "Journal of Chinese Political Science", "issn": "1080-6954"},
        {"name": "Journal of Contemporary China", "issn": "1067-0564"},
        {"name": "Modern China", "issn": "0097-7004"},
        {"name": "The China Journal", "issn": "1324-9347"},
        {"name": "The China Quarterly", "issn": "0305-7410"},
        {"name": "China-An International Journal", "issn": "0219-7472"}
    ],
    "other": [
        {"name": "Social Networks", "issn": "0378-8733"},
        {"name": "Social Forces", "issn": "0037-7732"},
        {"name": "Journal of Risk Research", "issn": "1366-9877"},
        {"name": "Risk Analysis", "issn": "0272-4332"},
        {"name": "Journal of Risk and Uncertainty", "issn": "0895-5646"},
        {"name": "Journal of Management", "issn": "0149-2063"},
        {"name": "New Media & Society", "issn": "1461-4448"},
        {"name": "Political Communication", "issn": "1058-4609"},
        {"name": "Media, Culture & Society", "issn": "0163-4437"},
        {"name": "Journalism & Mass Communication Quarterly", "issn": "1077-6990"},
        {"name": "Journal of Communication", "issn": "0021-9916"}
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
    "Journal of democracy": "Journal of Democracy",
    "Journal of Experimental Political Science": "Journal Of Experimental Political Science",
    "Comparative Political Studies": "Comparative Political Studies",
    "Political Research Quarterly": "Political Research Quarterly",
    "British Journal of Political Science": "British Journal of Political Science",
    "Research &amp; Politics": "Research & Politics",
    "Research &amp Politics": "Research & Politics",
    "Research & Politics": "Research & Politics",
    "Political Behavior": "Political Behavior",
    "Electoral Studies": "Electoral Studies",
    "European Union Politics": "European Union Politics",
    "Political Geography": "Political Geography",
    "West European Politics": "West European Politics",
    "Political Psychology": "Political Psychology",
    "International Organization": "International Organization",
    "International Studies Quarterly": "International Studies Quarterly",
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
    "The Annals of the American Academy of Political and Social Science": "Annals of the American Academy of Political and Social Science",
    "Political Science Research and Methods": "Political Science Research and Methods",
    "Public Choice": "Public Choice",
    "Public Opinion Quarterly": "Public Opinion Quarterly",

    # 经济学 (ECON)
    "American Economic Review": "American Economic Review",
    "Econometrica": "Econometrica",
    "Journal of Political Economy": "Journal of Political Economy",
    "Journal of Labor Economics": "Journal of Labor Economics",
    "Journal of Public Economics": "Journal of Public Economics",
    "Quarterly Journal of Economics": "Quarterly Journal of Economics",
    "Review of Economic Studies": "Review of Economic Studies",
    "Review of Economics and Statistics": "Review of Economics and Statistics",
    "Journal of Economic Perspectives": "Journal of Economic Perspectives",
    "Journal of Economic Literature": "Journal of Economic Literature",
    "Journal of Development Economics": "Journal of Development Economics",
    "Journal of the European Economic Association": "Journal of the European Economic Association",
    "Journal of Comparative Economics": "Journal of Comparative Economics",
    "Economic Journal": "Economic Journal",
    "The Economic Journal": "Economic Journal",
    "Journal of Economic Geography": "Journal of Economic Geography",
    "Annual Review of Economics": "Annual Review of Economics",
    "European Economic Review": "European Economic Review",
    "Econometric Theory": "Econometric Theory",
    "Journal of Economic Theory": "Journal of Economic Theory",
    "International Economic Review": "International Economic Review",

    # 中国研究 (CHINA)
    "Journal of Contemporary China": "Journal of Contemporary China",
    "The China Quarterly": "The China Quarterly",
    "The China Journal": "The China Journal",
    "Modern China": "Modern China",
    "China Information": "China Information",
    "Journal of Chinese Political Science": "Journal of Chinese Political Science",
    "China Perspectives": "China Perspectives",
    "China-An International Journal": "China-An International Journal",
    "China: An International Journal": "China-An International Journal",

    # 其他 (OTHER)
    "Social Networks": "Social Networks",
    "Social Forces": "Social Forces",
    "Journal of Risk Research": "Journal of Risk Research",
    "Risk Analysis": "Risk Analysis",
    "Journal of Risk and Uncertainty": "Journal of Risk and Uncertainty",
    "Journal of Management": "Journal of Management",
    "New Media & Society": "New Media & Society",
    "Political Communication": "Political Communication",
    "Media, Culture & Society": "Media, Culture & Society",
    "Journalism & Mass Communication Quarterly": "Journalism & Mass Communication Quarterly",
    "Journal of Communication": "Journal of Communication",

    # 公共行政 (PA) - 新增期刊
    "Canadian Public Administration": "Canadian Public Administration",
    "Perspectives on Public Management and Governance": "Perspectives on Public Management and Governance",
    "Public Personnel Management": "Public Personnel Management",
    "Review of Public Personnel Administration": "Review of Public Personnel Administration",

    # 公共政策 (PP) - 新增期刊
    "Canadian Public Policy": "Canadian Public Policy"
}


def normalize_journal_name(name):
    """标准化期刊名称"""
    if not name:
        return name
    # 先解码 HTML 实体编码（如 &amp; → &）
    decoded_name = html.unescape(name)
    # 尝试映射（优先用解码后的名称匹配）
    if decoded_name in JOURNAL_NAME_MAPPING:
        return JOURNAL_NAME_MAPPING[decoded_name]
    # 再尝试原始名称映射（兼容旧数据）
    if name in JOURNAL_NAME_MAPPING:
        return JOURNAL_NAME_MAPPING[name]
    # 返回解码后的名称（去除 HTML 实体）
    return decoded_name


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
    'commentary',
    'correction'
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

def fetch_crossref_dates(doi):
    """
    通过 Crossref API 获取论文的 published-online 和 published-print 日期
    返回: (published_online, published_print) 元组，获取失败则返回 ('', '')
    """
    if not doi:
        return '', ''
    
    # 规范化 DOI
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
            """解析 Crossref 的 date-parts 格式"""
            if date_parts and date_parts[0]:
                year = date_parts[0][0] if len(date_parts[0]) > 0 else None
                month = date_parts[0][1] if len(date_parts[0]) > 1 else 1
                day = date_parts[0][2] if len(date_parts[0]) > 2 else 1
                if year:
                    return f"{year:04d}-{month:02d}-{day:02d}"
            return ''
        
        # 解析 online 日期
        online_parts = message.get('published-online', {}).get('date-parts', [[]])
        published_online = parse_date_parts(online_parts)
        
        # 解析 print 日期
        print_parts = message.get('published-print', {}).get('date-parts', [[]])
        published_print = parse_date_parts(print_parts)
        
        return published_online, published_print
        
    except Exception as e:
        # 静默失败，不影响主流程
        return '', ''


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

        # 过滤未来日期（期刊排期导致的卷期未来日期）
        if pub_date:
            try:
                if datetime.strptime(pub_date, '%Y-%m-%d').date() > datetime.now().date():
                    print(f"    [过滤] 跳过未来日期文献: {title[:60]}... ({pub_date})")
                    return None
            except ValueError:
                pass  # 日期格式异常，保留

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
        
        # 获取 Crossref 日期（优先使用 Crossref 的 published-online）
        crossref_online, crossref_print = fetch_crossref_dates(doi)
        
        # 确定 published_online：优先 Crossref 的 online 日期，其次 OpenAlex 的 pub_date
        published_online = crossref_online if crossref_online else pub_date
        
        # 确定 published_print：使用 Crossref 的 print 日期（如果有）
        published_print = crossref_print
        
        # 确定 published_date：优先 online 日期，其次 print 日期，兜底 pub_date
        published_date = published_online or published_print or pub_date
        
        return {
            'openalex_id': openalex_id,
            'title': title,
            'abstract': abstract,
            'journal_name': journal_name,
            'published_date': published_date,
            'published_online': published_online,
            'published_print': published_print,
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
    
    # 加载已有文献
    existing_papers = load_existing_papers()
    
    # 构建 DOI 去重集合和 DOI→索引映射（用于摘要补充）
    existing_dois = set()
    doi_to_index = {}  # doi_lower -> index in existing_papers
    for idx, p in enumerate(existing_papers):
        doi = (p.get('doi') or '').lower().strip()
        if doi.startswith('https://doi.org/'):
            doi = doi[16:]
        if doi:
            existing_dois.add(doi)
            doi_to_index[doi] = idx

    if existing_papers:
        # 找到已有数据中最新的 published_date，往前退 3 天作为缓冲
        # 过滤掉未来日期，避免被期刊排期顶到后面
        today = datetime.now().date()
        valid_dates = [
            p.get('published_date', '1970-01-01')
            for p in existing_papers
            if p.get('published_date')
        ]
        valid_dates = [
            d for d in valid_dates
            if datetime.strptime(d, '%Y-%m-%d').date() <= today
        ]
        if valid_dates:
            latest_date = max(valid_dates)
        else:
            latest_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        # 取 min(now-days, latest_date-3天)，确保 --days 参数生效
        # daily: now-2天 比 latest_date-3天 更晚 → 取 latest_date-3天（增量补爬）
        # weekly/initial: now-14/120天 更早 → 取 now-days（按指定范围爬取）
        days_based_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        buffer_based_from = (
            datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=3)
        ).strftime('%Y-%m-%d')
        from_date = min(days_based_from, buffer_based_from)
    else:
        # 首次运行或数据丢失，使用默认天数
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    to_date = datetime.now().strftime('%Y-%m-%d')

    print(f"开始爬取文献: {from_date} 至 {to_date}")
    print(f"已有 DOI 去重集合: {len(existing_dois)} 个")
    print("=" * 60)

    existing_ids = {p['openalex_id'] for p in existing_papers}
    
    total_added = 0
    journal_stats = {}
    
    # 处理所有期刊
    all_journals = (
        [(j, 'PA') for j in JOURNALS_CONFIG['public_administration']] +
        [(j, 'PP') for j in JOURNALS_CONFIG['public_policy']] +
        [(j, 'POL') for j in JOURNALS_CONFIG['political_science']] +
        [(j, 'ECON') for j in JOURNALS_CONFIG['economics']] +
        [(j, 'OTHER') for j in JOURNALS_CONFIG['other']] +
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
        updated_abstract_count = 0
        updated_keywords_count = 0
        for paper in papers:
            if paper['openalex_id'] not in existing_ids:
                # DOI 去重：规范化后检查是否已存在
                paper_doi = (paper.get('doi') or '').lower().strip()
                if paper_doi.startswith('https://doi.org/'):
                    paper_doi = paper_doi[16:]

                if paper_doi and paper_doi in existing_dois:
                    # 检查是否需要补充摘要或关键词（OpenAlex 有而旧记录无）
                    existing_idx = doi_to_index.get(paper_doi)
                    if existing_idx is not None:
                        existing = existing_papers[existing_idx]
                        updated = False

                        # 补充摘要
                        new_abstract = (paper.get('abstract') or '').strip()
                        old_abstract = (existing.get('abstract') or '').strip()
                        if new_abstract and not old_abstract:
                            existing['abstract'] = new_abstract
                            existing['openalex_id'] = paper['openalex_id']
                            existing['published_online'] = paper.get('published_online', '')
                            print(f"    [更新] 补充摘要: {paper_doi[:50]}")
                            updated_abstract_count += 1
                            updated = True

                        # 补充关键词
                        new_keywords = paper.get('keywords', []) or []
                        old_keywords = existing.get('keywords', []) or []
                        if new_keywords and not old_keywords:
                            existing['keywords'] = new_keywords
                            print(f"    [更新] 补充关键词: {paper_doi[:50]}")
                            updated_keywords_count += 1
                            updated = True

                        if not updated:
                            print(f"    [跳过] DOI 已存在: {paper_doi[:50]}")
                    continue

                paper['category'] = category
                existing_papers.append(paper)
                existing_ids.add(paper['openalex_id'])
                if paper_doi:
                    existing_dois.add(paper_doi)
                    doi_to_index[paper_doi] = len(existing_papers) - 1
                added_count += 1

        # 打印总结
        parts = []
        if added_count > 0:
            parts.append(f"新增 {added_count} 篇")
        if updated_abstract_count > 0:
            parts.append(f"补充摘要 {updated_abstract_count} 篇")
        if updated_keywords_count > 0:
            parts.append(f"补充关键词 {updated_keywords_count} 篇")
        if parts:
            print(f"  {', '.join(parts)}")
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
