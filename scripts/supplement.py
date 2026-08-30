#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crossref + Semantic Scholar 补爬脚本（独立脚本，不修改原有爬虫）
功能：通过 Crossref 按 ISSN 发现 OpenAlex 漏爬的文献，
      再通过 Semantic Scholar 补全摘要等信息，合并写入 papers.json
用法：python scripts/supplement.py
"""

import requests
import json
import time
import os
import sys
import re
from datetime import datetime, timedelta

# ── 非学术文章过滤规则（与 crawler.py 保持一致）─────────────────────────

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
    """检查标题是否为非学术文章（与 crawler.py 一致）"""
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
    """清理文本中的HTML标签（与 crawler.py 一致）"""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_mainland_china_text(text):
    """判断 affiliation 文本是否指向中国大陆机构（排除港澳台）"""
    if not text:
        return False
    t = text.lower()
    # 排除港澳台
    exclude_keywords = ['hong kong', 'macau', 'macao', 'taiwan', 'taipei']
    for kw in exclude_keywords:
        if kw in t:
            return False
    # 第 1 层：含 "china" 关键词
    if 'china' in t:
        return True
    # 第 2 层：ROR 中国大陆机构数据库匹配
    return _match_ror_cn(t)


# ── ROR 中国大陆机构数据库 ────────────────────────────────────────────────────
_ror_cn_names = None  # 懒加载，首次使用时从 ror_cn.json 加载


def _load_ror_cn():
    """加载 ROR 中国大陆机构名称列表（含主名和别名）"""
    import os as _os
    global _ror_cn_names
    if _ror_cn_names is not None:
        return
    script_dir = _os.path.dirname(_os.path.abspath(__file__))
    ror_path = _os.path.join(script_dir, '..', 'data', 'ror_cn.json')
    if not _os.path.exists(ror_path):
        _ror_cn_names = set()
        return
    with open(ror_path, 'r', encoding='utf-8') as f:
        records = json.load(f)
    names = set()
    for r in records:
        for name_field in r.get('names', []):
            name = name_field.lower().strip()
            # 过滤太短的名称（易产生误判，如 "ZJU", "CTGU" 等 3-4 字符缩写）
            if len(name) >= 5:
                names.add(name)
    _ror_cn_names = names


def _match_ror_cn(text_lower):
    """检查文本是否匹配 ROR 中的中国大陆机构名称"""
    _load_ror_cn()
    if not _ror_cn_names:
        return False
    # 子串匹配：如果任何 ROR CN 机构名称出现在文本中
    for name in _ror_cn_names:
        if name in text_lower:
            return True
    return False


# ── 配置 ─────────────────────────────────────────────────────────────────────

# Semantic Scholar API Key（可选，不填则用未注册限额：100次/5分钟）
S2_API_KEY = os.environ.get('S2_API_KEY', '')

# Crossref 请求头（填写你的邮箱可使用 polite pool，速率更高）
CROSSREF_EMAIL = os.environ.get('EMAIL', 'user@example.com')
CROSSREF_HEADERS = {
    'User-Agent': f'LiteratureTracker/1.0 (mailto:{CROSSREF_EMAIL})'
}

S2_HEADERS = {
    'User-Agent': 'LiteratureTracker/1.0 (mailto:user@example.com)'
}
if S2_API_KEY:
    S2_HEADERS['x-api-key'] = S2_API_KEY

# 与 crawler.py 相同的期刊配置（直接复制，不依赖 crawler.py）
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

# ── 工具函数 ───────────────────────────────────────────────────────────────────

def load_papers():
    """加载已有论文（与 crawler.py 相同逻辑）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, '..', 'data', 'papers.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_papers(papers):
    """保存论文（与 crawler.py 相同逻辑，直接覆盖写入）"""
    os.makedirs('data', exist_ok=True)
    with open('data/papers.json', 'w', encoding='utf-8') as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)


def build_existing_dedup_keys(papers):
    """
    构建已有论文的去重 key 集合
    包含：DOI（小写）、title+第一作者 组合（兜底，处理 DOI 缺失情况）
    """
    keys = set()
    for p in papers:
        doi = (p.get('doi') or '').lower().strip()
        if doi:
            keys.add(doi)

        title = (p.get('title') or '').lower().strip()
        authors = p.get('authors') or []
        first_author = (authors[0] if authors else '').lower().strip()
        if title and first_author:
            keys.add(f"{title}||{first_author}")

    return keys


def get_category_for_journal(journal_name, journal_issn):
    """根据期刊名或 ISSN 查找对应的 category"""
    for category, journals in JOURNALS_CONFIG.items():
        for j in journals:
            if j['issn'] == journal_issn or j['name'].lower() == journal_name.lower():
                return category
    return 'unknown'


def normalize_journal_name(crossref_name):
    """将 Crossref 返回的期刊名称规范化为配置中的标准名称
    处理常见差异：大小写、The 前缀、副标题变体、HTML 实体等"""
    if not crossref_name:
        return crossref_name
    # 1. 精确匹配（大小写不敏感）
    name_lower = crossref_name.lower().strip()
    for journals in JOURNALS_CONFIG.values():
        for j in journals:
            if j['name'].lower() == name_lower:
                return j['name']
    # 2. 去掉 "The " 前缀后再匹配
    for prefix in ['the ', ]:
        if name_lower.startswith(prefix):
            stripped = name_lower[len(prefix):]
            for journals in JOURNALS_CONFIG.values():
                for j in journals:
                    if j['name'].lower() == stripped:
                        return j['name']
    # 3. 前缀匹配（处理带副标题的变体，如 "Journal of Comparative Policy Analysis: Research and Practice"）
    for journals in JOURNALS_CONFIG.values():
        for j in journals:
            key_lower = j['name'].lower()
            if name_lower.startswith(key_lower) and len(name_lower) > len(key_lower) and name_lower[len(key_lower)] in {':', ' '}:
                return j['name']
    # 4. 兜底：返回原值
    return crossref_name


# ── Crossref：按 ISSN 获取最新论文 ──────────────────────────────────────────

def _parse_crossref_date_parts(date_parts):
    """解析 Crossref 的 date-parts 格式为 YYYY-MM-DD"""
    if date_parts and date_parts[0]:
        year = date_parts[0][0] if len(date_parts[0]) > 0 else None
        month = date_parts[0][1] if len(date_parts[0]) > 1 else 1
        day = date_parts[0][2] if len(date_parts[0]) > 2 else 1
        if year:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return ''


def _parse_crossref_items(items, since_date):
    """解析 Crossref items 列表，提取论文信息，不做日期过滤"""
    results = []
    today = datetime.now().date()

    for item in items:
        doi = item.get('DOI', '').strip()
        if not doi:
            continue

        # 标题
        title_list = item.get('title', [])
        title = title_list[0] if title_list else ''
        if not title:
            continue

        # 清理 HTML 标签 + 过滤非学术文章（与 crawler.py 一致）
        title = clean_text(title)
        if is_non_academic_title(title):
            continue

        # 解析 online 日期
        online_parts = item.get('published-online', {}).get('date-parts', [[]])
        published_online = _parse_crossref_date_parts(online_parts)

        # 解析 print 日期
        print_parts = item.get('published-print', {}).get('date-parts', [[]])
        published_print = _parse_crossref_date_parts(print_parts)

        # 解析 Crossref created 日期（索引创建时间）
        crossref_created = ''
        created_str = item.get('created', {}).get('date-time', '')
        if created_str:
            try:
                created_dt = datetime.strptime(created_str[:10], '%Y-%m-%d')
                crossref_created = created_dt.strftime('%Y-%m-%d')
            except ValueError:
                pass

        # 确定 published_date（优先 online，其次 print，兜底 created）
        published_date = ''
        for d in [published_online, published_print]:
            if d:
                try:
                    if datetime.strptime(d, '%Y-%m-%d').date() > today:
                        continue
                    published_date = d
                    break
                except ValueError:
                    continue
        if not published_date and crossref_created:
            published_date = crossref_created

        # 作者
        authors = []
        has_mainland = False
        has_any_affiliation_data = False
        for author in item.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            full = f"{given} {family}".strip()
            if full:
                authors.append(full)
            # 提取 affiliation 信息
            for aff in author.get('affiliation', []):
                aff_name = aff.get('name', '')
                if aff_name:
                    has_any_affiliation_data = True
                    if is_mainland_china_text(aff_name):
                        has_mainland = True

        # 期刊名
        container = item.get('container-title', [])
        journal_name = container[0] if container else ''

        # URL
        url = item.get('URL', '')
        if not url and doi:
            url = f"https://doi.org/{doi}"

        results.append({
            'doi': doi,
            'title': title,
            'published_date': published_date,
            'published_online': published_online,
            'published_print': published_print,
            'crossref_created': crossref_created,
            'journal_name': journal_name,
            'authors': authors[:10],
            'url': url,
            'has_mainland_author': True if has_mainland else (False if has_any_affiliation_data else None)
        })

    return results


def _filter_by_any_date(results, since_date):
    """
    二次过滤：只要 published_online / published_print / crossref_created
    任一日期 >= since_date 就保留
    """
    filtered = []
    for r in results:
        dates = [r.get('published_online', ''), r.get('published_print', ''), r.get('crossref_created', '')]
        if any(d and d >= since_date for d in dates):
            filtered.append(r)
    return filtered


def fetch_crossref_by_issn(issn, from_date=None, rows=100):
    """
    通过 Crossref API 按 ISSN 获取最新论文（双查询策略）
    1. 主查询：sort=created + from-created-date（捕获 early view）
    2. 兜底查询：sort=published + from-pub-date（兼容不支持 created 的期刊）
    返回列表：[{"doi", "title", "published_date", "journal_name", "authors", "url"}]
    """
    if from_date:
        since_date = from_date
    else:
        since_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    url = f"https://api.crossref.org/journals/{issn}/works"
    all_results = []

    # ===== 主查询：按 created 排序 + from-created-date 过滤 =====
    try:
        params_main = {
            'sort': 'created',
            'order': 'desc',
            'rows': rows,
            'filter': f'from-created-date:{since_date}',
            'mailto': CROSSREF_EMAIL
        }
        resp = requests.get(url, headers=CROSSREF_HEADERS, params=params_main, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('message', {}).get('items', [])
            main_results = _parse_crossref_items(items, since_date)
            # 二次过滤：只要任一日期 >= since_date
            main_results = _filter_by_any_date(main_results, since_date)
            all_results.extend(main_results)
            print(f"    [Crossref-main] created 排序: 原始 {len(items)} 条, 过滤后 {len(main_results)} 条")
        else:
            print(f"    [Crossref-main] ISSN {issn} 请求失败: {resp.status_code}")
    except Exception as e:
        print(f"    [Crossref-main] ISSN {issn} 异常: {e}")

    # ===== 兜底查询：按 published 排序 + from-pub-date 过滤 =====
    # 如果主查询返回太少（< 20 条），用旧方式兜底，防止期刊不支持 created 排序
    if len(all_results) < 20:
        try:
            params_fallback = {
                'sort': 'published',
                'order': 'desc',
                'rows': rows,
                'filter': f'from-pub-date:{since_date}',
                'mailto': CROSSREF_EMAIL
            }
            resp = requests.get(url, headers=CROSSREF_HEADERS, params=params_fallback, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get('message', {}).get('items', [])
                fallback_results = _parse_crossref_items(items, since_date)
                # 去重：只保留主查询中没有的 DOI
                existing_dois = {r['doi'].lower() for r in all_results}
                for r in fallback_results:
                    if r['doi'].lower() not in existing_dois:
                        all_results.append(r)
                        existing_dois.add(r['doi'].lower())
                print(f"    [Crossref-fb] published 排序: 原始 {len(items)} 条, 新增 {len(all_results) - len(main_results)} 条")
            else:
                print(f"    [Crossref-fb] ISSN {issn} 请求失败: {resp.status_code}")
        except Exception as e:
            print(f"    [Crossref-fb] ISSN {issn} 异常: {e}")

    return all_results


# ── Semantic Scholar：批量补全摘要等信息 ─────────────────────────────────────

def fetch_s2_batch(doi_list):
    """
    通过 Semantic Scholar 批量 API 补全论文信息
    doi_list: list of DOI strings
    返回 dict: {doi_lower: {abstract, citationCount, authors, ...}}
    """
    if not doi_list:
        return {}

    # 构造请求 ID 列表
    ids = [f"DOI:{d}" for d in doi_list]

    url = "https://api.semanticscholar.org/graph/v1/paper/batch"
    params = {
        'fields': 'title,abstract,citationCount,authors,year,externalIds'
    }
    headers = dict(S2_HEADERS)
    headers['Content-Type'] = 'application/json'

    try:
        resp = requests.post(
            url,
            headers=headers,
            params=params,
            json={'ids': ids},
            timeout=60
        )
        if resp.status_code != 200:
            print(f"    [S2] 批量请求失败: {resp.status_code}")
            return {}
        data = resp.json()
        results = {}

        for paper in data.get('data', []):
            # 通过 externalIds 找到 DOI
            ext = paper.get('externalIds', {}) or {}
            doi = (ext.get('DOI') or '').lower()
            # 提取 affiliation 信息判断是否涉及大陆作者
            s2_has_mainland = False
            s2_has_any_affiliation = False
            s2_authors = paper.get('authors') or []
            for a in s2_authors:
                affs = a.get('affiliations', []) if isinstance(a, dict) else []
                if affs:
                    s2_has_any_affiliation = True
                for aff in affs:
                    if is_mainland_china_text(str(aff)):
                        s2_has_mainland = True
                        break
            s2_mainland_status = True if s2_has_mainland else (False if s2_has_any_affiliation else None)
            
            if not doi and paper.get('title'):
                # 有些返回没有 externalIds，尝试从请求ID映射
                pass
            if doi:
                results[doi] = {
                    'abstract': paper.get('abstract', '') or '',
                    'citationCount': paper.get('citationCount', 0) or 0,
                    'authors': [a.get('name', '') for a in (paper.get('authors') or [])],
                    'year': paper.get('year') or None,
                    'has_mainland_author': s2_mainland_status
                }

        return results

    except Exception as e:
        print(f"    [S2] 批量请求异常: {e}")
        return {}


def chunk_list(lst, n):
    """将列表按 n 个一组分块"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def supplement_with_s2(doi_list):
    """
    分批调用 S2 批量 API，补全摘要等信息
    S2 批量接口每次最多 500 个 ID
    """
    result = {}
    total = len(doi_list)
    print(f"    [S2] 共 {total} 个 DOI，分批查询...")

    for i, batch in enumerate(chunk_list(doi_list, 500)):
        print(f"    [S2] 批次 {i+1}/{(total + 499) // 500} ({len(batch)} 个)...")
        batch_result = fetch_s2_batch(batch)
        result.update(batch_result)
        # 速率限制：未注册 100次/5分钟 ≈ 每次请求后 sleep 3秒
        if i < (total - 1) // 500:
            time.sleep(3)

    found = sum(1 for d in doi_list if d.lower() in result)
    print(f"    [S2] 补全完成: {found}/{total} 找到摘要")
    return result


# ── 主流程 ───────────────────────────────────────────────────────────────────

def run_supplement(days=30, rows_per_journal=50):
    """
    主函数：
    1. 加载已有论文，提取已有 DOI 集合
    2. 遍历所有 ISSN，用 Crossref 查最近 days 天的论文
    3. 过滤掉已有 DOI
    4. 用 S2 批量补全摘要
    5. 合并写入 papers.json
    """
    print("=" * 60)
    print("Crossref + Semantic Scholar 补爬脚本")
    print("=" * 60)

    papers = load_papers()
    existing_keys = build_existing_dedup_keys(papers)
    print(f"已有论文: {len(papers)} 篇")
    print(f"去重 key 数: {len(existing_keys)}")
    print()

    # 动态窗口：基于已有数据最新日期计算 from_date
    if papers:
        today = datetime.now().date()
        valid_dates = [
            p.get('published_date', '1970-01-01')
            for p in papers
            if p.get('published_date')
        ]
        valid_dates = [
            d for d in valid_dates
            if datetime.strptime(d, '%Y-%m-%d').date() <= today
        ]
        if valid_dates:
            latest_date = max(valid_dates)
            # 取 min(now-days, latest_date-3天)，确保 --days 参数生效
            # daily: now-2天 比 latest_date-3天 更晚 → 取 latest_date-3天（增量补爬）
            # weekly/initial: now-14/120天 更早 → 取 now-days（按指定范围爬取）
            days_based_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            buffer_based_from = (
                datetime.strptime(latest_date, '%Y-%m-%d') - timedelta(days=3)
            ).strftime('%Y-%m-%d')
            dynamic_from = min(days_based_from, buffer_based_from)
        else:
            dynamic_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    else:
        dynamic_from = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    print(f"Crossref 查询起始日期: {dynamic_from}（动态窗口）")
    print()

    # 收集所有需要补爬的 (journal_info, category)
    all_journals = (
        [(j, 'PA') for j in JOURNALS_CONFIG['public_administration']] +
        [(j, 'PP') for j in JOURNALS_CONFIG['public_policy']] +
        [(j, 'POL') for j in JOURNALS_CONFIG['political_science']] +
        [(j, 'ECON') for j in JOURNALS_CONFIG['economics']] +
        [(j, 'OTHER') for j in JOURNALS_CONFIG['other']] +
        [(j, 'CHINA') for j in JOURNALS_CONFIG['china_studies']]
    )

    # 第一步：Crossref 发现新 DOI
    new_papers = []  # 待新增的论文（尚未补全 S2）
    crossref_results = {}  # doi -> crossref paper info

    print("【第一步】Crossref 按 ISSN 发现新论文...")
    for journal, category in all_journals:
        issn = journal.get('issn', '')
        name = journal.get('name', '')
        if not issn:
            continue

        print(f"  [{category}] {name} (ISSN: {issn})")
        works = fetch_crossref_by_issn(issn, from_date=dynamic_from, rows=rows_per_journal)

        added = 0
        for work in works:
            doi = work['doi'].lower()
            title = work.get('title', '').lower().strip()
            authors = work.get('authors') or []
            first_author = (authors[0] if authors else '').lower().strip()

            # 按 DOI 去重
            if doi in existing_keys:
                continue
            # 按 title+first_author 去重（兜底，处理 DOI 缺失或 OpenAlex 无 DOI 的情况）
            if title and first_author and f"{title}||{first_author}" in existing_keys:
                continue
            # 避免同一 DOI 被多个期刊重复添加（Crossref 数据有时 ISSN 映射不准）
            if doi and doi in crossref_results:
                continue

            work['category'] = category
            new_papers.append(work)
            crossref_results[doi] = work
            # 把新论文的 key 也加入去重集合，防止同批次内重复
            if doi:
                existing_keys.add(doi)
            if title and first_author:
                existing_keys.add(f"{title}||{first_author}")
            added += 1

        print(f"    发现 {len(works)} 篇，新增 {added} 篇")
        time.sleep(0.5)  # Crossref polite pool: 无需长时间等待

    print(f"\nCrossref 共发现新论文: {len(new_papers)} 篇")
    print()

    if not new_papers:
        print("没有发现需要补爬的新论文，退出。")
        return 0, {}

    # 第二步：S2 批量补全摘要
    print("【第二步】Semantic Scholar 批量补全摘要...")
    doi_list = [p['doi'].lower() for p in new_papers]
    s2_data = supplement_with_s2(doi_list)
    print()

    # 第三步：全局去重后合并数据，写入 papers.json
    print("【第三步】全局去重并合并数据...")

    # 先对已有数据进行全局去重（清理历史遗留重复）
    before_dedup = len(papers)
    seen_keys = set()
    deduped = []
    for p in papers:
        doi = (p.get('doi') or '').lower().strip()
        title = (p.get('title') or '').lower().strip()
        authors = p.get('authors') or []
        first_author = (authors[0] if authors else '').lower().strip()

        key = None
        if doi:
            key = doi
        elif title and first_author:
            key = f"{title}||{first_author}"

        if key:
            if key in seen_keys:
                continue
            seen_keys.add(key)

        deduped.append(p)

    if len(deduped) < before_dedup:
        print(f"  历史去重: 移除 {before_dedup - len(deduped)} 条重复记录")

    papers = deduped
    added_count = 0
    no_abstract_count = 0

    for paper in new_papers:
        doi = paper['doi'].lower()
        s2 = s2_data.get(doi, {})

        # 规范化期刊名称（Crossref 原始名称可能带 The 前缀、大小写差异）
        raw_journal_name = paper.get('journal_name', '')
        normalized_name = normalize_journal_name(raw_journal_name)

        # 构造与 crawler.py 输出格式兼容的论文记录
        new_record = {
            'openalex_id': f'crossref:{doi}',
            'title': paper.get('title', ''),
            'abstract': s2.get('abstract', '') or '',
            'journal_name': normalized_name,
            'published_date': paper.get('published_date', ''),
            'published_online': paper.get('published_online', ''),
            'published_print': paper.get('published_print', ''),
            'url': paper.get('url', ''),
            'doi': paper['doi'],
            'keywords': [],
            'authors': s2.get('authors', []) or paper.get('authors', [])[:10],
            'category': paper.get('category', 'unknown'),
            'citation_count': s2.get('citationCount', 0) or 0,
            'supplement_source': 'crossref+s2',
            'has_mainland_author': s2.get('has_mainland_author') if s2.get('has_mainland_author') is not None else paper.get('has_mainland_author')
        }

        # 如果 S2 提供了年份但没有 published_date，补全一下
        if not new_record['published_date'] and s2.get('year'):
            new_record['published_date'] = f"{s2['year']}-01-01"

        if not new_record['abstract']:
            no_abstract_count += 1

        papers.append(new_record)
        added_count += 1

    save_papers(papers)

    print(f"合并完成: 新增 {added_count} 篇")
    print(f"  其中 {added_count - no_abstract_count} 篇有摘要")
    print(f"  其中 {no_abstract_count} 篇无摘要（S2 未覆盖）")
    print(f"总计: {len(papers)} 篇")
    print()

    # 按期刊统计
    journal_stats = {}
    for p in new_papers:
        name = p.get('journal_name', '未知期刊')
        journal_stats[name] = journal_stats.get(name, 0) + 1

    return added_count, journal_stats


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Crossref+S2 补爬脚本：发现 OpenAlex 漏爬的文献'
    )
    parser.add_argument(
        '--days', type=int, default=30,
        help='Crossref 查询最近多少天的论文（默认 30 天）'
    )
    parser.add_argument(
        '--rows', type=int, default=50,
        help='每个 ISSN 最多查询多少篇（默认 50 篇）'
    )

    args = parser.parse_args()

    run_supplement(days=args.days, rows_per_journal=args.rows)
